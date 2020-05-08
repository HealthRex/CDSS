
#MANUAL SETUP
sheet_path='/Users/jonc101/Downloads/shc/'
github_path='/Users/jonc101/Documents/github2/CDSS/'
#export PYTHONPATH='/Users/jonc101/Documents/github/CDSS/'

export PYTHONPATH=$github_path

flowsheet2011='flowsheet2011'

flowsheet2019='flowsheet2019'


upload_script_path='scripts/GoogleCloud/BQ/lpch/flowsheets/'

flowsheet2012py='upload_flowsheet2012.py'



#cut_inline_comma=awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", "", $i) } 1
#remove_quotes_from_numbers=sed -e 's/^\(".*"\),"\(.*\)","\(.*\)","\(.*\)","\(.*\)","\(.*\)",\(".*"\),"\(.*\)",\(".*"\)$/\1,\2,\3,\4,\5,\6,\7,\8,\9/g'
#remove_double_quotes_from_string=sed 's/\([^",]\)"\([^",]\)/\1""\2/g'
#remove_non_numeric_col_6=awk -F, '{ gsub(/[^0-9.-]/,"",$6) }1' OFS=','
#remove_non_numeric_col_8=awk -F, '{ gsub(/[^0-9.-]/,"",$8) }1' OFS=','



#cd $flowsheet_path$flowsheet2011
#split -l 2000000 lpch_flowsheet2011.csv flowsheet_

cd $sheet_path
#sed 's/\"//g' lpch_flowsheet2012.csv > lpch_flowsheet2012_v2.csv
split -l 250000 shc_order_proc_2020.csv sheet_



#cd $flowsheet_path$flowsheet2012
#split -l 2000000 lpch_flowsheet2012.csv flowsheet_
#rm flowsheet.csv
#python2 $github_path$upload_script_path$flowsheet2012py

#  HOW TO LOG / AND PRINT
# sh [SHELL_FILE.sh] 2>&1 | tee -a [NAME_OF_LOG_FILE.log]
