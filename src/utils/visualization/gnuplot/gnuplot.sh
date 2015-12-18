#!/bin/bash

gnuplot << EOF 
set style fill transparent solid 0.5
set terminal postscript enhanced color eps
set size 1.2,1.0
set output "$1"
set style line 80 lt 1 lw 3  # dashed
set style line 80 lt  rgb "#808080"
set style line 81 lt 0 lw 2  # dashed
set style line 81 lt rgb "#808080"  # grey
set grid back linestyle 81
set border 3 back linestyle 80 
set xtics nomirror
set ytics nomirror
set style line 1 linetype 1 lc rgb "#88A825" linewidth 4 pointtype 2
set style line 2 linetype 1 lc rgb "#35203B" linewidth 4 pointtype 2
set style line 3 linetype 1 lc rgb "#911146" linewidth 4 pointtype 2
set style line 4 linetype 1 lc rgb "#CF4A30" linewidth 4 pointtype 2
set style line 5 linetype 1 lc rgb "#ED8C2B" linewidth 4 pointtype 2
set style function linespoints
set key top left
set datafile separator ","
set title "$2"
set xlabel "# guesses"
set ylabel "cracked pws (in %)"
set xrange [1000:1000000000]
set yrange [1:80]
#set xtics ('1x 10^8' 100000000, '2x 10^8' 200000000, '3x 10^8' 300000000, '4x 10^8' 400000000, '5x 10^8' 500000000, \
# '6x 10^8' 600000000, '7x 10^8' 700000000, '8x 10^8' 800000000, '9x 10^8' 900000000, '1x 10^9' 1000000000) rotate by 45 right
set logscale x

plot \
     "jtr_markov_progress.csv" \
        using 1:(\$3) with line ls 1 \
        title "JtR Markov mode",\
     "omen_progress.csv" \
        using 1:(\$3) with line ls 2 \
        title "OMEN,4-gram",\
     "pcfg_progress.csv" \
        using 1:(\$3) with line ls 3 \
        title "PCFG-GITHUB",\
     "prince_progress.csv" \
        using 1:(\$3) with line ls 4 \
        title "PRINCE"
EOF