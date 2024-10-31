function deleteAll() {
  // DELETE FORMS
  // Get all forms in the user's Google Drive
  var forms = DriveApp.getFilesByType(MimeType.GOOGLE_FORMS);
  
  while (forms.hasNext()) {
    var form = forms.next();
    var formName = form.getName();
    
    // Check if the form name starts with "form_"
    if (formName.startsWith("form_")) {
      form.setTrashed(true); // Move the form to trash
      Logger.log('Deleted form: ' + formName);
    }
  }

  // CLEAR SPREADSHEET CONTENT
// Names of the spreadsheets to clear
  var spreadsheetNames = ["forms_IDs", "Gforms_results"];
  
  // Loop through each spreadsheet name
  for (var i = 0; i < spreadsheetNames.length; i++) {
    var spreadsheetName = spreadsheetNames[i];
    
    // Find the file by name
    var files = DriveApp.getFilesByName(spreadsheetName);
    
    if (files.hasNext()) {
      var file = files.next();
      var spreadsheet = SpreadsheetApp.open(file);
      
      // Get all sheets in the spreadsheet
      var sheets = spreadsheet.getSheets();
      
      // Loop through each sheet
      for (var j = 0; j < sheets.length; j++) {
        var sheet = sheets[j];
        
        // Unlink the sheet from any Google Form
        try {
          var formUrl = sheet.getFormUrl();
          if (formUrl) {
            var form = FormApp.openByUrl(formUrl);
            form.removeDestination();
            Logger.log('Unlinked form from sheet: ' + sheet.getName());
          }
        } catch (e) {
          Logger.log('No form linked to sheet: ' + sheet.getName());
        }
        
        // Try to delete the sheet
        try {
          spreadsheet.deleteSheet(sheet);
          Logger.log('Deleted sheet: ' + sheet.getName());
        } catch (e) {
          try {
            Logger.log('Could not delete sheet will try clearing content instead.');
            sheet.clear(); // Clear all content in the sheet if deletion fails
          } catch (e) {
            Logger.log('Could neither delete the sheet nor delete its content')
          }
        }
      }
      
      Logger.log('Processed spreadsheet: ' + spreadsheetName);
    } else {
      Logger.log('Spreadsheet not found: ' + spreadsheetName);
    }
  }
}