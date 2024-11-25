function linkFormsToSpreadsheet() {
  var startTime = (new Date()).getTime();

  // Open the log spreadsheet
  var log_sheet = SpreadsheetApp.openById(log_spreadsheetId).getActiveSheet();

  // Get all values in the ID column
  var idRange = log_sheet.getRange(2, 2, log_sheet.getLastRow() - 1, 1);
  var formIDs = idRange.getValues();
  
  // Open the loglog spreadsheet and get the active sheet
  var loglog_sheet = SpreadsheetApp.openById(loglog_spreadsheetId).getActiveSheet();

  // Get i_start, ouput 0 if the cell is left empty
  var i_start = Number(loglog_sheet.getRange(1,3).getValues()) || 0;
  Logger.log("i_start is " + i_start);

  // Loop through each form ID
  for (var i = i_start; i < formIDs.length; i++) {
    var currTime = (new Date()).getTime();
    if (currTime - startTime >= 1500000) { // stop after 25 minutes
      ScriptApp.newTrigger("linkFormsToSpreadsheet")
          .timeBased()
          .at(new Date(currTime + 300000)) // restart 5 minutes later
          .create();
      break;
    } else {
      var formId = formIDs[i][0];  // Need to access [0] since getValues returns 2D array
      var form = FormApp.openById(formId);

      // Set the form's response destination to the response spreadsheet
      form.setDestination(FormApp.DestinationType.SPREADSHEET, resp_spreadsheetId);

      Logger.log('Linked form no. ' + (i + 1));
      // Log the progress in loglog sheet
      loglog_sheet.getRange(1,3).setValue(i+1)
    }
  }
}