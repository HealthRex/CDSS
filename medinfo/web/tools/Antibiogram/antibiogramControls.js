/**
 * Copyright 2012, Jonathan H. Chen (jonc101 at gmail.com / jonc101 at stanford.edu)
 *
 */
// Depends on toolkit.js, Color.js, antibiogramData.js

// Color extremes to represent positive vs. negative sensitivity
var SENSITIVITY_COLOR_POSITIVE = new Color('#00ff00');
var SENSITIVITY_COLOR_MODERATE = new Color('#ffff00');
var SENSITIVITY_COLOR_NEGATIVE = new Color('#ff0000');
var SENSITIVITY_COLOR_UNKNOWN = new Color('#f0f0f0');

/**
 * Function called on page load to initialize visualized / selected data
 */
function initialize(theForm)
{
    // Reset the data load field to default data
    loadSensitivityData( theForm.dataLoad, "default");

    updateAntibiogramList(theForm);
    updateBugList(theForm);
    updateDrugList(theForm);
}

/**
 * Quick clear / reset option for user to wipe out prior selections
 */
function clearSelectedBugs()
{
    var theForm = document.forms[0];
    theForm.bugSelected.options.length = 0;
}
function clearSelectedDrugs()
{
    var theForm = document.forms[0];
    theForm.drugSelected.options.length = 0;
}


/**
 * Reset the available antibiogram list based on SENSITIVE_DATA_PER_SOURCE from data file
 */
function updateAntibiogramList(theForm)
{
    // Populate list of antibiograms to choose from
    var sourceKeys = Object.keys(SENSITIVITY_DATA_PER_SOURCE).sort();
    for(var i=0; i<sourceKeys.length; i++)
    {
        var sourceKey = sourceKeys[i];
        if (sourceKey != 'default')
        {
            var option = document.createElement('option');
            option.value = sourceKey;
            option.text = sourceKey;
            option.defaultSelected = ( sourceKey == DEFAULT_SOURCE );
            theForm.antibiogramSelect.add(option);
        }
    }
}


/**
 * Reset the available and selected bug lists to match any category selections
 */
function updateBugList(theForm)
{
    var availableField = theForm.bugAvailable;
    var selectedField = theForm.bugSelected;

    var bugPropField = theForm.bugProp;

    // Build quick lookup dictionary on which bug properties are selected
    var bugPropSelectionDict = {};
    var numPropSelected = 0;
    for( var i=0; i < bugPropField.length; i++ )
    {
        bugPropSelectionDict[bugPropField[i].value] = bugPropField[i].checked;
        if ( bugPropField[i].checked ) { numPropSelected++; }
    }

    // Eliminate any prior data
    availableField.options.length = 0;
    selectedField.options.length = 0;

    // Build up filtered list of items
    var filteredList = new Array();

    for( var i=0; i < BUG_LIST.length; i++ )
    {
        var name = BUG_LIST[i];

        // Only display items for which sensitivity data is available
        if ( name in SENSITIVITY_TABLE_BY_BUG )
        {
            // If any of this bug's properties are in the checked list or no specific one selected, then include it in the available list
            var bugPropList = PROPERTIES_BY_BUG[name];
            if ( numPropSelected == 0 ) { filteredList.push(name); }
            else
            {
                for( var j=0; j < bugPropList.length; j++ )
                {
                    var bugProp = bugPropList[j]
                    if ( bugPropSelectionDict[bugProp] )
                    {   // If within one of the checked drug classes, then initiate in selected list instead
                        filteredList.push(name);
                        break;  // No need to check further properties
                    }
                }
            }
        }
    }

    // Now actually produce the data in sorted in order
    filteredList.sort();
    for( var i=0; i < filteredList.length; i++ )
    {
        var name = filteredList[i];
        availableField.options.add( new Option(name, name) );
        //selectedField.options.add( new Option(name, name) );
    }
}

/**
 * Reset the available and selected drug lists to match any category selections
 */
function updateDrugList(theForm)
{
    var availableField = theForm.drugAvailable;
    var selectedField = theForm.drugSelected;

    var drugPropField = theForm.drugProp;

    // Build quick lookup dictionary on which drug classes are selected
    var drugPropSelectionDict = {};
    var numPropSelected = 0;
    for( var i=0; i < drugPropField.length; i++ )
    {
        drugPropSelectionDict[drugPropField[i].value] = drugPropField[i].checked;
        if ( drugPropField[i].checked ) { numPropSelected++; }
    }

    // Build quick lookup dictionary on which drugs actually have sensitivity data available
    var drugAvailableDict = {};
    for( var bug in SENSITIVITY_TABLE_BY_BUG )
    {
        var sensitivityPerDrug = SENSITIVITY_TABLE_BY_BUG[bug];
        for( var drug in sensitivityPerDrug )
        {
            drugAvailableDict[drug] = true;
        }
    }

    // Eliminate any prior data
    availableField.options.length = 0;
    selectedField.options.length = 0;

    // Build up filtered list of items
    var filteredList = new Array();

    for( var i=0; i < DRUG_LIST.length; i++ )
    {
        var name = DRUG_LIST[i];

        // Only display the drug if sensitivity data is available
        if ( name in drugAvailableDict )
        {
            // If any of the properties are in the checked list or no specific one selected, then include it in the available list
            var drugPropList = PROPERTIES_BY_DRUG[name];
            if ( numPropSelected == 0 ) { filteredList.push(name); }
            else
            {   // If any of this drug's properties are in the checked list, then include it in the available list
                for( var j=0; j < drugPropList.length; j++ )
                {
                    var drugProp = drugPropList[j]
                    if ( drugPropSelectionDict[drugProp] )
                    {   // If within one of the checked drug classes, then initiate in selected list instead
                        filteredList.push(name);
                        break;  // No need to check further properties
                    }
                }
            }
        }
    }

    // Now actually produce the data in sorted in order
    filteredList.sort();
    for( var i=0; i < filteredList.length; i++ )
    {
        var name = filteredList[i];
        availableField.options.add( new Option(name, name) );
        //selectedField.options.add( new Option(name, name) );
    }
}

/**
 * Convenience function.  If user clicks on Bug property name,
 *  have that be equivalent to clicking on the checkbox (but gives user a bigger mouse target to aim for)
 */
function toggleBugProp(bugProp)
{
    var theForm = document.forms[0];
    var bugPropField = theForm.bugProp;

    for( var i=0; i < bugPropField.length; i++ )
    {
        if ( bugPropField[i].value == bugProp )
        {
            bugPropField[i].click();  // Simulate the click
            break;  // Do not need to check further
        }
    }
}

/**
 * Convenience function.  If user clicks on drug class name,
 *  have that be equivalent to clicking on the checkbox (but gives user a bigger mouse target to aim for)
 */
function toggleDrugProp(drugProp)
{
    var theForm = document.forms[0];
    var drugPropField = theForm.drugProp;

    for( var i=0; i < drugPropField.length; i++ )
    {
        if ( drugPropField[i].value == drugProp )
        {
            drugPropField[i].click();  // Simulate the click
            break;  // Do not need to check further
        }
    }
}

/**
 * Top level function to analyze the situation
 */
function doAnalysis(theForm)
{
    reset();    // Reset the feedback field to blank

    // Ensure at least some selections to work with
    var availableField = theForm.bugAvailable;
    var selectedField = theForm.bugSelected;
    if ( selectedField.options.length == 0 )
    {   // None selected, then just auto-select over all available
        selectAllList(availableField, true);
        selectMoveCopy( availableField, selectedField, true );
    }

    var availableField = theForm.drugAvailable;
    var selectedField = theForm.drugSelected;
    if ( selectedField.options.length == 0 )
    {   // None selected, then just auto-select over all available
        selectAllList(availableField, true);
        selectMoveCopy( availableField, selectedField, true );
    }

    document.all['sensitivityTableSpace'].innerHTML = generateSensitivityTableHTML(theForm);
    //printSensitivityTable(theForm);
}

function printSensitivityTable(theForm)
{
    var bugListField = theForm.bugSelected;
    var drugListField = theForm.drugSelected;

    for( var i=0; i < bugListField.options.length; i++ )
    {
        var bug = bugListField.options[i].value;
        if ( bug in SENSITIVITY_TABLE_BY_BUG )
        {
            var sensTable = SENSITIVITY_TABLE_BY_BUG[bug];
            for( var j=0; j < drugListField.options.length; j++ )
            {
                var drug = drugListField.options[j].value;
                var sensValue = null;
                if ( drug in sensTable ) { sensValue = sensTable[drug]['value']; }
                if ( !sensValue && sensValue != 0 ) { sensValue = '?'; }
                print( sensValue );
                print(' ');
            }
            println(bug);
        }
    }
}

/**
 * Generate a simple 2D table of data to represent the core sensitivity data
 * for the currently selected bugs and drugs.  Takes care of steps
 *  like aggregating total column and row values, as well as automatically
 *  excluding rows / columns without data.
 *
 * - Each column for one drug, plus add 1st column for "Number Isolates Tested" data if available
 *      and 2nd column for "All Drugs"
 * - Each row for one bug, plus add 1st column for "All Bugs"
 *
 * Return as a 3-ple array,
 *  1st element being core data table
 *  2nd element being list of column headers
 *  3rd element being list of row headers
 */
function generateSensitivityDataTable(theForm)
{
    var returnData = new Array(3);  // 3-ple of return data elements
    var colHeaders = new Array();
    var rowHeaders = new Array();

    var dataTable = new Array();    // 2D Table = Array of Arrays
    var dataRow; // Next row to add to table

    var bugListField = theForm.bugSelected;
    var drugListField = theForm.drugSelected;

    // Associative array to collect cumulative / aggregate data on each column of drug information
    //  In particular, looking for the worst case scenario of poor / min sensitivity
    var minSensPerDrug = {};

    // Similarly for bug, but account for max case, if use all selected drugs, accept best sensitivity
    var maxSensPerBug = {};

    // Final aggregate statistics.  Take the minimum of all max effects for each drug to see the
    //  worst case sensitivity if treated all selected drugs
    var minOfMaxForAllDrugs = null;

    var totalNumTested = null;

    // Iterate through data to collect aggregate data
    for( var j=0; j < drugListField.options.length; j++ )
    {
        var drug = drugListField.options[j].text;
        minSensPerDrug[drug] = null;    // Start as unknown
    }
    for( var i=0; i < bugListField.options.length; i++ )
    {
        var bug = bugListField.options[i].value;
        maxSensPerBug[bug] = null;  // Start as unknown

        var bugSensTable = {};
        if ( bug in SENSITIVITY_TABLE_BY_BUG )
        {
            bugSensTable = SENSITIVITY_TABLE_BY_BUG[bug];
        }

        var numTested = null;   // Default to unknown if based on general reference source
        if ( NUMBER_TESTED_KEY in bugSensTable )
        {
            numTested = bugSensTable[NUMBER_TESTED_KEY]['value'];
            if ( !totalNumTested ) { totalNumTested = 0; }
            totalNumTested += numTested;
        }
        for( var j=0; j < drugListField.options.length; j++ )
        {
            var drug = drugListField.options[j].value;
            var valueMap = bugSensTable[drug];
            var sensValue = (valueMap && (valueMap['value'] || valueMap['value']==0 ) ? valueMap['value'] : valueMap);

            if ( maxSensPerBug[bug] == null || sensValue > maxSensPerBug[bug] )
            {
                maxSensPerBug[bug] = sensValue;
            }
            if ( minSensPerDrug[drug] == null || sensValue < minSensPerDrug[drug] )
            {
                minSensPerDrug[drug] = sensValue;
            }
        }

        if ( minOfMaxForAllDrugs == null || maxSensPerBug[bug] < minOfMaxForAllDrugs )
        {
            minOfMaxForAllDrugs = maxSensPerBug[bug];
        }
    }

    // With the aggregate data now available, now iterate again to actually construct the data table
    // First add a drug name header row and a row for aggregate sensitivity if count all bugs

    colHeaders.push('Microbe');
    if ( totalNumTested ) { colHeaders.push('Isolates Tested'); } // Only show if have data
    colHeaders.push('ALL DRUGS');

    rowHeaders.push('ALL BUGS');
    dataRow = new Array();
    dataTable.push(dataRow);
    if ( totalNumTested ) { dataRow.push(totalNumTested); }
    dataRow.push(minOfMaxForAllDrugs);
    for( var j=0; j < drugListField.options.length; j++ )
    {
        var drug = drugListField.options[j].value;
        if ( minSensPerDrug[drug] == null ) { continue; }   // Skip cols with no data
        colHeaders.push(drug);
        dataRow.push(minSensPerDrug[drug]);
    }

    // Core data table
    for( var i=0; i < bugListField.options.length; i++ )
    {
        var bug = bugListField.options[i].value;
        if ( maxSensPerBug[bug] == null ) { continue; }  // Skip rows with no data
        rowHeaders.push(bug);

        dataRow = new Array();
        dataTable.push(dataRow);

        // Load data for lookup
        var bugSensTable = {};
        if ( bug in SENSITIVITY_TABLE_BY_BUG )
        {
            bugSensTable = SENSITIVITY_TABLE_BY_BUG[bug];
        }

        // Add header / summary columns
        if ( totalNumTested )
        {
            var numTested = null;   // Default to unknown if based on general reference source
            if ( NUMBER_TESTED_KEY in bugSensTable )
            {
                numTested = bugSensTable[NUMBER_TESTED_KEY]['value'];
            }
            dataRow.push(numTested);
        }
        dataRow.push(maxSensPerBug[bug]);

        for( var j=0; j < drugListField.options.length; j++ )
        {
            var drug = drugListField.options[j].value;
            if ( minSensPerDrug[drug] == null ) { continue; }   // Skip cols with no data

            var valueMap = bugSensTable[drug];
            dataRow.push(valueMap);
        }
    }

    return [dataTable, colHeaders, rowHeaders];
}

/**
 * Produce the HTML table representation of sensitivity data for the selected bugs and drugs
 */
function generateSensitivityTableHTML(theForm)
{
    // Separate data preparation from presentation steps
    var dataTuple = generateSensitivityDataTable(theForm);
    var dataTable = dataTuple[0];
    var colHeaders = dataTuple[1];
    var rowHeaders = dataTuple[2];

	// Determine if have isolates tested counts from real data, or more qualitative data
	var haveIsolatesTested = ( colHeaders.indexOf('Isolates Tested') > -1 );

    // Now actually adapt the data table into HTML presented form
    var tableHTML = new Array();

    // Header Row
    tableHTML.push('<table border=0 cellpadding=2 cellspacing=2>');
    tableHTML.push('<tr valign=bottom>');
    for( var j=0; j < colHeaders.length; j++ )
    {
        if ( j == 0 )   // Don't modify the first header column
        {
            tableHTML.push('<th class="headerRow">'+colHeaders[j]+'</th>');
        }
        else
        {
            tableHTML.push('<th class="headerRow">'+formatHeader(colHeaders[j])+'</th>');
        }
    }
    tableHTML.push('</tr>');

    // Iterate through bug rows
    for( var i=0; i < dataTable.length; i++ )
    {
        tableHTML.push('<tr valign=middle>');

        // Header Column
        tableHTML.push('<td align=center class="headerCol" nowrap>'+(rowHeaders[i])+'</td>');

        var dataRow = dataTable[i];
        // Iterate through drug columns / cells
        for( var j=0; j < dataRow.length; j++ )
        {
            var valueMap = dataRow[j];
            var dataValue = (valueMap && (valueMap['value'] || valueMap['value']==0)? valueMap['value'] : valueMap);
            
            tableHTML.push('<td align=center style="background-color: '+cellColorPerValue(dataValue)+'">'+formatValue(dataValue, valueMap, !haveIsolatesTested)+'</td>');
        }
        tableHTML.push('</tr>');
    }

    tableHTML.push('</table>');

    return tableHTML.join("\n");
}

/**
 * Format header text for display.  Preferably sideways, but may have to improvise
 */
function formatHeader(inText)
{
    inText = inText.replace('/',' / ');

    return inText;

    // return '<div class="rotateText">'+inText+'</div>';

    var outText = new Array();
    for( var i=0; i < inText.length; i++ )
    {
        outText.push(inText.charAt(i));
    }
    return outText.join('<br>\n');

}

/**
 * Format cell value.  Usually just direct, but if null / undefined, then '?'
 * If qualitative set, then look for broad values to label as just +, +/-, or -
 */
function formatValue(inText, valueMap, qualitative)
{
    var formatStr = inText;
    if ( !inText && inText != 0 )
    {
        formatStr = '?';
    }
    else if ( qualitative )
    {
    	if 		( inText >= DEFAULT_SENSITIVITY_POSITIVE ) { formatStr = '+'; }
    	else if ( inText <= DEFAULT_SENSITIVITY_NEGATIVE ) { formatStr = '-'; }
    	else // ( inText ~ DEFAULT_SENSITIVITY_MODERATE )
    	{
    		formatStr = '+/-';
    	}
    }
    
    if ( valueMap && valueMap['comment'] )
    {	// Comment attached to data value.  Present as link pop-up information
    	formatStr = '<a href="javascript: println(\''+valueMap['comment']+'\'); alert(\''+valueMap['comment']+'\');">'+formatStr+'*</a>';
    }
    return formatStr;
}

/**
 * Based on the drug sensitivity represented by the cell, specify a background color to help highlight
 * Expects sensitivityValue to range from 0 to 100 representing a percentage
 */
function cellColorPerValue(sensValue)
{
    if ( !sensValue && sensValue != 0 || sensValue == '?') { return SENSITIVITY_COLOR_UNKNOWN.valueOf(); }

    sensValue = ( sensValue > 100 ? 100 : sensValue );
    sensValue = ( sensValue < 0 ? 0 : sensValue );

    var posColor = SENSITIVITY_COLOR_POSITIVE;
    var negColor = SENSITIVITY_COLOR_NEGATIVE;
    var scalar = null;

    // For brighter color in moderate range, use different delimiting color there
    //  and scale sensitivity value to 0.0-1.0 range
    if ( sensValue > 50 )
    {
        negColor = SENSITIVITY_COLOR_MODERATE;
        scalar = (sensValue-50)/50.0;
    }
    else
    {
        posColor = SENSITIVITY_COLOR_MODERATE;
        scalar = sensValue/50.0;
    }

    var cellColor = new Color();
    cellColor.setRed( negColor.getRed() + (posColor.getRed()-negColor.getRed()) * scalar );
    cellColor.setGreen( negColor.getGreen() + (posColor.getGreen()-negColor.getGreen()) * scalar );
    cellColor.setBlue( negColor.getBlue() + (posColor.getBlue()-negColor.getBlue()) * scalar );
    return cellColor.valueOf();
}


/**
 * Load the data input field with pre-constructed antibiogram data
 *  and auto-submit to update in-memory sensitivity data
 */
function loadSensitivityData( dataLoadField, antibiogramName, noAutoSubmit, keepPriorData )
{
    var clearPriorData = !keepPriorData;
    if ( !antibiogramName )
    {
        antibiogramName = "default";
    }
    dataLoadField.value = SENSITIVITY_DATA_PER_SOURCE[antibiogramName];

    if ( !noAutoSubmit )
    {
        submitSensitivityData(dataLoadField, clearPriorData);
    }
}

/**
 * Submit the sensitivity data in the input field to update or replace
 *  the current in-memory sensitivity data
 *
 * clearPriorData - If set, will first wipe out any prior sensitivity data.
 *      Default left unset, will just update prior data with new ones
 */
function submitSensitivityData(dataLoadField, clearPriorData)
{
    var theForm = dataLoadField.form;

    if ( clearPriorData )
    {
        for( var bug in SENSITIVITY_TABLE_BY_BUG )
        {
            delete SENSITIVITY_TABLE_BY_BUG[bug];
        }
    }
    // Parse through the data load field line by line
    var dataLines = dataLoadField.value.split('\n');
    for( var i=0; i < dataLines.length; i++ )
    {
        var dataLine = dataLines[i].trim();
        if ( dataLine )
        {
            var dataChunks = dataLine.split('\t');
            if ( dataChunks.length < 3 )
            {
                println('Expected 3 columns from line '+i+': '+ dataLine );
            }
            else
            {
                var sens = parseInt(dataChunks[0]);
                var bug = dataChunks[1];
                var drug = dataChunks[2];
                var comment = null;
                if ( dataChunks.length > 3 ) { comment = dataChunks[3]; }	// Optional footnote / comment

                if ( isNaN(sens) )
                {
                    println('Expect value from 0-100, but got non-numeric sensitivity value in 1st column of line '+i+': '+ dataLine );
                }
                else if ( !(bug in PROPERTIES_BY_BUG) )
                {
                    println('Unrecognized bug name in 2nd column of line '+i+': '+ dataLine );
                }
                else if ( !(drug in PROPERTIES_BY_DRUG) )
                {
                    println('Unrecognized drug name in 3rd column of line '+i+': '+ dataLine );
                }
                else
                {   // Data looks valid.  Numerical sensitivity and recognized bug and drug names
                    if ( !(bug in SENSITIVITY_TABLE_BY_BUG) )
                    {
                        SENSITIVITY_TABLE_BY_BUG[bug] = {};
                    }
                    SENSITIVITY_TABLE_BY_BUG[bug][drug] = {'value':sens, 'comment':comment};
                }
            }
        }
    }
    println('Completed parsing '+i+' lines of data');

    // Update the list of available bugs and drugs to select from
    updateBugList(theForm);
    updateDrugList(theForm);
}


/**
 * Convenience function for printing out messages to the feedback element.
 *  Include indentation depth option
 */
function print( message, depth )
{
    var theForm = document.forms[0];
    var feedbackField = theForm.feedback;

    depth = parseInt(depth);
    if (depth)
    {
        for( var i=0; i < depth; i++ )
        {
            feedbackField.value += '   ';
        }
    }
    feedbackField.value += message;
}
function println( message, depth )
{
    if ( !message ) { message = ''; }
    print( message +'\n', depth );
}
function summaryPoint( message )
{
    var theForm = document.forms[0];
    theForm.summary.value += '= '+message+' ='+'\n';
}

function reset()
{
    var theForm = document.forms[0];
    theForm.feedback.value = '';
    theForm.summary.value = '';
}

