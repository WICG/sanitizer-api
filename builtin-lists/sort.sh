#!/bin/sh
for list in {elements,attributes}-*-{known,baseline,default}.txt; do
  echo $list:
  OUT=$(mktemp)
  grep "^#" $list > $OUT
  grep -v "^#" $list | sort >> $OUT
  diff $list $OUT
  cp $OUT $list
done
