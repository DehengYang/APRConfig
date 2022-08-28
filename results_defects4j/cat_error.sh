folder=results_defects4j

for file in `find $folder -type f -name error.log`
do 
	echo "$file"
	cat $file
done
