'''
The following parameters are passed to the plugin:

'label'                     # String:  Name/Label of the current job
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

    # Initiate ConfigHelper instance
    ch = ConfigHelper('./configfiles/run.ini')


    '''
    Samples:
    - Get a value (TYPE CASTED!) from the 'run.ini':    my_value = ch.get_option('DEFAULT', 'my_value')
    - Get all (unique) passwords from the leak:         for password in pws_multi.iterkeys(): [...]
    - Get the occurence counter for a password:         occurences = pws_multi[password]['occ']
    - Get all cracked passwords:                        for password in cracked_pws.iterkeys(): [...]
    '''

    #   [Do your calculations here...]






    # Append lines to the output-list
    output = list()
    output.append("\n\n")
    output.append("**** **** **** **** [TITLE OF THIS CALCULATION] **** **** **** ****\n")
    output.append("                     [APPEND THE RESULTS HERE]                     \n")

    # Print output to file and terminal/console
    with open(output_file, 'a') as f:
        for line in output:
            f.write(line)
            print line[:-1]
        f.write("\n")

    print "The analysis plugin <%s> has been executed successfully.\n" % self_name
except Exception, e:
    print "An error occured in the analysis plugin '%s': %s\n" % (self_name, str(e))
