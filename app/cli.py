from argparse import ArgumentParser
from configparser import ConfigParser
import simplematch as sm
import os

# open_files returns the rw file handlers of all files
def open_files(paths, mode):
    fds = []
    for path in paths:
        fds.extend(open_file_recursive(path,mode))
    return fds

match_src_file = sm.Matcher("*.go")

def open_file_recursive(path, mode):
    for root, _, files in os.walk(path, topdown=False):
        # print("🏁" + root)
        fds = []
        for filename in files:
            # open file and return the file handler
            if is_file_needed(match_src_file, root, filename, files):
                ffname = os.path.join(root, filename)
                # print("opening: " + ffname)
                # return handler
                f = open(ffname, mode)
                fds.append(f)
        return fds


# is_file_needed picks out files of interest based on the filename and it's location
def is_file_needed(matcher, root, fname, fnames):
    cond1 = matcher.test(fname)
    cond2 = "main.go" in fnames
    return cond1 and cond2

def make_folders(in_paths, out_paths):
    for i in range(len(in_paths)):
        for root, _, files in os.walk(in_paths[i], topdown=False):
            for fname in files:
                if is_file_needed(match_src_file, root, fname, files):
                    ffname = out_paths[i]+root.removeprefix(in_paths[i]) + "/" + fname
                    # print("making folders for: " + ffname)
                    os.makedirs(os.path.dirname(ffname), exist_ok=True)

            
def main():
    parser = ArgumentParser(prog='cli')
    parser.add_argument("-p", "--prod", help="Flag to run in production environment", action="store_true")
    args = parser.parse_args()
    env =  "prod" if args.prod else "test"

    config = ConfigParser()
    config.read('cli.cfg')
    # paths
    root_path = config.get(env, "root_path")
    print(root_path)
    folders = config.get(env, 'folders').split(',')
    paths = list(map(lambda s: os.path.join(root_path, s), folders))
    
    if env != "prod":
        # open for read write
        r_fds = open_files(paths, "r")
        # load, transform, and write
        out_folders = config.get(env, "out_folders").split(',')
        out_paths = list(map(lambda s: os.path.join(root_path, s), out_folders))
        # make the corresonding files in os
        make_folders(paths, out_paths)
        pass
    else:
        pass


if __name__ == '__main__':
    main()
