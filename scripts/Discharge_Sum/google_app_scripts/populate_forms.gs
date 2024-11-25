function populateForms() {
  var startTime = (new Date()).getTime();

  // Open the log spreadsheet and get the specified sheet
  var log_sheet = SpreadsheetApp.openById(log_spreadsheetId).getActiveSheet();

  // Get all values in the ID column
  var idRange = log_sheet.getRange(2, 2, log_sheet.getLastRow() - 1, 1);
  var formIDs = idRange.getValues();

  var data_sheet = SpreadsheetApp.openById(data_spreadsheetId).getActiveSheet();
  var data = data_sheet.getDataRange().getValues();
  var headers = data[0];

  // Get links to notes
  var log_data = log_sheet.getDataRange().getValues();

  // Extract the fourths column
  var link_to_notes = log_data.map(function(row) {
    return [row[4]]; // Index 4 corresponds to the fourth column
  });

  // Open the loglog spreadsheet and get the active sheet
  var loglog_sheet = SpreadsheetApp.openById(loglog_spreadsheetId).getActiveSheet();

  // Get i_start, ouput 1 if the cell is left empty
  var i_start = Number(loglog_sheet.getRange(1,2).getValues()) || 1;
  Logger.log("i_start is " + i_start);

  for (var i = i_start; i < data.length; i++) {
    var currTime = (new Date()).getTime();
    if (currTime - startTime >= 1500000) { // stop after 25 minutes
      ScriptApp.newTrigger("populateForms")
          .timeBased()
          .at(new Date(currTime + 300000)) // restart 5 minutes later
          .create();
      break;
    } else {
    var form = FormApp.openById(formIDs[i-1]);
    form.setTitle(data[i][0]); // The first column is the form name
    
    for (var j = 1; j < 4; j++) { //changed n_col for 4 here no text added
      var sectionHeader = form.addMultipleChoiceItem();
      sectionHeader.setTitle(headers[j])
      sectionHeader.setChoiceValues([data[i][j]]).setRequired(true);
      Logger.log('Populated form ' + i + ": field " + j)
    }
    sectionHeader.setTitle('Link to notes')
    sectionHeader.setChoiceValues(link_to_notes[i])

    Logger.log('Populating form ' + i + " with questions...")
var some_choices = ['33 - Low Importance: This component has minimal impact and can be deprioritized.',
   '50 - Moderate Importance: This component is somewhat important and should be considered.',
   '66 - High Importance: This component is very important, and poor performance on it leads to low-quality discharge summaries.',
   '100 - Critical Importance: This component is essential, and poor performance on it results in highly unreliable discharge summaries.']
var all_choices = ['0 - Very Low Importance: This component can be ignored.',
   '33 - Low Importance: This component has minimal impact and can be deprioritized.',
   '50 - Moderate Importance: This component is somewhat important and should be considered.',
   '66 - High Importance: This component is very important, and poor performance on it leads to low-quality discharge summaries.',
   '100 - Critical Importance: This component is essential, and poor performance on it results in highly unreliable discharge summaries.']
var axes = [
  { title: "EVALUATION COMPONENT NO. 1", weight: "Importance of evaluation component no. 1", choices: some_choices, perfect: "Ideal response for evaluation component no. 1", fair: "Adequate response for evaluation component no. 1", wrong: "Incorrect response for evaluation component no. 1", req: true},
  { title: "EVALUATION COMPONENT NO. 2", weight: "Importance of evaluation component no. 2", choices: some_choices,  perfect: "Ideal response for evaluation component no. 2", fair: "Adequate response for evaluation component no. 2", wrong: "Incorrect response for evaluation component no. 2", req: true },
  { title: "EVALUATION COMPONENT NO. 3", weight: "Importance of evaluation component no. 3", choices: some_choices,  perfect: "Ideal response for evaluation component no. 3", fair: "Adequate response for evaluation component no. 3", wrong: "Incorrect response for evaluation component no. 3", req: true },
  { title: "EVALUATION COMPONENT NO. 4", weight: "Importance of evaluation component no. 4", choices: some_choices,  perfect: "Ideal response for evaluation component no. 4", fair: "Adequate response for evaluation component no. 4", wrong: "Incorrect response for evaluation component no. 4", req: true },
  { title: "EVALUATION COMPONENT NO. 5", weight: "Importance of evaluation component no. 5", choices: some_choices,  perfect: "Ideal response for evaluation component no. 5", fair: "Adequate response for evaluation component no. 5", wrong: "Incorrect response for evaluation component no. 5", req: true },
  { title: "EVALUATION COMPONENT NO. 6", weight: "Importance of evaluation component no. 6", choices: all_choices,  perfect: "Ideal response for evaluation component no. 6", fair: "Adequate response for evaluation component no. 6", wrong: "Incorrect response for evaluation component no. 6", req: false },
  { title: "EVALUATION COMPONENT NO. 7", weight: "Importance of evaluation component no. 7", choices: all_choices,  perfect: "Ideal response for evaluation component no. 7", fair: "Adequate response for evaluation component no. 7", wrong: "Incorrect response for evaluation component no. 7", req: false },
  { title: "EVALUATION COMPONENT NO. 8", weight: "Importance of evaluation component no. 8", choices: all_choices,  perfect: "Ideal response for evaluation component no. 8", fair: "Adequate response for evaluation component no. 8", wrong: "Incorrect response for evaluation component no. 8", req: false },
  { title: "EVALUATION COMPONENT NO. 9", weight: "Importance of evaluation component no. 9", choices: all_choices,  perfect: "Ideal response for evaluation component no. 9", fair: "Adequate response for evaluation component no. 9", wrong: "Incorrect response for evaluation component no. 9", req: false },
  { title: "EVALUATION COMPONENT NO. 10", weight: "Importance of evaluation component no. 10", choices: all_choices,  perfect: "Ideal response for evaluation component no. 10", fair: "Adequate response for evaluation component no. 10", wrong: "Incorrect response for evaluation component no. 10", req: false }
];
    axes.forEach(function(axis) {
    form.addTextItem().setTitle(axis.title).setRequired(axis.req);
    form.addMultipleChoiceItem().setTitle(axis.weight).setChoiceValues(axis.choices).setRequired(true);
    form.addParagraphTextItem().setTitle(axis.perfect).setHelpText('i.e., the evaluator will assign +2 points if ALL information below is provided.').setRequired(axis.req);
    form.addParagraphTextItem().setTitle(axis.fair).setHelpText('i.e., the evaluator will assign +1 point if ALL information below is provided.').setRequired(axis.req);
    form.addParagraphTextItem().setTitle(axis.wrong).setHelpText('i.e., the evaluator will assign -1 point if ANY information below is provided.').setRequired(axis.req);
  });
  form.addMultipleChoiceItem().setTitle("Include in the evaluation benchmark?").setChoiceValues(['YES', 'NO']).setRequired(true)
  Logger.log('Finished populating form no. ' + i)

  // Log the progress in loglog sheet
  loglog_sheet.getRange(1,2).setValue(i+1)
}
}
}