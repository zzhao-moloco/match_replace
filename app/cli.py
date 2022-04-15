from argparse import ArgumentParser
from configparser import ConfigParser
import simplematch as sm
import os

def openFiles(paths):
    handlers = []
    for path in paths:
        handlers.append(openFileRecursive(path))
    return handlers
    

def openFileRecursive(path):
    matcher = sm.Matcher("*.go")
    for root, _, files in os.walk(path, topdown=False):
        print("🏁" + root)
        for filename in files:
            # open file and return the file handler
            if is_file_needed(matcher, filename, files):
                print(filename)
                # return handler

# 
def is_file_needed(matcher, fname, fnames):
    return matcher.test(fname)

            
def main():
    # parser = ArgumentParser(prog='cli')
    # parser.add_argument('name', help="The user's name.", default="name")
    # args = parser.parse_args()
    # print("Hello, %s!" % args.name)

    config = ConfigParser()
    config.read('cli.cfg')
    # paths
    root_path = config.get("path", "root_path")
    folders = config.get("path", 'folders').split(',')
    paths = list(map(lambda s: root_path + "/" + s, folders))
    # open for read write
    file_handlers = openFiles(paths)
    # load, transform, and write


if __name__ == '__main__':
    main()
