"""Quick support script to input an Excel file and then dump out all of the worksheet data as separate tab delimited files
"""

import sys, os;
import openpyxl;	# Open source library for reading Excel files in Python. Install with "python -m pip install openpyxl"
import csv;


def extractExcelSheets(inFilename):
	# Open the Excel workbook
	wb = openpyxl.load_workbook(inFilename)
	generatedFileList = list();
	for sheetName in wb.get_sheet_names():
		# Pull out one worksheet at a time
		ws = wb.get_sheet_by_name(sheetName);

		# Create a separate output file, name based on input file and worksheet name, to dump contents as CSV
		outFilename = os.path.splitext(inFilename)[0] +"."+ sheetName +".tsv";
		fileout = open(outFilename,"w");
		writer = csv.writer(fileout, dialect=csv.excel_tab);

		# Iterate through worksheet data values and output to TSV file
		for row in ws.values:
			#print row
			row = list(row);	# Convert to a modifiable list
			for i, value in enumerate(row):
				if isinstance(value, unicode):	# Clean up string values by replacing non-ascii characters (e.g., \xa0 = non-breaking space)
					row[i] = value.replace(u'\xa0', u' ');
			writer.writerow(row);

		fileout.close();
		generatedFileList.append(outFilename);
	return generatedFileList;

def main(argv):
	inFilename = argv[1];
	generatedFileList = extractExcelSheets(inFilename);
	for item in generatedFileList:
		print item;

if __name__ == "__main__":
	main(sys.argv);