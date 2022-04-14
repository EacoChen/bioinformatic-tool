
def read_last_line(filename, off=-50, _encode='utf-8'):
    with open(filename,'rb') as f:
        while True:
            f.seek(off,2)
            lines = f.readlines()
            if len(lines) >= 2:
                last_line = lines[-1]
                break
            off *= 2
    return last_line.decode(_encode)
