#!/usr/bin/env python
import sys

'''
:author: Robin Flume
:contact: robin.flume@rub.de
'''

def main():
    ''' This script provides a solution for John the Ripper to only process the desired amount of guesses
    by blocking the output if the amount reached.
    Needed is this as the cracking instance of JtR is processing the incoming candidates faster than
    the analysis module of the PGF.
    '''
    counter = 0
    while counter < int(sys.argv[1]):
        candidate = sys.stdin.readline()
        sys.stdout.write(candidate)               # pass candidate through
        counter += 1
    else:
        return

if __name__ == '__main__':
    main()
