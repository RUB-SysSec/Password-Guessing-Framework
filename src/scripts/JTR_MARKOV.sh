#!/bin/bash

# ${1} received the training file, ${2} (if used) the max. amount of guesses

cd /opt/pgf/john-guess

# Training
rm -f stats
./calc_stat "${1}" stats > /dev/null 2>&1

# Determine Level
./genmkvpwd stats 0 12 > myLevel.txt
LEVEL=`perl -ne 'BEGIN { $trsh = shift } ($lvl, $pswd) = /lvl=([0-9]+).*\(([0-9]+)\)$/; print "$lvl" and exit if $pswd >= $trsh;' ${2} myLevel.txt`
rm -f myLevel.txt

# Execute Guesser
./john --markov:${LEVEL}:0:0:12 --stdout
