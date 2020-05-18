#!/bin/bash

# This script makes train/dev/test split based on data files in data_directory
# The data files should all be tab-delimited plaintext files (which may be gzip-compressed)
# Each data file should be a patient encounter with the encounter ID followed by .txt or .txt.gz in the filename
# The data_directory should also contain a columns.txt file specifying column names for all the fields in the data files
# The fields, patient_id and encounter_id, must be present

gzip_compressed=0

while getopts ":gh" opt; do
	case $opt in
		g) gzip_compressed=1
		   ;;
		h) 
		   echo "Usage: $0 [-g] [-h] <data_directory> <split_train> <split_dev> <split_test>"
		   echo "Options and arguments:"
		   echo "  -g             : Specify that the data files are gzip compressed"
		   echo "  -h             : Help"
		   echo "  data_directory : Directory containing the data we want to split into train/dev/test sets"
		   echo "  split_train    : Percentage that we want to put into train set (e.g. 70 means 70 percent)"
                   echo "  split_dev      : Percentage that we want to put into dev (validation) set"
                   echo "  split_test     : Percentage that we want to put into test set"
		   exit 1
		   ;;
		\?)
		   echo "Invalid option: -$OPTARG" >&2 # Fold output from stdout to stderr (file_descriptor=2)
		   exit 1
		   ;;
	esac
done

shift $((OPTIND-1))

if [ ! "$#" -eq 4 ]; then
	echo "Usage: $0 [-g] [-h] <data_directory> <split_train> <split_dev> <split_test>"
	exit 1
fi

data_directory="$1"
split_train="$2"
split_dev="$3"
split_test="$4"
columns_file="$data_directory/columns.txt"
extension=".txt"

if [ $gzip_compressed -eq 1 ]; then
	extension=".txt.gz"
fi


if [ ! -d "$data_directory" ]; then
	echo "The following directory does not exist: $data_directory"
	exit 1
fi

if [ ! -f "$columns_file" ]; then
        echo "The columns info file was not found: $columns_file"
        exit 1
fi

if [ $((split_train+split_dev+split_test)) -ne 100 ]; then
	echo "split_train, split_dev, and split_test must be whole numbers which add up to 100"
	exit 1
fi

if [ $split_train -le 0 -o $split_dev -le 0 -o $split_test -le 0 ]; then
	echo "split_train, split_dev, and split_test must be positive non-zero numbers"
	exit 1
fi

# Get the patient ID and encounter ID column numbers
patient_id_col=$(awk -F'\t' 'NR==1{for(i=1;i<=NF;i++) if($i=="patient_id") {print i;exit}}' "$columns_file")
encounter_id_col=$(awk -F'\t' 'NR==1{for(i=1;i<=NF;i++) if($i=="encounter_id") {print i;exit}}' "$columns_file")

if [ -z $patient_id_col ] || [ -z $encounter_id_col ]; then
	echo "The columns info file ($columns_file) must contain the fields: patient_id and encounter_id"
	exit 1
fi

# Progress monitor
progress_monitor() {
	iteration=$1
	total_iterations=$2
	if [ $total_iterations -lt 20 ]; then
		return  # No need to monitor progress if fewer than 20 iterations
	fi
	for ((n=0;n<=100;n+=10)); do
		if [ $iteration -eq $((total_iterations*n/100)) ]; then
			echo " - $n% done"
		fi
	done
}

# Make train, dev, test directories; if they already exist, move their contents to data_directory
echo "Creating train, test, dev folders..."
mkdir -p "$data_directory/train/"
mkdir -p "$data_directory/test/"
mkdir -p "$data_directory/dev/"
mv "$data_directory/train/"* "$data_directory/" 2> /dev/null
mv "$data_directory/test/"* "$data_directory/" 2> /dev/null
mv "$data_directory/dev/"* "$data_directory/" 2> /dev/null

# Make a temporary file
temp_file=$(mktemp)
trap "rm -f $temp_file" INT TERM HUP EXIT

# Extract patient IDs and encounter IDs from data files
echo "Retrieving patient IDs and encounter IDs..."
i=0
num_files=$(ls "$data_directory"|wc -l)
for f in "$data_directory"/*$extension; do
	fname=`basename ${f}`
	if [ ! "$fname" == "columns.txt" ]; then # If not the column names info file
		cmd="cat"
		if [ $gzip_compressed -eq 1 ]; then
			cmd="zcat"
		fi
		$cmd "$f"|head -1|cut -f$patient_id_col,$encounter_id_col >> $temp_file
	fi
        ((i++))
        progress_monitor $i $num_files
done

ids_directory="$data_directory/IDs"
mkdir -p "$ids_directory"

# Sort the IDs and store them in a file
echo "Sorting IDs and writing them to a file..."
sort $temp_file > "$ids_directory"/patient_ids_and_encounter_ids_sorted.txt

# Now put only unique patient IDs in a file
echo "Writing unique patient IDs to a file..."
cut -f1 "$ids_directory"/patient_ids_and_encounter_ids_sorted.txt|sort -u|shuf > "$ids_directory"/patient_ids_all.txt

# Calculate the split
echo "Calculating train, dev, test splits..."
num_patients=$(cat "$ids_directory"/patient_ids_all.txt|wc -l)
num_train=$((num_patients*split_train/100))
offset_test=$((num_train+1))
num_test=$((num_patients*split_test/100))
offset_dev=$((offset_test+num_test))

# Write patient IDs and encounter IDs to files
head -$num_train "$ids_directory"/patient_ids_all.txt > "$ids_directory"/patient_ids_train.txt
tail -n +$offset_test "$ids_directory"/patient_ids_all.txt|head -$num_test > "$ids_directory"/patient_ids_test.txt
tail -n +$offset_dev "$ids_directory"/patient_ids_all.txt > "$ids_directory"/patient_ids_dev.txt
grep -F -f "$ids_directory"/patient_ids_train.txt "$ids_directory"/patient_ids_and_encounter_ids_sorted.txt|cut -f2 > "$ids_directory"/encounter_ids_train.txt
grep -F -f "$ids_directory"/patient_ids_dev.txt "$ids_directory"/patient_ids_and_encounter_ids_sorted.txt|cut -f2 > "$ids_directory"/encounter_ids_dev.txt
grep -F -f "$ids_directory"/patient_ids_test.txt "$ids_directory"/patient_ids_and_encounter_ids_sorted.txt|cut -f2 > "$ids_directory"/encounter_ids_test.txt

echo "Splitting the dataset..."

while read line; do
  mv "$data_directory"/${line}${extension} "$data_directory/train/"
done < "$ids_directory"/encounter_ids_train.txt

echo "- Finished training set split"

while read line; do
  mv "$data_directory"/${line}${extension} "$data_directory/dev/"
done < "$ids_directory"/encounter_ids_dev.txt

echo "- Finished dev (validation) set split"

while read line; do
  mv "$data_directory"/${line}${extension} "$data_directory/test/"
done < "$ids_directory"/encounter_ids_test.txt

echo "- Finished test set split"
