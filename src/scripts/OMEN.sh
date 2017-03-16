#!/bin/bash

# ${1} received the training file, ${2} (if used) the max. amount of guesses

cd /opt/pgf/omen

# Training
rm -f CP.level EP.level IP.level LN.level createConfig
./createNG --iPwdList "${1}" > /dev/null 2>&1

# Execute Guesser
./enumNG --ignoreEP --maxattempts ${2} --pipeMode

# OMEN can benefit from an adaptive length scheduling algorithm incorporating live feedback,
# which is not available (due to the missing feedback channel) in stdout mode.
#
# Theoretically, best mode is:
# ./enumNG --simAtt /opt/pgf/leaks/rockyou_guess.txt --ignoreEP --maxattempts 100000000000 --optimizedLS