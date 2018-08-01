= Dev Workshop =
Pivot Charts - Pivot Tables - Quick Data Manipulation and Visualization in Excel

== Learning Goals ==
- Long vs. Wide Data Formats
- Excel Table Controls (Freeze Panes, Auto-Filter)
- Excel VLOOKUP (code table reference)
- Excel Pivot Tables and Pivot Charts
- Raster vs. Vector Graphics

== Preconditions ==
- Microsoft Excel installed (or your preferred data manipulation environment)
- Review the Difference between "Wide" vs. "Long" Data Formats
  https://sejdemyr.github.io/r-tutorials/basics/wide-and-long/

== Workshop Steps ==
- Download and review Figure 1a and 2a from the linked paper to see an example of what we're trying to reproduce
https://informaticssummit2018.zerista.com/event/member/470474

- Create a new blank Excel Workbook
- Copy
  [sampleData/labConsecutiveNormalStats.tsv](https://github.com/HealthRex/CDSS/blob/master/scripts/DevWorkshop/sampleData/labConsecutiveNormalStats.tsv) and
  [sampleData/labBaseDisplayNameLookup.tsv](https://github.com/HealthRex/CDSS/blob/master/scripts/DevWorkshop/sampleData/labBaseDisplayNameLookup.tsv)
  (Tab-separated files, like CSV, but with tabs) to Excel worksheet(s). Be sure to use the first row.

- Apply "Freeze Panes" to the Top Row, so that the data will still be visible under the header row, even if scroll down

- Apply "Auto-Filter" to the data, to make it easy to quickly sort and filter the data

- Add columns to the primary data with the "Display Name" for each lab (rather than the coded name), using VLOOKUP on the lookup table.

- Add a column for a "Normal Rate" to the primary data (normal count / total count)

- Select all of the columns of potential interest in the primary data table, and create a new Pivot Chart 
  (Which necessarily creates a respective Pivot Table)

- Drag-and-Drop the columns of interest into different filters, x-axis, y-axis, and value fields in the PivotTable/Chart
- Try different chart types to visualize (will almost always be column/bar and line)


- See final file used in paper for a completed example
https://drive.google.com/file/d/0B01s8toiGe4NTnRTTFBCRzBUTVE/view?usp=sharing
