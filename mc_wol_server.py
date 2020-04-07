import socket
import json
import var_int
from packet_helper import Packet, write_string

class PacketError(OSError):
    """An error for a bad packet"""

def wait_for_wake(ip, port, version_string, quiet=False):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(1)

    if not quiet: print('Waiting for wake')
    conn, addr = s.accept()
    if not quiet: print('Connection from: {}'.format(addr))
    handshake = Packet.recv(conn)
    version = var_int.read(var_int.byte_helper(handshake.data))
    status_query = Packet.recv(conn)
    if status_query.id != 0 or status_query.data:
        raise PacketError('Bad packet: {}'.format(status_query))
    status_json = json.dumps({
        'version': {
            'name': version_string,
            'protocol': version
        },
        'players': {
            'max': 0,
            'online': 0
        },
        'description': {
            'text': 'Server is being booted now, please refresh in a minute'
        }
    }, separators=(',', ':'))
    status = Packet(0, write_string(status_json))
    status.send(conn)
    ping = Packet.recv(conn)
    if ping.id != 1:
        raise PacketError('Bad packet: {}'.format(ping))
    pong = Packet(1, ping.data)
    pong.send(conn)
    conn.close()

def main():
    while True:
        try:
            wait_for_wake('0.0.0.0', 25565, '1.14.4')
            print('Waking server')
            return
        except PacketError as ex:
            print(ex)

if __name__ == '__main__':
    main()
