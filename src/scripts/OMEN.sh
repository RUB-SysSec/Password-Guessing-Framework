#!/bin/bash

# ${1} received the training file, ${2} (if used) the max. amount of guesses

cd /opt/pgf/omen

# Set Smoothing Settings
printf "additive\n-delta_all 1\n-delta_LN 0\n-levelAdjust_all 250\n-levelAdjust_CP 2\n-levelAdjust_LN 1" > my_smoothing_settings

# Training
rm -f CP.level EP.level IP.level LN.level createConfig
./createNG --smoothing my_smoothing_settings --ngram 4 "${1}" > /dev/null 2>&1

# Execute Guesser
./enumNG --ignoreEP --maxattempts ${2} -p

# Best mode below, but it is only performing well in the --simulateAttack mode not in the -p (stdout) mode
# this can not be used with the Password Guessing Framework due to a bug in OMEN.
#./enumNG --simAtt /opt/pgf/leaks/rockyou_guess.txt --ignoreEP --maxattempts 100000000000 --optimizedLS