#!/bin/bash

# ${1} received the training file, ${2} (if used) the max. amount of guesses

cd /opt/pgf/pcfg-google

# Training
rm -f grammar/* digits/* special/*
./process.py "${1}" > /dev/null 2>&1

# Execute Guesser
./pcfg_manager -dname0 "${1}" -dprob0 0.6