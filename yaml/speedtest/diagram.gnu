set terminal svg
set output 'diagram.svg'

set logscale
set xrange [100:2000]
set xlabel 'number of operations'
set yrange[1:120]
set ytics 10 nomirror
set ylabel 'readtime in s'
set y2range[1:650]
set y2tics 10 nomirror
set y2label 'filesize in MB'
set key left top

plot 'times.txt' lc 1 with lp title 'time no compr', \
'times_gz.txt' lc 2 with lp title 'time compr', \
'size.txt' lc 3 axes x1y2 with lp title 'filesize no compr', \
'size_gz.txt' lc 4 axes x1y2 with lp title 'filesize compr' 
