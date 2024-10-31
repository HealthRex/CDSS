function run_all() {
  Logger.log('--- COPY FORMS ---')
  createFormCopies()
  Logger.log('--- POPULATE FORMS ---')
  populateForms()
  Logger.log('--- LINK RESPONSES TO SPREADSHEET ---')
  linkFormsToSpreadsheet()
  Logger.log('--- PREFILL THE FORMS ---')
  createPrefilledUrl()
}