"""Usage:
main_sequence.exe  <data_folder> <default_pps> <brightest_pps> [options]

Arguments:
  model             tv model code
  default_pps       name of default preset picture setting
  brightest_pps     name of brightest preset picture setting

Options:
  -h --help
  --defabc      include abc on tests for default pps
  --hdr=pps     specify hdr preset picture setting for testing
  --hdrabc      include abc on tests for hdr pps
  --brabc       include abc on tests for brightest pps
  --qs=secs     tv has quickstart off by default, number of seconds to wake
"""
import sys
from docopt import docopt
from pathlib import Path
import sequence as ts
import command_sequence as cs
sys.path.append('..')
import logfuncs as lf


def get_test_order(docopt_args, ccf_pps_list):
    """Determine test order from option arguments."""
    test_order = ts.setup_tests(ccf_pps_list)
    abc_def_tests = {
        True: ['default', 'default_100', 'default_35', 'default_12', 'default_3'],
        False: ['default', 'default_low_backlight']
    }
    test_order += abc_def_tests[bool(docopt_args['--defabc'])]
    
    abc_br_tests = {
        True: ['brightest', 'brightest_100', 'brightest_35', 'brightest_12', 'brightest_3'],
        False: ['brightest', 'brightest_low_backlight']
    }
    test_order += abc_br_tests[bool(docopt_args['--brabc'])]
    
    if docopt_args['--hdr']:
        abc_hdr_tests = {
            True: ['hdr10', 'hdr10_100', 'hdr10_35', 'hdr10_12', 'hdr10_3'],
            False: ['hdr10', 'hdr10_low_backlight']
        }
        test_order += abc_hdr_tests[bool(docopt_args['--hdrabc'])]
    test_order += [
        'standby',
        'waketime',
        'standby_echo',
        'echo_waketime',
        'standby_google',
        'google_waketime',
    ]
    return test_order


def main():
    logger, docopt_args, data_folder = lf.start_script(__doc__, 'main-sequence.log')
    
    ccf_pps_list = ['default', 'brightest']
    if docopt_args['--hdr']:
        ccf_pps_list += ['hdr10_default']
    test_order = get_test_order(docopt_args, ccf_pps_list)
    logger.info(test_order)
    
    rename_pps = {
        'default': docopt_args['<default_pps>'],
        'brightest': docopt_args['<brightest_pps>'],
        'hdr10_default': docopt_args['--hdr'],
        'abc_default': docopt_args['<default_pps>']
    }
    qson = not docopt_args['--qs'] or float(docopt_args['--qs']) >= 10
    test_seq_df = ts.create_test_seq_df(test_order, rename_pps, qson)
    logger.info('\n' + test_seq_df.to_string())
    command_df = cs.create_command_df(test_seq_df)
    ts.save_sequences(test_seq_df, command_df, data_folder)


if __name__ == '__main__':
    main()
