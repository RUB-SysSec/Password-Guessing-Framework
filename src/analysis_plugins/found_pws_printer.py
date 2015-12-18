'''
The following parameters are passed to the plugin:

'pws_multi'                 #   Dict: {'password/hash':{'occ':0, 'lookups':0}} 
                                  -->  password/hash is the key, 'occ' the occurence counter and 'lookups' a coutner for how often the pw/hash has been looked up during the guessing process
'pw_counter'                #    Int:  Counter for the overall amount of passwords/hashes in the leak
'pws_unique_counter'        #    Int:  Counter for the unique occurences in the leak
'guesses'                   #    Int:  Amount of guesses made by the guesser
'cracked_counter'           #    Int:  Amount of cracked passwords/hashes
'cracked_pws'               #   Dict:  {'password/hash':[guess-no. which cracked the pw]}
                                  -->  NOTE that for hashes, the guess-no. is always 0, as no guessing-no. can eb determinded from the JtR '.pot' file
'output_file'               # String:  Path of the file to write the analysis results into

Write your code in the try/ecept block to get error messages during the execution.
Also, no method declarations etc. are needed.
Name your script with a leading '_' to make the analysis module skip it during executing the plugins. E.g, 'myfile.py' will be executed, '_myfile.py' won't.
'''

import sys
import os
sys.path.insert(1, os.path.abspath('./'))
# import the ConfigHelper to be able to read values from the run.ini
from pgf.initiation.confighelper import ConfigHelper

#   [Do the necessary imports here...]



try:

    f = open(output_file.replace('.txt', '_found.txt'), 'w')

    for i in cracked_pws:
        f.write(i + '\n')

    print "The analysis plugin <%s> has been executed successfully.\n" % self_name
except Exception, e:
    print "An error occured in the analysis plugin '%s': %s\n" % (self_name, str(e))
