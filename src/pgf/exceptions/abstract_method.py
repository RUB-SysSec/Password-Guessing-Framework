'''
:author: Fabian Langer
:contact: fabian.langer@rub.de
'''

import sys

def _function_id(obj, nFramesUp):
    ''' Create a string naming the function n frames up on the stack.
    '''
    fr = sys._getframe(nFramesUp+1)
    co = fr.f_code
    return '%s.%s' % (obj.__class__, co.co_name)

def abstract_method(obj=None):
    ''' Use this instead of 'pass' for the body of abstract methods.
    '''
    raise NotImplementedError('Unimplemented abstract method: %s' % _function_id(obj, 1))
