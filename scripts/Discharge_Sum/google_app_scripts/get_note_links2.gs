function getFileUrlsFromFolder() {  
  // Get the folder and spreadsheet
  const folder = DriveApp.getFolderById(patient_notes_folderID);
  const spreadsheet = SpreadsheetApp.openById(log_spreadsheetId);
  const sheet = spreadsheet.getActiveSheet();
  
  // Get all files in the folder
  const files = folder.getFiles();
  
  // Create an array to store file information
  const fileInfo = [];
  
  // Collect file names and URLs
  while (files.hasNext()) {
    const file = files.next();
    fileInfo.push({
      name: file.getName(),
      url: file.getUrl()
    });
  }
  
  // Sort the array by numbers in filenames
  fileInfo.sort((a, b) => {
    // Extract numbers from filenames using regex
    const numA = parseInt(a.name.match(/\d+/)?.[0] || '0');
    const numB = parseInt(b.name.match(/\d+/)?.[0] || '0');
    return numA - numB;
  });
  
  // Write the sorted data to the spreadsheet
  fileInfo.forEach((file, index) => {
    sheet.getRange(index + 2, 5).setValue(file.url);
  });

}