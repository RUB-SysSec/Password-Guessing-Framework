'''
:author: Fabian Langer
:contact: fabian.langer@rub.de
:author: Robin Flume
:contact: robin.flume@rub.de
'''

from pgf.exceptions.abstract_method import abstract_method

class InputParser(object):
    ''' Abstract class used for different kinds of input files.
    '''

    def __init__(self):
        ''' Constructor.
        '''
        abstract_method(self)

    def get_filetype(self):
        ''' Return the input type indicator to run the according analysis module and the execution module correctly.
        '''
        abstract_method(self)

    def parse_pw_file(self):
        '''Parses the Password File (filename) and returns the given data,
        such as plain text passwords or hashvalues, usernames, hash algorithms, salts and so on.
        '''
        abstract_method(self)
