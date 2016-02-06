#!/bin/bash
# 
# Count files in subdir in dir $1.

mdir=$1

ls -1 $mdir | while read line
do
    echo -n $line " "
    ls -1 "$mdir/$line" | wc -l
done
