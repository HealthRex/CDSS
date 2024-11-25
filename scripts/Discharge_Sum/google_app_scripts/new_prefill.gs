function createPrefilledUrl() {
  var startTime = (new Date()).getTime();

  // Open the loglog spreadsheet and get the active sheet
  var loglog_sheet = SpreadsheetApp.openById(loglog_spreadsheetId).getActiveSheet();

  // Get i_start, ouput 0 if the cell is left empty
  var i_start = Number(loglog_sheet.getRange(1,4).getValues()) || 0;
  Logger.log("i_start is " + i_start);

  // Open the prefilling spreadsheet and get the specified sheet
  var prefil_sheet = SpreadsheetApp.openById(prefil_spreadsheetId).getActiveSheet();

  // Get all values in the ID column
  var prefilling = prefil_sheet.getRange(2, 1, prefil_sheet.getLastRow(), prefil_sheet.getLastColumn()).getValues();

  // Open the log spreadsheet and get the specified sheet
  var log_sheet = SpreadsheetApp.openById(log_spreadsheetId).getActiveSheet();
  
  // Get all values in the ID column
  var idRange = log_sheet.getRange(2, 2, log_sheet.getLastRow() - 1, 1);
  var formIDs = idRange.getValues();

  var i = i_start;
  for (var formIdIndex = i_start; formIdIndex <  formIDs.length; formIdIndex++) {
    var currTime = (new Date()).getTime();
    if (currTime - startTime >= 1500000) { // stop after 25 minutes
      ScriptApp.newTrigger("createPrefilledUrl")
          .timeBased()
          .at(new Date(currTime + 300000)) // restart 5 minutes later
          .create();
      break;
    } else {
    // Get the form by ID
    var form = FormApp.openById(formIDs[formIdIndex]);
    
    // Create a form response
    var formResponse = form.createResponse();
    
    // Get all form items
    var items = form.getItems();
    
    // Loop through items and set pre-filled responses
    var j = 0; // iteration n on text
    var k = 0; // iteration n on multiple choice
    for (var itemIndex = 0; itemIndex < items.length; itemIndex++) {
      var item = items[itemIndex];
      switch(item.getType()) {
        case FormApp.ItemType.TEXT:
          var textItem = item.asTextItem();
          formResponse.withItemResponse(textItem.createResponse(prefilling[i][j])); 
          j++;
          break;
        case FormApp.ItemType.PARAGRAPH_TEXT:
          var paragItem = item.asParagraphTextItem();
          formResponse.withItemResponse(paragItem.createResponse(prefilling[i][j])); 
          j++;
          break;
        case FormApp.ItemType.MULTIPLE_CHOICE:
          var multipleChoiceItem = item.asMultipleChoiceItem();
          var choices = multipleChoiceItem.getChoices();
          if (k > 2 && k < 8) {
            formResponse.withItemResponse(multipleChoiceItem.createResponse(choices[1].getValue()));
          } else {
            formResponse.withItemResponse(multipleChoiceItem.createResponse(choices[0].getValue()));
          }
          k++;
          break;
        // Add more cases for other question types as needed
      }
    }
    
    // Generate the pre-filled URL
    var prefilledUrl = formResponse.toPrefilledUrl();
    
    // Add the form URL to the data spreadsheet
    log_sheet.getRange(i + 2, 4).setFormula('=HYPERLINK("' + prefilledUrl + '", "Prefilled Form")');
    Logger.log('Pre-filled form no. ' + (i + 1));
    //Logger.log(prefilledUrl);

    // Update iteration count
    i++;
    // Log the progress in loglog sheet
    loglog_sheet.getRange(1,4).setValue(i)
  }
}
}