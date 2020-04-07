import sys
import os
from os import path
import argparse
from mc_wol_server import wait_for_wake

class StartException(Exception):
    pass

def get_mc_jar(folder, version):

    print('Multiple minecraft server jar files found, '
          'please specify a version')

def start_controller(folder, jar, version):
    properties = path.join(folder, 'server.properties')
    if not path.isfile(properties):


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', help='The folder of the minecraft server')
    parser.add_argument('--version', help='The version of minecraft to use')
    args = parser.parse_args()
    jar, version = get_mc_jar(args.folder, args.version)
    if not jar:
        sys.exit(1)
    try:
        start_controller(args.folder, jar, version)
    except StartException as ex:
        print('Controller failed to start: {}'.format(ex))

if __name__ == '__main__':
    main()
