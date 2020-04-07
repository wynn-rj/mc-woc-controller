def size(i):
    size = 1
    while((i & ~0x7f) != 0):
        size += 1
        i = i >> 7
    return size

def write(i):
    res = bytes()
    while((i & ~0x7F) != 0):
        res += bytes([(i & 0x7F) | 0x80])
        i = i >> 7
    res += bytes([i])
    return res

def read(connection):
    value = 0
    size = 0
    b = int.from_bytes(connection.recv(1), 'big')
    while(b & 0x80 == 0x80):
        value |= (b & 0x7f) << (size * 7)
        size += 1
        if (size > 5):
            raise Exception('Bad number')
        b = int.from_bytes(connection.recv(1), 'big')
    return value | ((b & 0x7f) << (size * 7))

class byte_helper:
    def __init__(self, bytelist):
        self.bytes = bytelist

    def recv(self, i):
        b = self.bytes[0:i]
        self.bytes = self.bytes[i:]
        return bytes(list(b))

def main():
    import sys
    print(read(byte_helper([0xd7, 0x7c])))
    print(read(byte_helper([0xd4, 0x7c])))

if __name__ == '__main__':
    main()
