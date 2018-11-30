#!/srv/anaconda3/bin/python3.7

import server
import subprocess as sp
import sys

if __name__ == '__main__':
    list_popen = []
    # for file_ in sys.argv[1:]:
    for file_ in ('file1', 'file2', 'file4'):
        list_popen.append(sp.Popen(['./EngineA.py', file_], stdout=sp.PIPE))
    for p in list_popen:
        # print(p.stdout.read())
        print('- {}'.format(p.communicate()[0]))
        # p.wait()
    # p = sp.Popen(['./EngineA.py', '123'], stdout=sp.PIPE)
    # print(p.stdout.read())

    # s = server.Server()
    # s.start()
