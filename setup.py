import sys
import distutils
from shutil import copyfile, copytree, move
from cx_Freeze import setup, Executable
import os
from zipfile import ZipFile
# import scipy

sys.path.append(r'.\Report')
# includefiles_list=[]
# scipy_path = os.path.dirname(scipy.__file__)
# includefiles_list.append(scipy_path)


def zipdir(directory, destination=None):
    # path to folder which needs to be zipped

    # calling function to get all file paths in the directory
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    print('zipping...')
    # writing files to a zipfile
    if not destination:
        destination = f'{directory}.zip'
    with ZipFile(destination, 'w') as zip:
        # writing each file one by one
        for file in file_paths:
            zip.write(file)
    print('All files zipped successfully!')


# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    # "packages": ['scipy'],
    "includes": ['pandas', 'docopt','matplotlib', 'matplotlib.backends.backend_tkagg', 'seaborn', 'scipy.ndimage._ni_support',
                 'seaborn.cm', 'scipy', 'scipy.spatial.ckdtree', 'scipy.sparse.csgraph._validation'],
}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Console"

setup(  name = "TV Test Report",
        version = "0.1",
        description = 'Creates pdf report from test results',
        options = {"build_exe": build_exe_options},
        executables = [Executable(r"Report\report.py", base=base), Executable(r"TestSequence\tv_test_sequence.py", base=base)]
        )


# distutils.dir_util.copy_tree('build/exe.win-amd64-3.6', 'exe.win-amd64-3.6')
copyfile(r'TestSequence\test-details.csv', r'build\exe.win-amd64-3.6\test-details.csv')
copyfile(r'Report\coeffs.csv', r'build\exe.win-amd64-3.6\coeffs.csv')
copyfile(r'Report\intro-text.csv', r'build\exe.win-amd64-3.6\intro-text.csv')

src, dst = r'C:\Users\rhohe\PycharmProjects\cmdTestSequence\Report\APL', r'build\exe.win-amd64-3.6\APL'
if not os.path.isdir(dst):
    copytree(src, dst)
else:
    for file in os.listdir(src):
        copyfile(os.path.join(src, file), os.path.join(dst, file))

if os.path.isfile(r'build\exe.win-amd64-3.6\lib\scipy\spatial\cKDTree.cp36-win_amd64.pyd'):
    os.rename(r'build\exe.win-amd64-3.6\lib\scipy\spatial\cKDTree.cp36-win_amd64.pyd', r'build\exe.win-amd64-3.6\lib\scipy\spatial\ckdtree.cp36-win_amd64.pyd')

zipdir(r'build\exe.win-amd64-3.6', 'tv-test-scripts.zip')