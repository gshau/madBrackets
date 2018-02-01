#!/bin/bash
# Pull data from html-unlabeled table on kenpom's website

if [ "$#" -ne 2 ]; then
  echo "Wrong number of arguments.  Required: "
  echo "$0 filename year"
  exit -1
fi

file=$1
year=$2
curl -o $file.html https://kenpom.com/index.php?y=$year


sed -n '/<tbody>/,/<\/tbody>/p' $file.html | sed -e 's/<td/\'$'\n<td/g'  | sed -e 's/<\/tr/\'$'\n<\/tr/g'  > $file.txt

rm -f $file.html


cat $file.txt | sed 's/<thead>/\
/g' > tmp.txt
mv -vf tmp.txt $file.txt

cat $file.txt | sed 's/<\/thead>//g' > tmp.txt
mv -vf tmp.txt $file.txt


nteam=`cat $file.txt | grep '</tr>' |wc -l`

echo $nteam

echo ' ' > $file.csv

cat $file.txt | sed 's/<.*>\(.*[A-Z].* .*[A-Z].*\)<\/.*>/\1/'|sed 's/<.*>\(.*[[:alpha:]]\)<\/.*>/\1/' | sed '/<span*>/,/<\/span>/p' | sed 's/<span.*>//g' | sed 's/<\/a>//g' | sed 's/<.*>\(.*[[:digit:]]\)<\/.*>/\1/' | tr '\n' ',' |  sed 's/<tbody>,//g' | sed 's/<\/tbody>//g' | sed 's/<\/tr>,/\
/g' | sed 's/<td*.>,//g' | sed 's/<td class="bold-bottom">,//g' | sed 's/<tr class="tourney">,//g' | sed 's/<thead>.*<\/thead>//g' | grep -v 'NCSOS' |grep -v 'Rank'  | sed 's/,[ \t]*/,/g' | sed 's/ ,/,/g' | sed 's/<td class="td-right">,//g'| sed 's/<td class="td-right bold-bottom">,//g' > $file.csv

sed -i '$ d' $file.csv

mv -vf $file.csv $file-$year.csv
# cat $file.csv > $file.txt

exit
