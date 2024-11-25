function shareDocsInFolderWithStanford() {
  var startTime = (new Date()).getTime();

  // Get the folder by ID
  var folder = DriveApp.getFolderById(patient_notes_folderID);

  // Get all files in the folder
  var files = folder.getFilesByType('application/vnd.openxmlformats-officedocument.wordprocessingml.document');

  // Create an array to store the files
  var fileArray = [];
  while (files.hasNext()) {
    fileArray.push(files.next());
  }

  // Sort the file array by name
  fileArray.sort(function(a, b) {
    return a.getName().localeCompare(b.getName());
  });

  // Open the loglog spreadsheet and get the active sheet
  var loglog_sheet = SpreadsheetApp.openById(loglog_spreadsheetId).getActiveSheet();

  // Get i_start, ouput 0 if the cell is left empty
  var i_start = Number(loglog_sheet.getRange(1,1).getValues()) || 0;
  Logger.log("i_start is " + i_start);

  // Iterate through the sorted file array
  for (var i = i_start; i < fileArray.length; i++) {
    var currTime = (new Date()).getTime();
    if (currTime - startTime >= 1500000) { // stop after 25 minutes
      ScriptApp.newTrigger("shareDocsInFolderWithStanford")
          .timeBased()
          .at(new Date(currTime + 300000)) // restart 5 minutes later
          .create();
      break;
    } else {
    var file = fileArray[i];

    // Share the file with anyone at Stanford in viewer mode
    file.setSharing(DriveApp.Access.DOMAIN_WITH_LINK, DriveApp.Permission.VIEW);

    Logger.log("i is " + i);
    // Log the progress in loglog sheet
    loglog_sheet.getRange(1,1).setValue(i+1)
    }
  }
}