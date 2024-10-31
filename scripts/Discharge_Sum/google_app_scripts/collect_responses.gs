function linkFormsToSpreadsheet() {
  // Open the log spreadsheet
  var log_sheet = SpreadsheetApp.openById(log_spreadsheetId).getActiveSheet();

// Get all values in the ID column
  var idRange = log_sheet.getRange(2, 2, log_sheet.getLastRow() - 1, 1);
  var formIDs = idRange.getValues();
  
  // Loop through each form ID
  var i = 1
  formIDs.forEach(function(formId) {
    var form = FormApp.openById(formId);

    // Set the form's response destination to the response spreadsheet
    form.setDestination(FormApp.DestinationType.SPREADSHEET, resp_spreadsheetId);

    Logger.log('Linked form no. ' + i )
    i++
  });
}