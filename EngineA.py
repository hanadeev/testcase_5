#!/home/hd/anaconda3/bin/python3

import sys
from engine import EngineA
import time

if __name__ == '__main__':
    # time.sleep(1)
    print(EngineA.scan(sys.argv[1:]))
