import var_int

class Packet:
    def __init__(self, idnum=None, data=None):
        self.data = data
        self.id = idnum
        if idnum or data:
            self.length = var_int.size(self.id) + len(data)

    def send(self, connection):
        message = var_int.write(self.length) + var_int.write(self.id) + \
            self.data
        connection.send(message)

    def recv(connection):
        me = Packet()
        me.length = var_int.read(connection)
        me.id = var_int.read(connection)
        data_len = me.length - var_int.size(me.id)
        if data_len > 0:
            me.data = connection.recv(data_len)
        else:
            me.data = None
        return me

    def __repr__(self):
        return '({}, {}, {})'.format(self.length, self.id, self.data)

def write_string(s):
    return var_int.write(len(s)) + bytes(s, 'utf-8')
