import pandas as pd


RENAME_DICT = {
    'tag': 'Test Number',
    'test_name': 'Test Name',
    'test_time': 'Test Duration (Seconds)',
    'video': 'Video Clip',
    'preset_picture': 'Preset Picture Setting',
    'abc': 'Automatic Brightness Control (ABC)',
    'lux': 'Illuminance Level (Lux)',
    'mdd': 'Motion Detection Dimming (MDD)',
    'qs': 'QuickStart',
    'sdr': 'IEC SDR',
    'clasp_hdr': 'CLASP HDR',
    'dots': 'Dots Pattern',
    'lum_sdr': 'Luminance Profile',
    'default_level': 'Default Level',
    'lowest_level': 'Lowest Level',
    'backlight': 'Backlight Setting',
    'oob': 'Default Out of Box Setting',
    'off': 'Off',
    'on': 'On',
}

STAB_MAX_ITER = 6

# todo: manual sequence custom message
def display_row_settings(row):
    """Create test condition/settings portion of test prompt."""
    non_setting_cols = ['special_commands', 'tag', 'test_name', 'test_time']
    display_row = row.drop(non_setting_cols).dropna().rename(RENAME_DICT).replace(RENAME_DICT)
    s = '-'*80
    s += '\\nThe conditions for the current test should be:\\n\\n'
    for setting, val in zip(display_row.index, display_row):
        if setting == 'Illuminance Level (Lux)':
            val = int(val)
        s += f'    {setting} - {val}'
        if setting == RENAME_DICT['mdd']:
            s += ' (if applicable)'
        s += '\\n'
    return s


def message_heading(current_row):
    """Create message heading portion of test prompt."""
    message = f'Test Name: {current_row["test_name"]}\\nTest Tag: {current_row["tag"]}\\n'
    if pd.notnull(current_row['test_time']):
        message += f'Test Time (seconds): {int(current_row["test_time"])}\\n\\n'
    return message


def message_instructions(current_row, previous_row=None, extra=None, countdown=True):
    """Create user instruction portion of test prompt."""
    setting_titles = {
        'mdd': 'motion detection dimming (MDD)',
        'abc': 'automatic brightness control (ABC)',
        'qs': 'quickstart (QS)',
        'preset_picture': 'preset picture',
    }
    test_clip = RENAME_DICT.get(current_row['video'], current_row['video'])
    message = '-' * 80
    message += '\\nInstructions:\\n\\n'
    if extra:
        message += extra
    if previous_row is not None:
        changes = current_row[(current_row != previous_row) & pd.notnull(current_row)]
        for col, change_val in changes.iteritems():
            if col in setting_titles.keys():
                message += f'* Change the {setting_titles[col]} setting to {change_val}'
                if col == 'mdd':
                    message += ' (if applicable)'
                message += '\\n'
            elif col == 'lux':
                message += f'* Adjust the illuminance level to {int(change_val)} lux\\n'
            elif col == 'video':
                message += f'* Change the video clip to {test_clip}\\n'
            elif col == 'backlight' and change_val == 'lowest_level':
                message += '* Lower the backlight setting to the lowest possible level and record this level.\\n'
    if countdown:
        message += f'* When ready begin the {test_clip} clip and press the OK button when the test clip content begins at the end of the countdown.\\n\\n'
    return message


def user_message(i, test_seq_df):
    """Create standard test prompt"""
    previous_row = test_seq_df.iloc[i - 1]
    current_row = test_seq_df.iloc[i]
    message = message_heading(current_row)
    message += message_instructions(current_row, previous_row)
    message += display_row_settings(current_row)
    return message


def waketime_message_start(row):
    """Create waketime test prompt."""
    message = message_heading(row)
    message += '-' * 80
    message += '\\nInstructions:\\n\\n'
    message += '* Now that the standby test is complete we are going to measure wake time.\\n'
    message += '* Press the OK button at the same time as you press the power button to turn on the television.\\n'
    message += '* A new message will appear asking you to press another button as soon as the TV has become responsive to input.'
    return message


# Scecond (finishing) test prompt for waketime tests
WT_MESSAGE2 = "As soon as the TV becomes responsive to input press the OK button."


def lum_profile_message(row):
    """Create lum profile test prompt."""
    message = message_heading(row)
    extra = '* Next we will capture the luminance profile of the TV.\\n'
    message += message_instructions(row, extra=extra)
    message += display_row_settings(row)
    return message


def stabilization_message(row):
    """Create stabilization test(s) prompt."""
    message = message_heading(row)
    extra = f'This test repeats until TV power output is stable or until {STAB_MAX_ITER} iterations is reached (minimum 2 iterations).\\n'
    message += message_instructions(row, extra=extra)
    message += display_row_settings(row)
    return message


def standby_message(row):
    """Create standby test prompt."""

    message = message_heading(row)
    message += '-' * 80
    message += '\\nInstructions:\\n\\n'
    message += f'* The next test will be a standby test.\\n'
    if 'echo' in row['test_name']:
        message += '* Connect the TV to the Amazon Echo\\n'
    if 'google' in row['test_name']:
        message += '* Connect the TV to the Google Home\\n'
    if 'qs' in row.index:
        message += f'* Ensure that QuckStart is set to {RENAME_DICT[row["qs"]]}'
        if row['qs']=='off':
            message+= ' (if applicable)'
        message += '.\\n'
    message += "* Power down the TV using the remote and press the OK button to begin test."
    return message


def screen_config_message(row):
    """Create screen_config test prompt."""
    message = message_heading(row)
    extra = '* Next we will configure the camera for the remaining tests.\\n'
    message += message_instructions(row, extra=extra, countdown=False)
    message += "Press OK when the clip is on the screen with no overlay\\n\\n"
    message += display_row_settings(row)
    return message


def create_command_df(test_seq_df):
    """Create dataframe that will eventually to be saved to to command-sequence.csv and fed to Labview."""
    
    # command_rows is a list of tuples containing data to be turned into dataframe (each tuple is a row)
    # command_rows always starts with these 6 1 column rows
    command_rows = [(i,) for i in ['#Config', 'Remote name', 'IR Delay (ms)', 'Macro File', '', '#Sequence']]
    # for each test (row) in test_seq_df create the appropriate rows in command_rows
    for i, row in test_seq_df.iterrows():
        command_rows.append(('tag', row['tag']))
        if 'waketime' in row['test_name']:
            command_rows.extend([
                ('user_command', waketime_message_start(row)),
                ('tag', row['tag'] + .1),
                ('user_command', WT_MESSAGE2)
            ])
        elif 'config' in row['test_name']:
            command_rows.append(('user_command', screen_config_message(row)))
        elif 'lum_profile' in row['test_name']:
            command_rows.append(('user_command', lum_profile_message(row)))
        elif 'standby' in row['test_name']:
            command_rows.append(('user_command', standby_message(row)))
        elif 'stabilization' in row['test_name']:
            command_rows.append(('user_stabilization', stabilization_message(row), 300, STAB_MAX_ITER))
        else:
            command_rows.append(('user_command', user_message(i, test_seq_df)))

        if not pd.isnull(row['test_time']):
            command_rows.append(('wait', row['test_time']))

        if not pd.isnull(row['special_commands']):
            for special_command in row['special_commands'].split(','):

                command_type, command = special_command.split(':')
                command_rows.append((command_type, command.strip()))

    command_df = pd.DataFrame(data=command_rows)
    command_df.columns = ['command_type', 'command', 'stab_wait', 'max_stab'][:command_df.shape[1]]
    return command_df