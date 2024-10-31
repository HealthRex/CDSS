function createPrefilledUrl() {
  // Open the prefilling spreadsheet and get the specified sheet
  var prefil_sheet = SpreadsheetApp.openById(prefil_spreadsheetId).getActiveSheet();

  // Get all values in the ID column
  var prefilling = prefil_sheet.getRange(2, 1, 2, prefil_sheet.getLastColumn()).getValues();

  // Open the log spreadsheet and get the specified sheet
  var log_sheet = SpreadsheetApp.openById(log_spreadsheetId).getActiveSheet();
  
  // Get all values in the ID column
  var idRange = log_sheet.getRange(2, 2, log_sheet.getLastRow() - 1, 1);
  var formIDs = idRange.getValues();

  var i = 0
  formIDs.forEach(function(formId) {
  // Get the form by ID
  var form = FormApp.openById(formId);
  
  // Create a form response
  var formResponse = form.createResponse();
  
  // Get all form items
  var items = form.getItems();
  
  // Loop through items and set pre-filled responses
  var j = 0
  items.forEach(function(item) {
    switch(item.getType()) {
      case FormApp.ItemType.TEXT:
        var textItem = item.asTextItem();
        formResponse.withItemResponse(textItem.createResponse(prefilling[0][j])); // change to prefilling[i][j] later
        j++
        break;
      case FormApp.ItemType.PARAGRAPH_TEXT:
        var paragItem = item.asParagraphTextItem();
        formResponse.withItemResponse(paragItem.createResponse(prefilling[0][j])); // change to prefilling[i][j] later
        j++
        break;
      case FormApp.ItemType.LIST:
        var listItem = item.asListItem();
        var choices = listItem.getChoices();
        formResponse.withItemResponse(listItem.createResponse(choices[0].getValue()));
        break;
      // Add more cases for other question types as needed
    }
  });
  
  // Generate the pre-filled URL
  var prefilledUrl = formResponse.toPrefilledUrl();
  
  // Add the form URL to the data spreadsheet
  log_sheet.getRange(i + 2, 3).setValue(prefilledUrl);
  Logger.log('Pre-filled form no. ' + (i + 1));

  // Update iteration count
  i++
  });
}