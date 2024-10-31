function populateForms() {
  // Open the log spreadsheet and get the specified sheet
  var log_sheet = SpreadsheetApp.openById(log_spreadsheetId).getActiveSheet();

  // Get all values in the ID column
  var idRange = log_sheet.getRange(2, 2, log_sheet.getLastRow() - 1, 1);
  var formIDs = idRange.getValues();

  var data_sheet = SpreadsheetApp.openById(data_spreadsheetId).getActiveSheet();
  var data = data_sheet.getDataRange().getValues();
  var headers = data[0];
  
  var n_col = 0;
  for (var key in headers) {
      if (headers[key].trim() !== '') {
          n_col++;
      }
  }

  for (var i = 1; i < data.length; i++) {
    var form = FormApp.openById(formIDs[i-1]);
    form.setTitle(data[i][0]); // The first column is the form name
    
    for (var j = 1; j < n_col; j++) {
      if (data[i][j] !== '') {
        var sectionHeader = form.addSectionHeaderItem();
        sectionHeader.setTitle(headers[j])
        sectionHeader.setHelpText(data[i][j]);
        Logger.log('Populated form ' + i + ": field " + j)
      }
    }
    Logger.log('Populating form ' + i + " with questions...")

    form.addTextItem().setTitle("axis_of_evaluation_1").setRequired(true);
    form.addListItem().setTitle("axis_1_weight").setChoiceValues(['1','2','3']).setRequired(true)
    form.addParagraphTextItem().setTitle("axis_1_perfect").setHelpText('Will assign +2 points if ALL information below is provided.').setRequired(true)
    form.addParagraphTextItem().setTitle("axis_1_fair").setHelpText('Will assign +1 point if ALL information below is provided.').setRequired(true)
    form.addParagraphTextItem().setTitle("axis_1_wrong").setHelpText('Will assign -1 point if ANY information below is provided.').setRequired(true)

    form.addTextItem().setTitle("axis_of_evaluation_2").setRequired(true);
    form.addListItem().setTitle("axis_2_weight").setChoiceValues(['1','2','3']).setRequired(true)
    form.addParagraphTextItem().setTitle("axis_2_perfect").setHelpText('Will assign +2 points if ALL information below is provided.').setRequired(true)
    form.addParagraphTextItem().setTitle("axis_2_fair").setHelpText('Will assign +1 point if ALL information below is provided.').setRequired(true)
    form.addParagraphTextItem().setTitle("axis_2_wrong").setHelpText('Will assign -1 point if ANY information below is provided.').setRequired(true)

    form.addTextItem().setTitle("axis_of_evaluation_3").setRequired(true);
    form.addListItem().setTitle("axis_3_weight").setChoiceValues(['1','2','3']).setRequired(true)
    form.addParagraphTextItem().setTitle("axis_3_perfect").setHelpText('Will assign +2 points if ALL information below is provided.').setRequired(true)
    form.addParagraphTextItem().setTitle("axis_3_fair").setHelpText('Will assign +1 point if ALL information below is provided.').setRequired(true)
    form.addParagraphTextItem().setTitle("axis_3_wrong").setHelpText('Will assign -1 point if ANY information below is provided.').setRequired(true)

    form.addTextItem().setTitle("axis_of_evaluation_4").setRequired(true);
    form.addListItem().setTitle("axis_4_weight").setChoiceValues(['1','2','3']).setRequired(true)
    form.addParagraphTextItem().setTitle("axis_4_perfect").setHelpText('Will assign +2 points if ALL information below is provided.').setRequired(true)
    form.addParagraphTextItem().setTitle("axis_4_fair").setHelpText('Will assign +1 point if ALL information below is provided.').setRequired(true)
    form.addParagraphTextItem().setTitle("axis_4_wrong").setHelpText('Will assign -1 point if ANY information below is provided.').setRequired(true)

    form.addTextItem().setTitle("axis_of_evaluation_5").setRequired(true);
    form.addListItem().setTitle("axis_5_weight").setChoiceValues(['1','2','3']).setRequired(true)
    form.addParagraphTextItem().setTitle("axis_5_perfect").setHelpText('Will assign +2 points if ALL information below is provided.').setRequired(true)
    form.addParagraphTextItem().setTitle("axis_5_fair").setHelpText('Will assign +1 point if ALL information below is provided.').setRequired(true)
    form.addParagraphTextItem().setTitle("axis_5_wrong").setHelpText('Will assign -1 point if ANY information below is provided.').setRequired(true)

    form.addTextItem().setTitle("axis_of_evaluation_6").setRequired(false);
    form.addListItem().setTitle("axis_6_weight").setChoiceValues(['0','1','2','3']).setRequired(false)
    form.addParagraphTextItem().setTitle("axis_6_perfect").setHelpText('Will assign +2 points if ALL information below is provided.').setRequired(false)
    form.addParagraphTextItem().setTitle("axis_6_fair").setHelpText('Will assign +1 point if ALL information below is provided.').setRequired(false)
    form.addParagraphTextItem().setTitle("axis_6_wrong").setHelpText('Will assign -1 point if ANY information below is provided.').setRequired(false)

    form.addTextItem().setTitle("axis_of_evaluation_7").setRequired(false);
    form.addListItem().setTitle("axis_7_weight").setChoiceValues(['0','1','2','3']).setRequired(false)
    form.addParagraphTextItem().setTitle("axis_7_perfect").setHelpText('Will assign +2 points if ALL information below is provided.').setRequired(false)
    form.addParagraphTextItem().setTitle("axis_7_fair").setHelpText('Will assign +1 point if ALL information below is provided.').setRequired(false)
    form.addParagraphTextItem().setTitle("axis_7_wrong").setHelpText('Will assign -1 point if ANY information below is provided.').setRequired(false)

    form.addTextItem().setTitle("axis_of_evaluation_8").setRequired(false);
    form.addListItem().setTitle("axis_8_weight").setChoiceValues(['0','1','2','3']).setRequired(false)
    form.addParagraphTextItem().setTitle("axis_8_perfect").setHelpText('Will assign +2 points if ALL information below is provided.').setRequired(false)
    form.addParagraphTextItem().setTitle("axis_8_fair").setHelpText('Will assign +1 point if ALL information below is provided.').setRequired(false)
    form.addParagraphTextItem().setTitle("axis_8_wrong").setHelpText('Will assign -1 point if ANY information below is provided.').setRequired(false)

    form.addTextItem().setTitle("axis_of_evaluation_9").setRequired(false);
    form.addListItem().setTitle("axis_9_weight").setChoiceValues(['0','1','2','3']).setRequired(false)
    form.addParagraphTextItem().setTitle("axis_9_perfect").setHelpText('Will assign +2 points if ALL information below is provided.').setRequired(false)
    form.addParagraphTextItem().setTitle("axis_9_fair").setHelpText('Will assign +1 point if ALL information below is provided.').setRequired(false)
    form.addParagraphTextItem().setTitle("axis_9_wrong").setHelpText('Will assign -1 point if ANY information below is provided.').setRequired(false)

    form.addTextItem().setTitle("axis_of_evaluation_10").setRequired(false);
    form.addListItem().setTitle("axis_10_weight").setChoiceValues(['0','1','2','3']).setRequired(false)
    form.addParagraphTextItem().setTitle("axis_10_perfect").setHelpText('Will assign +2 points if ALL information below is provided.').setRequired(false)
    form.addParagraphTextItem().setTitle("axis_10_fair").setHelpText('Will assign +1 point if ALL information below is provided.').setRequired(false)
    form.addParagraphTextItem().setTitle("axis_10_wrong").setHelpText('Will assign -1 point if ANY information below is provided.').setRequired(false)

    form.addMultipleChoiceItem().setTitle("include_in_the_benchmark").setChoiceValues(['YES', 'NO']).setRequired(true)
    
    Logger.log('Finished populating form no. ' + i)
  }
}