// ID of the form you want to copy
var templateFormId = '1T2GkCEYrrNzw9rp4r1DSaJhPzkLahMQHE_fFHqsA2CM';

// ID of the spreadsheet where you want to store forms' information
var log_spreadsheetId = '1AaSoVVRrrKBg6y5vlugF4m6rlOYSiauHDzLUJePh_3g';

// ID of the spreadsheet containing the data to populate the forms
var data_spreadsheetId = "1z0G7PBOU69xk0pDVIfR0h8gp-kByO6dYTcxEe-fWg2Q"

// ID of the spreadsheet where you want to collect all responses
var resp_spreadsheetId = '13rmntzLJYLjGpnWvYc4FTfEvP0CXaw7e_IL84J_vRNg';

// ID of the prefilling spreadsheet
var prefil_spreadsheetId = '1KB_PXGg9ZThYWEnpp-lNAPzC4-_JuFWcUYzIqpoK0MA'

function createFormCopies() {
  // Number of copies is the no. of observation in the dataset
  var numberOfCopies = SpreadsheetApp.openById(data_spreadsheetId).getActiveSheet().getLastRow() -1
  
  // Get the source form file
  var sourceFile = DriveApp.getFileById(templateFormId);
  
  // Get the folder where the source form is located
  var parentFolder = sourceFile.getParents().next();
  
  // Open the log spreadsheet and get the active sheet
  var log_sheet = SpreadsheetApp.openById(log_spreadsheetId).getActiveSheet();
  
  // Add headers
  log_sheet.appendRow(['Form_no', 'Form_ID', 'Form_link'])
  
  for (var i = 1; i <= numberOfCopies; i++) {
    // Create a copy of the form
    var newFile = sourceFile.makeCopy('form_' + i, parentFolder);
    
    // Get the ID of the new form
    var newFormId = newFile.getId();
    
    // Open the new form and set its title
    var newForm = FormApp.openById(newFormId);
    newForm.setTitle('form_' + i);
    
    // Append the form information to the log spreadsheet
    log_sheet.appendRow([newForm.getTitle(), newFormId]);

    Logger.log("Created form no. " + i)
  }
}