#!/bin/bash
dot -Tps ed.dot -oed.ps
convert           \
   -verbose       \
   -density 150   \
    ed.ps      \
   -quality 100   \
    ed.png
dot -Tps math.dot -omath.ps
convert           \
   -verbose       \
   -density 150   \
    math.ps      \
   -quality 100   \
    math.png
