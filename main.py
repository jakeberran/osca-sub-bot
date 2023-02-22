import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app.__main__ import main

if __name__ == '__main__':
  main()