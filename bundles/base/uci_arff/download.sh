wget -np -r http://repository.seasr.org/Datasets/UCI/arff || exit 1
mv repository.seasr.org/Datasets/UCI/arff/*.arff . || exit 1
rm -rf repository.seasr.org/ || exit 1
for x in *.arff; do y=`echo $x | sed -e 's/.arff//'`; echo $y; mkdir $y; mv $x $y/data.arff; done || exit 1
for x in */data.arff; do echo $x; m=`dirname $x`/metadata; d=`grep Title $x | head -1 | cut -f 2 -d :`; echo "description: $d" > $m; echo "source: http://repository.seasr.org/Datasets/UCI/arff" >> $m; done || exit 1
