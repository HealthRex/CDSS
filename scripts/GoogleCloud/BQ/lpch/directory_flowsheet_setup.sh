
#MANUAL SETUP
flowsheet_path='/Users/jonc101/Documents/lpch_auto/flowsheets/'
github_path='/Users/jonc101/Documents/github/CDSS/'
#export PYTHONPATH='/Users/jonc101/Documents/github/CDSS/'

export PYTHONPATH=$github_path

flowsheet2011='flowsheet2011'
flowsheet2012='flowsheet2012'
flowsheet2013='flowsheet2013'
flowsheet2014='flowsheet2014'
flowsheet2015='flowsheet2015'
flowsheet2016='flowsheet2016'
flowsheet2017='flowsheet2017'
flowsheet2018='flowsheet2018'
flowsheet2019='flowsheet2019'


upload_script_path='scripts/GoogleCloud/BQ/lpch/flowsheets/'

flowsheet2012py='upload_flowsheet2012.py'
flowsheet2013py='upload_flowsheet2013.py'
flowsheet2014py='upload_flowsheet2014.py'
flowsheet2015py='upload_flowsheet2015.py'
flowsheet2016py='upload_flowsheet2016.py'
flowsheet2017py='auto_flowsheet_2017.py'
flowsheet2018py='upload_flowsheet2018.py'
flowsheet2019py='upload_flowsheet2019.py'


#cut_inline_comma=awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1
#remove_quotes_from_numbers=sed -e 's/^\(".*"\),"\(.*\)","\(.*\)","\(.*\)","\(.*\)","\(.*\)",\(".*"\),"\(.*\)",\(".*"\)$/\1,\2,\3,\4,\5,\6,\7,\8,\9/g'
#remove_double_quotes_from_string=sed 's/\([^",]\)"\([^",]\)/\1""\2/g'
#remove_non_numeric_col_6=awk -F, '{ gsub(/[^0-9.-]/,"",$6) }1' OFS=','
#remove_non_numeric_col_8=awk -F, '{ gsub(/[^0-9.-]/,"",$8) }1' OFS=','



#cd $flowsheet_path$flowsheet2011
#split -l 2000000 lpch_flowsheet2011.csv flowsheet_

cd $flowsheet_path$flowsheet2012
#sed 's/\"//g' lpch_flowsheet2012.csv > lpch_flowsheet2012_v2.csv
split -l 2000000 lpch_flowsheet2012_v2.csv flowsheet_



#cd $flowsheet_path$flowsheet2012
#awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1' lpch_flowsheet2012.csv  | sed -e 's/^\(".*"\),"\(.*\)","\(.*\)","\(.*\)","\(.*\)","\(.*\)",\(".*"\),"\(.*\)",\(".*"\)$/\1,\2,\3,\4,\5,\6,\7,\8,\9/g' | sed 's/\([^",]\)"\([^",]\)/\1""\2/g' | awk -F, '{ gsub(/[^0-9]/,"",$6) }1' OFS=','  > flowsheet.csv

#awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1' lpch_flowsheet2012.csv  | awk -F, '{ gsub(/[^0-9.-]/,"",$6) }1' OFS=',' | sed -e 's/^\(".*"\),"\(.*\)","\(.*\)","\(.*\)","\(.*\)","\(.*\)",\(".*"\),"\(.*\)",\(".*"\)$/\1,\2,\3,\4,\5,\6,\7,\8,\9/g' | sed 's/\([^",]\)"\([^",]\)/\1""\2/g' | awk -F, '{ gsub(/[^0-9.-]/,"",$8) }1' OFS=','  > flowsheet.csv
#split -l 2000000 lpch_flowsheet2012.csv flowsheet_
#rm flowsheet.csv
#python2 $github_path$upload_script_path$flowsheet2012py

#cd $flowsheet_path$flowsheet2013
#awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1' lpch_flowsheet2013.csv  | awk -F, '{ gsub(/[^0-9.-]/,"",$6) }1' OFS=',' | sed -e 's/^\(".*"\),"\(.*\)","\(.*\)","\(.*\)","\(.*\)","\(.*\)",\(".*"\),"\(.*\)",\(".*"\)$/\1,\2,\3,\4,\5,\6,\7,\8,\9/g' | sed 's/\([^",]\)"\([^",]\)/\1""\2/g' | awk -F, '{ gsub(/[^0-9.-]/,"",$8) }1' OFS=','  > flowsheet.csv
#split -l 2000000 lpch_flowsheet2013.csv flowsheet_
#rm flowsheet.csv
#python2 $github_path$upload_script_path$flowsheet2013py

#cd $flowsheet_path$flowsheet2014
#awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1' lpch_flowsheet2014.csv  | awk -F, '{ gsub(/[^0-9.-]/,"",$6) }1' OFS=',' | sed -e 's/^\(".*"\),"\(.*\)","\(.*\)","\(.*\)","\(.*\)","\(.*\)",\(".*"\),"\(.*\)",\(".*"\)$/\1,\2,\3,\4,\5,\6,\7,\8,\9/g' | sed 's/\([^",]\)"\([^",]\)/\1""\2/g' | awk -F, '{ gsub(/[^0-9.-]/,"",$8) }1' OFS=','  > flowsheet.csv
#split -l 2000000 lpch_flowsheet2014.csv flowsheet_


#rm flowsheet.csv
#python2 $github_path$upload_script_path$flowsheet2014py

#cd $flowsheet_path$flowsheet2015

#sed -e 's/^\(".*"\),"\(.*\)","\(.*\)","\(.*\)","\(.*\)","\(.*\)",\(".*"\),"\(.*\)",\(".*"\)$/\1,\2,\3,\4,\5,\6,\7,\8,\9/g'  lpch_flowsheet2015.csv | sed 's/\([^",]\)"\([^",]\)/\1""\2/g' | awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1'  | awk -F, '{ gsub(/[^0-9.-]/,"",$6) }1' OFS=',' | awk -F, '{ gsub(/[^0-9.-]/,"",$8) }1' OFS=','> flowsheet.csv
#awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1' $csv_name  | awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1'| awk -F, '{ gsub(/[^0-9.-]/,"",$14) }1' OFS=','|awk -F, '{ gsub(/[^0-9.-]/,"",$15) }1' OFS=','| awk -F, '{ gsub(/[^0-9.-]/,"",$23) }1' OFS=','| awk -F, '{ gsub(/[^0-9.-]/,"",$24) }1' OFS=','| sed 's/\([^",]\)"\([^",]\)/\1""\2/g'  > $csv_write_name
#basis# awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1' lpch_flowsheet2015.csv  | awk -F, '{ gsub(/[^0-9.-]/,"",$6) }1' OFS=',' | sed -e 's/^\(".*"\),"\(.*\)","\(.*\)","\(.*\)","\(.*\)","\(.*\)",\(".*"\),"\(.*\)",\(".*"\)$/\1,\2,\3,\4,\5,\6,\7,\8,\9/g' | sed 's/\([^",]\)"\([^",]\)/\1""\2/g' | awk -F, '{ gsub(/[^0-9.-]/,"",$8) }1' OFS=',' | sed 's/\([^",]\)"\([^",]\)/\1""\2/g' > flowsheet.csv
#awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1' lpch_flowsheet2015.csv  |sed -e 's/^\(".*"\),"\(.*\)","\(.*\)","\(.*\)","\(.*\)","\(.*\)",\(".*"\),"\(.*\)",\(".*"\)$/\1,\2,\3,\4,\5,\6,\7,\8,\9/g' | sed 's/\([^",]\)"\([^",]\)/\1""\2/g'|  awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1'| awk -F, '{ gsub(/[^0-9.-/]/,"",$6) }1' OFS=',' |  awk -F, '{ gsub(/[^0-9.-/]/,"",$8) }1' OFS=','|  sed 's/\([^",]\)"\([^",]\)/\1""\2/g' > flowsheet.csv
#split -l 2000000 lpch_flowsheet2015.csv flowsheet_
#rm flowsheet.csv
#python2 $github_path$upload_script_path$flowsheet2015py

#cd $flowsheet_path$flowsheet2019
#cat lpch_flowsheet2016.csv |  awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1' |awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1'| awk -F, '{ gsub(/[^0-9.-]/,"",$6) }1' OFS=',' | awk -F, '{ gsub(/[^0-9.-]/,"",$8) }1' OFS=','  | awk -F, '{ gsub(/"/,"",$5) }1' OFS=','| sed -e 's/^\(".*"\),"\(.*\)","\(.*\)","\(.*\)","\(.*\)","\(.*\)",\(".*"\),"\(.*\)",\(".*"\)$/\1,\2,\3,\4,\5,\6,\7,\8,\9/g'  | sed 's/\([^",]\)"\([^",]\)/\1""\2/g' | sed 's/\([^",]\)"\([^",]\)/\1""\2/g' > flowsheet.csv
#split -l 2000000  lpch_flowsheet2019.csv flowsheet_

#split -l 150000 flowsheet.csv flowsheet_
#rm flowsheet.csv
#python2 $github_path$upload_script_path$flowsheet2016py


#cd $flowsheet_path$flowsheet2017

#split -l 5000000 flowsheet.csv flowsheet_


#cd $flowsheet_path$flowsheet2018
#cat lpch_flowsheet2018.csv |  awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1' |awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1'| awk -F, '{ gsub(/[^0-9.-]/,"",$6) }1' OFS=',' | awk -F, '{ gsub(/[^0-9.-]/,"",$8) }1' OFS=','  | awk -F, '{ gsub(/"/,"",$5) }1' OFS=','| sed -e 's/^\(".*"\),"\(.*\)","\(.*\)","\(.*\)","\(.*\)","\(.*\)",\(".*"\),"\(.*\)",\(".*"\)$/\1,\2,\3,\4,\5,\6,\7,\8,\9/g'  | sed 's/\([^",]\)"\([^",]\)/\1""\2/g' | sed 's/\([^",]\)"\([^",]\)/#\1""\2/g' | awk -F, '{ gsub(/[^0-9.-]/,"",$6) }1' OFS=',' | awk -F, '{ gsub(/[^0-9.:-]/," ",$7) }1' OFS=','  | awk -F, '{ gsub(/[^0-9.-]/,"",$8) }1' OFS=','   > flowsheet.csv
#split -l 1000000 lpch_flowsheet2018.csv flowsheet_


#cd $flowsheet_path$flowsheet2019
#cat lpch_flowsheet2018.csv |  awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1' |awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1'| awk -F, '{ gsub(/[^0-9.-]/,"",$6) }1' OFS=',' | awk -F, '{ gsub(/[^0-9.-]/,"",$8) }1' OFS=','  | awk -F, '{ gsub(/"/,"",$5) }1' OFS=','| sed -e 's/^\(".*"\),"\(.*\)","\(.*\)","\(.*\)","\(.*\)","\(.*\)",\(".*"\),"\(.*\)",\(".*"\)$/\1,\2,\3,\4,\5,\6,\7,\8,\9/g'  | sed 's/\([^",]\)"\([^",]\)/\1""\2/g' | sed 's/\([^",]\)"\([^",]\)/\1""\2/g' > flowsheet.csv
#cat lpch_flowsheet2019.csv |  awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1' |awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1'| awk -F, '{ gsub(/[^0-9.-]/,"",$6) }1' OFS=',' | awk -F, '{ gsub(/[^0-9.-]/,"",$8) }1' OFS=','  | awk -F, '{ gsub(/"/,"",$5) }1' OFS=','| sed -e 's/^\(".*"\),"\(.*\)","\(.*\)","\(.*\)","\(.*\)","\(.*\)",\(".*"\),"\(.*\)",\(".*"\)$/\1,\2,\3,\4,\5,\6,\7,\8,\9/g'  | sed 's/\([^",]\)"\([^",]\)/\1""\2/g' | sed 's/\([^",]\)"\([^",]\)/#\1""\2/g' | awk '{if (NR!=1) {print}}' > flowsheet.csv


#  HOW TO LOG / AND PRINT
# sh [SHELL_FILE.sh] 2>&1 | tee -a [NAME_OF_LOG_FILE.log]
