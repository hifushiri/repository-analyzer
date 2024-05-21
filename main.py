import pydriller
import glob
import os
from binaryornot.check import is_binary
import sys


# error on incorrect/non-existant path
repo_path = sys.argv[1]
if (not os.path.isdir(repo_path)):
    sys.exit('ERROR[1]: Path provided is incorrect.')

# error on no .git dir inside
is_a_repo = False
for dir_name in os.listdir(repo_path):
    if (dir_name == '.git'):
        is_a_repo = True
        break
if (not is_a_repo):
    sys.exit('ERROR[2]: Directory provided is not a repository.')


# ---
# searching for binary files
# ---
binary_count = 0
binary_list = []
for root, d_names, f_names in os.walk(repo_path, topdown=True):
    for f in f_names:
        if (f[0] == '.'): break # skip for hidden files
        full_f = os.path.join(root, f)
        rel_path = full_f.replace(repo_path, '')
        if (rel_path[0] == '.' or
            rel_path[:2] == '/.'): break # skip for files in hidden dirs
                                         # (mainly for .git)
        if (os.path.isfile(full_f) and is_binary(full_f)):
                binary_list.append(full_f.replace(repo_path, ''))
                binary_count += 1


# ---
# searching for empty commits
# ---
empty_commit_count = 0
empty_commit_list = []
for commit in pydriller.Repository(repo_path).traverse_commits():
     if (not commit.msg.isprintable()):
        empty_commit_count += 1
        empty_commit_list.append(commit.hash)


# ---
# searching for .gitignore, Makefile and README.md
# ---
files_dict = {
    '.gitignore': False,
    'Makefile': False,
    'README.md': False
}
for filename in os.listdir(repo_path):
    file_basename = os.path.basename(filename)
    if file_basename in files_dict:
        files_dict[file_basename] = True


# ---
# output + cyclomatic complexity
# ---

# binary output
if (binary_count == 0):
    print('No binary files found.')
else:
    print('%d binary files found.' % (binary_count))
    print('The found binary files are:')
    for file in binary_list:
        binary_count -= 1
        if (binary_count == 0):
            print('└──', file)
            break
        print('├──', file)

# empty commits output
if (empty_commit_count == 0):
    print('\nNo empty commits found.\n')
else:
    print('\n%d empty commits found.\n' % (empty_commit_count))
    print('The found empty commits are:')
    for commit in empty_commit_list:
        empty_commit_count -= 1
        if (empty_commit_count == 0):
            print('└──', commit, end='\n\n')
            break
        print('├──', commit)

# .gitignore, Makefile and README.md output
for filename in files_dict:
    if (not files_dict[filename]):
        print ('%s file was not found!' % (filename))

# cyclomatic complexity
os.system("lizard %s" % (repo_path))
