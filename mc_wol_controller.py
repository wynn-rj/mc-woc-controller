import sys
import argparse
import subprocess
import re
import os
from os import path
from mcrcon import MCRcon
from mc_wol_server import wait_for_wake, PacketError

class StartException(Exception):
    """An exception for when the program failed to start"""

def get_mc_jar(folder, version):
    if version:
        jar = path.join(folder, 'minecraft_server.{}.jar'.format(version))
        if not path.isfile(jar):
            raise StartException('The given server version could not be found')
        return jar, version
    jar = None
    for file in os.listdir(folder):
        if not path.isfile(path.join(folder, file)):
            print('Skipping folder {}'.format(file))
            continue
        if file.startswith('minecraft_server') and file.endswith('.jar'):
            if jar:
                raise StartException('Multiple minecraft server jar files '
                                     'found, please specify a version')
            jar = path.join(folder, file)
            version = '.'.join(file.split('.')[1:-1])
    return jar, version

def read_server_properties(folder, fields):
    properties = path.join(folder, 'server.properties')
    if not path.isfile(properties):
        raise StartException('Server properties file does not exist')
    needed_props = { k : None for k in fields }
    with open(properties, 'r') as propertiesf:
        for line in propertiesf:
            values = line.split('=')
            if values[0] not in needed_props:
                continue
            if len(values) < 2:
                raise StartException('Expected value for server propety {}'
                                     .format(values[0]))
            needed_props[values[0]] = values[1].strip()
    for k, v in needed_props.items():
        if not v:
            raise StartException('No value found for property {}'.format(k))
    return needed_props

def sleep_till_wake(properties):
    while True:
        try:
            wait_for_wake(properties['server-ip'],
                          int(properties['server-port']), properties['version'])
            return
        except PacketError as ex:
            print(ex)
        except OSError as ex:
            print('Network Error: {}'.format(ex))
            sys.exit(1)

def start_server(args, jar):
    xms = '-Xms{}'.format(args.xms)
    xmx = '-Xmx{}'.format(args.xmx)
    jarfile = path.basename(jar)
    cwd = path.dirname(jar)
    server = subprocess.Popen(['java', xmx, xms, '-d64', '-jar', jarfile,
                              'nogui'], cwd=cwd)
    if server.poll():
        raise StartException('Server died while starting')
    return server

def sleep_till_empty(server, args, properties):
    while True:
        try:
            server.wait(int(args.timeout * 60))
            #Server must have been stopped
            return
        except subprocess.TimeoutExpired:
            with MCRcon('localhost', properties['rcon.password']) as mc:
                players = mc.command('/list')
                player_cnt = re.search(r'(\d+) of a max \d+', players)
                if player_cnt and player_cnt.group(1) and \
                        int(player_cnt.group(1)) == 0:
                    mc.command('/stop')
                    break
    server.wait()

def start_controller(args, jar):
    needed_properties = ['server-ip', 'server-port', 'rcon.password']
    properties = read_server_properties(args.folder, needed_properties)
    properties['version'] = args.version
    while True:
        print('Enter listening mode on {}:{}'.format(
            properties['server-ip'], int(properties['server-port'])))
        sleep_till_wake(properties)
        print('Waking server')
        sleep_till_empty(start_server(args, jar), args, properties)
        print('Sending server to sleep')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', help='The folder of the minecraft server')
    parser.add_argument('--version', help='The version of minecraft to use')
    parser.add_argument('--xms', help='Starting ram amount for server',
                        default='1G')
    parser.add_argument('--xmx', help='Max ram amount for server',
                        default='6G')
    parser.add_argument('--timeout', help='How long to wait to check if server'
                        ' is unused (in minutes)', default=60, type=float)
    args = parser.parse_args()
    try:
        jar, version = get_mc_jar(args.folder, args.version)
        args.version = version
        if not jar:
            print('No jar file found')
            sys.exit(1)
        start_controller(args, jar)
    except StartException as ex:
        print('Controller failed to start: {}'.format(ex))

if __name__ == '__main__':
    main()
