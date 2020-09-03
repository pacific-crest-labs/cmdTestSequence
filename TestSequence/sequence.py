"""Functions used in multiple test sequence scripts."""
import sys
import shutil
import pandas as pd
from pathlib import Path
sys.path.append(str(Path(sys.path[0]).parent))
from filefuncs import archive
from error_popups import permission_popup


def get_tests():
    """Construct dictionary of all possible tests from csv file."""
    path = Path(sys.path[0]).joinpath('test-details.csv')
    df = pd.read_csv(path).T
    df.columns = df.iloc[0]
    tests = df.to_dict()
    return tests


def setup_tests(ccf_pps_list, lum_profile=True):
    """Construct list of setup tests meant to go at beginning of a test sequence"""
    
    # include a ref_ccf test for each preset picture setting requiring a color correction factor
    test_order = [f"ref_ccf_{pps}" for pps in ccf_pps_list]
    # followed by the screen_config test
    test_order += ['screen_config']
    # followed by a camera_ccf test for each ccf pps
    test_order += [f"camera_ccf_{pps}" for pps in ccf_pps_list]
    if lum_profile:
        test_order += ['lum_profile']
    test_order += ['stabilization']
    return test_order

def create_test_seq_df(test_order, rename_pps, qson=False):
    """Construct the test sequence DataFrame"""
    tests = get_tests()
    # columns argument ensures order of columns. Columns not listed (if any) will still appear after columns listed here
    columns = ['test_name', 'test_time', 'video', 'preset_picture', 'abc', 'backlight', 'lux', 'mdd', 'qs',
               'special_commands']
    df = pd.DataFrame(columns=columns)
    for test in test_order:
        df = df.append(tests[test], ignore_index=True)
    
    prev_peak = False
    for idx, row in df.iterrows():
        # apply correct peak commands if any
        peak = pd.notna(row['special_commands']) and 'peak_test:' in row['special_commands']
        
        if prev_peak and not peak:
            if pd.isna(row['special_commands']):
                df.loc[idx, 'special_commands'] = 'peak_test:end'
            else:
                df.loc[idx, 'special_commands'] = 'peak_test:end,' + df.loc[idx, 'special_commands']
        
        prev_peak = peak
        
    if qson:
        df['qs'] = df['qs'].replace('off', 'on')
    df['preset_picture'] = df['preset_picture'].replace(rename_pps)
    df.index = range(1, len(df) + 1)
    df.index.name = 'tag'
    return df.reset_index()

        
@permission_popup
def save_sequences(test_seq_df, command_df, data_folder, repair=False):
    """Save test_seq_df and command_df to correct locations"""
    filenames = ['test-sequence.csv', 'command-sequence.csv']
    # save to current working directory
    test_seq_df.to_csv(filenames[0], index=False)
    command_df.to_csv(filenames[1], index=False, header=False)
    # also save within the data_folder
    for filename in filenames:
        if repair:
            # save to repair sub-folder if this is repair sequence
            repair_folder = Path(data_folder).joinpath('Repair')
            repair_folder.mkdir(exist_ok=True)
            save_path = repair_folder.joinpath(f"repair-{filename}")
        else:
            save_path = Path(data_folder).joinpath(filename)
            
        if save_path.exists():
            archive(save_path, date=True)
        shutil.copy(filename, save_path)