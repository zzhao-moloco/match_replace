from argparse import ArgumentParser
from asyncio import wrap_future
from configparser import ConfigParser
from pkg_resources import to_filename
from requests import patch
import simplematch as sm
import os

# open_files returns the rw file handlers of all files


def open_files(paths, mode):
    fds = []
    for path in paths:
        fds.extend(open_file_recursive(path, mode))
    return fds


match_src_file = sm.Matcher("*.go")


def open_file_recursive(path, mode):
    fds = []
    for root, _, files in os.walk(path, topdown=False):
        # print("🏁" + root)
        for filename in files:
            # open file and return the file handler
            if is_file_needed(match_src_file, root, filename, files):
                ffname = os.path.join(root, filename)
                # print("opening: " + ffname + " with mode "+ mode)
                # return handler
                f = open(ffname, mode)
                fds.append(f)
    return fds


# is_file_needed picks out files of interest based on the filename and it's location
def is_file_needed(matcher, root, fname, fnames):
    cond1 = matcher.test(fname)
    cond2 = "main.go" in fnames
    return cond1 and cond2


def make_write_files(in_paths, out_paths):
    for i in range(len(in_paths)):
        for root, _, files in os.walk(in_paths[i], topdown=False):
            for fname in files:
                if is_file_needed(match_src_file, root, fname, files):
                    ffname = out_paths[i] + \
                        root.removeprefix(in_paths[i]) + "/" + fname
                    # print("making folders for: " + ffname)
                    os.makedirs(os.path.dirname(ffname), exist_ok=True)
                    os.close(os.open(ffname, os.O_CREAT))


def update_import(lines):
    for i in range(len(lines)):
        l = lines[i]
        if "urfave/cli" in l:
            new_import = l[:l.find('"')+1] + \
                "github.com/urfave/cli/v2" + l[l.rfind('"'):]
            lines[i] = new_import
    return lines


def command_pointer(lines):
    matcher = sm.Matcher("*[]cli.Command{*")
    for i in range(len(lines)):
        l = lines[i]
        if matcher.test(l):
            insert = l.find("cli.")
            new_line = l[:insert]+"*"+l[insert:]
            lines[i] = new_line
    return lines

def seperate_alias(lines):
    flag_matcher = sm.Matcher("*cli.{flag_type}Flag{*")
    name_matcher = sm.Matcher('*Name:*"*, {alias}",*')
    name_with_var_matcher = sm.Matcher('*Name:* + ",*" + {var_alias},*')
    new_lines = []
    i = 0
    while i < len(lines):
        l = lines[i]
        if flag_matcher.test(l) and flag_matcher.match(l)["flag_type"]:
            # print(l)
            insert = l.find("cli.")
            new_line = l[:insert]+"&"+l[insert:]
            # print(new_line)
            new_lines.append(new_line)
            # fix the next line
            l = lines[i+1]
            if name_matcher.test(l):
                alias = name_matcher.match(l)["alias"]
                new_line = l.replace(", "+alias, "")
                # print(new_line)
                new_lines.append(new_line)
                # skip the next line check
                i += 1
                patch_line = l[:l.find("Name")] + 'Aliases: []string{"'+alias+'"},' + l[l.rfind(",")+1:]
                # print(patch_line)
                new_lines.append(patch_line)
            elif name_with_var_matcher.test(l):
                alias_var = name_with_var_matcher.match(l)["var_alias"]
                new_line = l.replace(' + "," + ' + alias_var, "")
                # print(new_line)
                new_lines.append(new_line)
                i += 1
                patch_line = l[:l.find("Name")] + 'Aliases: []string{'+alias_var+'},' + l[l.rfind(",")+1:]
                # print(patch_line)
                new_lines.append(patch_line)
            else:
                # these next lines to flags didn't get caught
                print("skipped:", end="")
                print(l)
        else:
            new_lines.append(l)
        i += 1
            
    return new_lines

transformers = [update_import,command_pointer, seperate_alias]


def transform(rfd, wfd, prod):
    lines = rfd.readlines()
    if prod:
        for f in transformers:
            lines = f(lines)
        rfd.seek(0, 0)
        rfd.writelines(lines)
        return
    for f in transformers:
        lines = f(lines)
    wfd.writelines(lines)


def transform_all(r_fds, w_fds):
    if not w_fds:
        # prod mode
        for i in range(len(r_fds)):
            transform(r_fds[i], None, True)
        return
    # test mode
    for i in range(len(r_fds)):
        # print(r_fds[i].name, w_fds[i].name)
        transform(r_fds[i], w_fds[i], False)


def main():
    parser = ArgumentParser(prog='cli')
    parser.add_argument(
        "-p", "--prod", help="Flag to run in production environment", action="store_true")
    args = parser.parse_args()
    env = "prod" if args.prod else "test"

    config = ConfigParser()
    config.read("cli.cfg")
    # paths
    root_path = config.get(env, "root_path")
    folders = config.get(env, "folders").split(',')
    paths = list(map(lambda s: os.path.join(root_path, s), folders))

    if env != "prod":
        # open for read
        r_fds = open_files(paths, "r")
        # make paths
        out_folders = config.get(env, "out_folders").split(',')
        out_paths = list(
            map(lambda s: os.path.join(root_path, s), out_folders))
        # make files from paths
        make_write_files(paths, out_paths)
        # open for write
        w_fds = open_files(out_paths, "w+")
        transform_all(r_fds, w_fds)
        close_all(r_fds)
        close_all(w_fds)
    else:
        # production
        fds = open_files(paths, "r+")
        transform_all(fds, None)
        close_all(fds)


def close_all(fds):
    for fd in fds:
        fd.close()


if __name__ == '__main__':
    main()
