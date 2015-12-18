''' Calculates the Alpha-Guesswork (Partial Guessing Entropie) and the Min. Entropie for a password leak.

Skript call: "(python) entropy_calcultator.py [inputfule] [percentage]"

where [inputfule] is the path to the password leak. It may contain either plaintext passwords (one pw per line)
including multiple passwords. The leak must not be cleaned, meaningly still containing multiple passwords.
[percentage] is a float value between 0.00 and 1.00 representing the percentage of passwords you want to crack.



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
'''

import sys
import os
sys.path.insert(1, os.path.abspath('./'))
import operator
import math
from math import fmod
from pgf.initiation.confighelper import ConfigHelper

try:
    # Initiate ConfigHelper instance
    ch = ConfigHelper('./configfiles/run.ini')

    alpha = ch.get_option('DEFAULT', 'alpha')           # value will already be return as float

    probabilities = dict()                              # create dict to store the probabilities of the passwords
    alpha_guesswork = 0.0                               # return value to be calculated
    u_alpha = 0.0                                       # helper
    lambda_u_alpha = 0.0                                # helper

    # calc probabilities for all pws in the leak
#     print "Calculating probabilities..."
    for pw, occ_lu in pws_multi.iteritems():
        probabilities[pw] = float(occ_lu['occ'])/float(pw_counter)

#     print "Sorting the passwords by their probabilities..."
    # sort the probabilities-dict by value (ascending) and return list-type object
    prob_sorted = sorted(probabilities.items(), key=operator.itemgetter(1))
    prob_sorted.reverse()
    prob_sorted.insert(0, ('0', 0.0))                   # insert empty tuple at index 0 so the indexes below are starting at 1 (paper conform)

    # calc u_alpha
    index = 0
    sum_ = 0.0
    alpha = float(alpha)

    # add prob. of pw at index [index] until u_alpha is >= alpha
#     print "Calculating the entropies..."
    while(lambda_u_alpha < alpha):
        index += 1
        lambda_u_alpha += prob_sorted[index][1]         # sum up the probabilities, starting at the highest
        sum_ += index * prob_sorted[index][1]           # sum up the probabilities, starting at the highest, each multplied with the current index
    u_alpha = index                                     # u_alpha is calculated as:  min{ j: (sum[1 to j] of p_i) >= alpha} --> u_alpha = index (j)

    # calc partial guessing entropy
    alpha_guesswork = ((1.0 - lambda_u_alpha) * u_alpha) + sum_

    # Makes the term constant for uniform distribution and calculates (G^~)-alpha in Bits
    alpha_guesswork_bits = math.log((((2.0*alpha_guesswork)/lambda_u_alpha)-1.0),2) + math.log((1.0/(2.0-lambda_u_alpha)),2)

    # calc min entropy
    min_entropy = -math.log(prob_sorted[1][1], 2)          # calc logarythm (base 2) of the most likely password

    output = list()
    output.append("\n\n")
    output.append("**** **** **** ****  RESULTS OF ENTROPY CALCULATIONS  **** **** **** ****\n")
    output.append("Alpha-Guesswork        (a = %4.2f)*: %12.0f    guesses\n" % (alpha, alpha_guesswork))
    output.append("Alpha-Guesswork (bits) (a = %4.2f)*: %15.3f bits\n" % (alpha, alpha_guesswork_bits))
    output.append("                     Min. Entropy*: %15.3f bits\n\n" % min_entropy)
    output.append("NOTE: If the password file contains salted hashes, the entropies cannot\n"\
                  "      be calculated and these values are irrelevant!\n"\
                  "      Unsalted hashes (which occure multiple times in the leak) result\n"\
                  "      in a correct entropy calculation though!\n\n")

    with open(output_file, 'a') as f:
        for line in output:
            f.write(line)
            print line[:-1]
        f.write("\n")

    print "The analysis plugin <%s> has been executed successfully.\n" % self_name
except Exception, e:
    print "An error occured in the analysis plugin '%s': %s\n" % (self_name, str(e))


