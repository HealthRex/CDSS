// ID of the patient_notes google drive folder
var patient_notes_folderID = '1FajdUHewYtYV7h1WKsTKtfN-mp_WdYI_'

// ID of the form you want to copy
var templateFormId = '1T2GkCEYrrNzw9rp4r1DSaJhPzkLahMQHE_fFHqsA2CM';

// ID of the spreadsheet where you want to store forms' information
var log_spreadsheetId = '1AaSoVVRrrKBg6y5vlugF4m6rlOYSiauHDzLUJePh_3g';

// ID of the spreadsheet containing the data to populate the forms
var data_spreadsheetId = "1z0G7PBOU69xk0pDVIfR0h8gp-kByO6dYTcxEe-fWg2Q"

// ID of the spreadsheet where you want to collect all responses
var resp_spreadsheetId = '1NS3sEJvc7rPpDizvhrrDxdsS8qrRrOjeyFAph5cZr9U';

// ID of the prefilling spreadsheet
var prefil_spreadsheetId = '1KB_PXGg9ZThYWEnpp-lNAPzC4-_JuFWcUYzIqpoK0MA'

// ID of the spreadsheet where you want to store no. of iterations
var loglog_spreadsheetId = '1aMrE3BrocnegF1XmW3BwFAg0weZlS5VmhRzZv2F_5Rg';

function createFormCopies() {
  var startTime = (new Date()).getTime();

  // Number of copies is the no. of observation in the dataset
  var numberOfCopies = SpreadsheetApp.openById(data_spreadsheetId).getActiveSheet().getLastRow() -1
  
  // Get the source form file
  var sourceFile = DriveApp.getFileById(templateFormId);
  
  // Get the folder where the source form is located
  var parentFolder = sourceFile.getParents().next();
  
  // Open the log spreadsheet and get the active sheet
  var log_sheet = SpreadsheetApp.openById(log_spreadsheetId).getActiveSheet();
  
  const i_start = getHighestNumberedFile(parentFolder.getId()) + 1 ;
  Logger.log("i_start is " + i_start)

  if (i_start < 2) {
  // Add headers
  log_sheet.appendRow(['Form_no', 'Form_ID', 'Form_link', 'Prefilled_form_link', 'Note_link'])
  }

  for (var i = i_start; i <= numberOfCopies; i++) {
    var currTime = (new Date()).getTime();
    if (currTime - startTime >= 1500000) { // stop after 25 minutes
      ScriptApp.newTrigger("createFormCopies")
          .timeBased()
          .at(new Date(currTime + 300000)) // restart 5 minutes later
          .create();
      break;
    } else {
    // Create a copy of the form
    var newFile = sourceFile.makeCopy('Form_' + i, parentFolder);

    // Get the ID of the new form
    var newFormID = newFile.getId();

    // Get the URL of the new form
    var newFormUrl = newFile.getUrl();
    
    // Append the form information to the log spreadsheet
    log_sheet.appendRow(['Form_' + i, newFormID, newFormUrl]);

    Logger.log("Created form no. " + i)
    }
  }
}

function getHighestNumberedFile(folderId) {
  // Get the folder by ID
  const folder = DriveApp.getFolderById(folderId);
  
  // Get all files in the folder
  const files = folder.getFiles();
  
  let highestNumber = 0;
  
  // Iterate through all files
  while (files.hasNext()) {
    const file = files.next();
    const fileName = file.getName();
    
    // Extract numbers from filename using regex
    const matches = fileName.match(/\d+/g);
    
    if (matches) {
      // Convert all found numbers to integers and find the highest
      matches.forEach(match => {
        const num = parseInt(match, 10);
        if (!isNaN(num) && num > highestNumber) {
          highestNumber = num;
        }
      });
    }
  }
  
  return highestNumber;
}