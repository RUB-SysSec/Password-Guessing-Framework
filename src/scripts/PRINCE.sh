#!/bin/bash

# ${1} received the training file, ${2} (if used) the max. amount of guesses

cd /opt/pgf/prince/src

# Execute Guesser
./pp64.bin --limit ${2} < "${1}"