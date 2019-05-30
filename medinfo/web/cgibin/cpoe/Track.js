// When page is done loading
$(document).on('ready', function(){initTrackingBindings()})

// Store Trackers in page session (to avoid being lost across page updates)
// Below if-statement is a good place to make one-time initializations
if (sessionStorage.length == 0){
  sessionStorage.setItem('eventTracker', JSON.stringify(new Object())) // Track user action events
  sessionStorage.setItem('resultsTracker', JSON.stringify(new Object())) // Track results that come up
  sessionStorage.setItem('signedItemsTracker', JSON.stringify(new Object())) // Track signed items
  sessionStorage.setItem('lastButtonClicked', "") // Track last clicked button to use in state of results
  sessionStorage.setItem('listIdx', "0") // Track list index of results
  startTimer()
}
eventTracker = $.parseJSON(sessionStorage.getItem('eventTracker')) // Track user action events
resultsTracker = $.parseJSON(sessionStorage.getItem('resultsTracker')) // Track results that come up
signedItemsTracker = $.parseJSON(sessionStorage.getItem('signedItemsTracker')) // Track signed items
listIdxTracker = parseInt(sessionStorage.getItem('listIdx')) // Index of recommendation lists
// Store idx in appropriate input
console.log('loading recListIndex:' + listIdxTracker)

lastButtonClicked = ""

/**
* Save trackers to file
*/
function saveTrackers(){
  var data = new Object()
  data['startTime'] = sessionStorage.getItem('startTime')
  data['endTime'] = sessionStorage.getItem('endTime')
  data['eventTracker'] = sessionStorage.getItem('eventTracker')
  data['resultsTracker'] = sessionStorage.getItem('resultsTracker')
  data['signedItemsTracker'] = sessionStorage.getItem('signedItemsTracker')
  data['user'] = sessionStorage.getItem('user')
  data['patient'] = sessionStorage.getItem('patient')
  data_string = JSON.stringify(data)

  var encoded_data = "text/json;charset=utf-8," + encodeURIComponent(data_string)
  var a = document.createElement('a');
  a.href = 'data:' + encoded_data;
  a.download  = data['user'] + '_' + data['patient'] +'_data_v5.json';
  a.click()
  sessionStorage.clear()
}

/**
* Save trackers in window.name
* To be used with page is reloaded, to keep trackers persistent
*/
function setTrackers(){
  sessionStorage.setItem('eventTracker', JSON.stringify(eventTracker)) // Track user action events
  sessionStorage.setItem('resultsTracker', JSON.stringify(resultsTracker)) // Track results that come up
  sessionStorage.setItem('signedItemsTracker', JSON.stringify(signedItemsTracker)) // Track signed items
  sessionStorage.setItem('listIdx', listIdxTracker.toString()) // Track index of recommendation lists
}

/**
* Record beginning of test
*/
function startTimer(){
  startTime = Date.now()
  // console.log(startTime)
  sessionStorage.setItem('startTime', startTime)
}

/**
* Record ending of test
*/
function stopTimer(){
  endTime = Date.now()
  // console.log(endTime)
  sessionStorage.setItem('endTime', endTime)
}

/**
* Collect general case info (user info, patient info, etc.)
*/
function collectCaseInfo(){
  var simUser = $('input[type="hidden"][name="sim_user_id"]')
  // console.log(simUser.val())
  var simPatient = $('input[type="hidden"][name="sim_patient_id"]')
  // console.log(simPatient.val())
  sessionStorage.setItem('user', simUser.val().toString())
  sessionStorage.setItem('patient', simPatient.val().toString())
}

/*
* Initialize tracking bindings on page
*/
function initTrackingBindings(){
  collectCaseInfo()
  // Going back to setup page through top link ends test
  var home = $('.breadcrumb')
  home.on('click', function(event){
    // Let user confirm exit (and clearing of session)
    var exit = confirm("Exit and save user testing?")
    if (exit) {
      setTrackers()
      stopTimer()
      saveTrackers()
    } else {
      // If exit is cancelled, prevent page change
      event.preventDefault()
    }
  })

  var dataTable = $('#currentDataTableSpace')
  attachTimeChangeBindings()
  attachResultsReviewBindings()
  attachOrderBindings()
  attachNewOrderBindings()
  attachResultBindings()
  trackOrders()
  var elementsToObserve = new Object()
  elementsToObserve[dataTable] = attachResultsReviewBindings

  var mutationObserver = new MutationObserver(function(mutations) {
    attachResultsReviewBindings()
  })
  mutationObserver.observe(dataTable.get(0), {
    attributes: true,
    characterData: true,
    childList: true,
    subtree: true,
    attributeOldValue: true,
    characterDataOldValue: true
  })
}

/**
* Attach bindings to time forward/backward functionality
*/
function attachTimeChangeBindings(){
  var timeChangeButtons = $('.headingTable input[type="button"]')
  timeChangeButtons.on('click', function(){
    var state = new Object()
    var timeChange = $(this).val()
    incrementCounter(timeChange, state)
    // Changing time reloads entire page, must save events!
    setTrackers()
  })
}

/**
* Attach bindings to results view
*/
function attachResultsReviewBindings(){
  // Notes
  var viewNotes = $('input[type="button"][value="Notes"]')
  viewNotes.unbind('click')
  viewNotes.on('click load', function(){
    var state = new Object()
    incrementCounter("Notes", state)
  })
  // Specific Notes
  var viewSpecificNotes = $('#currentDataTableSpace a')
  viewSpecificNotes.unbind('click')
  viewSpecificNotes.on('click', function(){
    var noteLinkText = this.text
    var state = new Object()
    state['linkText'] = noteLinkText
    incrementCounter("NoteContent", state)
  })
  // Results Review
  var viewResultsReview = $('input[type="button"][value="Results Review"]')
  viewResultsReview.unbind('click')
  viewResultsReview.on('click', function(){
    // Update lastButtonClicked
    lastButtonClicked = "ResultsReview"
    var state = new Object()
    incrementCounter("ResultsReview", state)
  })
  // Active Orders
  var viewActiveOrders = $('input[type="button"][value="Active Orders"]')
  viewActiveOrders.unbind('click')
  viewActiveOrders.on('click', function(){
    // Update lastButtonClicked
    lastButtonClicked = "ActiveOrders"
    var state = new Object()
    incrementCounter("ActiveOrders", state)
  })
  // Active Orders Removal
  var activeOrdersRemoval = $('input[type="button"][value="X"]')
  activeOrdersRemoval.unbind('click')
  activeOrdersRemoval.on('click', function(){
    // Update lastButtonClicked
    lastButtonClicked = "ActiveOrdersRemoval"
    var state = new Object()
    incrementCounter("ActiveOrdersRemoval", state)
  })
  // Order History
  var viewOrderHistory = $('input[type="button"][value="Order History"]')
  viewOrderHistory.unbind('click')
  viewOrderHistory.on('click', function(){
    // Update lastButtonClicked
    lastButtonClicked = "OrderHistory"
    var state = new Object()
    incrementCounter("OrderHistory", state)
  })
}

/**
* Attach bindings to New Orders view
*/
function attachOrderBindings(){
  // Search bar
  var orderSearch = $('input[type="text"][name="orderSearch"]')
  // Find Orders
  var findOrders = $('input[type="submit"][value="Find Orders"]')
  findOrders.on('click', function(){
    // Update lastButtonClicked
    lastButtonClicked = "FindOrders"
    var state = new Object()
    var searchQuery = orderSearch.val()
    state['searchQuery'] = searchQuery
    incrementCounter("FindOrders", state)
  })
  // Order Sets
  var orderSets = $('input[type="button"][value="Order Sets"]')
  orderSets.on('click', function(){
    // Update lastButtonClicked
    lastButtonClicked = "OrderSets"
    var state = new Object()
    var searchQuery = orderSearch.val()
    state['searchQuery'] = searchQuery
    incrementCounter("OrderSets", state)
  })
  // Diagnoses
  var diagnoses = $('input[type="button"][value="Diagnoses"]')
  diagnoses.on('click', function(){
    // Update lastButtonClicked
    lastButtonClicked = "Diagnoses"
    var state = new Object()
    var searchQuery = orderSearch.val()
    state['searchQuery'] = searchQuery
    incrementCounter("Diagnoses", state)
  })
  // Sign Orders ** Resets entire patient frame!!!
  var signOrders = $('input[type="submit"][value="Sign Orders"]')
  signOrders.on('click', function(e){
    // Update lastButtonClicked
    lastButtonClicked = "SignOrders"
    var state = new Object()
    var searchQuery = orderSearch.val()
    // Get checked orders and add to state
    state['searchQuery'] = searchQuery
    // Save signed items
    storeSignedOrders()
    incrementCounter("SignOrders", state)
    // Save trackers before page reloads
    setTrackers()
  })
}

/**
* Basic counter that keeps track of times buttons have been clicked.
*/
function incrementCounter(eventName, state){
  var currTime = Date.now()
  state['eventTime'] = currTime

  if (eventTracker[eventName] == undefined) {
    eventTracker[eventName] = []
  }
  eventTracker[eventName].push(state)
  console.log(eventTracker)
}

/**
* Basic saving helper for storing new results and such
*/
function storeResults(results, state){
  var action = lastButtonClicked
  // results is list containing result items or object of named lists
  // Named list example: {'commonOrders': [items], 'specificOrders': [items]}
  var currTime = Date.now()
  state['storeTime'] = currTime

  var resultBlob = new Object()
  resultBlob['items'] = results
  resultBlob['state'] = state

  if (resultsTracker[action] == undefined){
    resultsTracker[action] = []
  }
  resultsTracker[action].push(resultBlob)
  // console.log(resultsTracker)
}

/**
* Store signed orders when "Sign Orders" clicked
*/
function storeSignedOrders(){
  var newSignedOrders = $('#newOrdersDetailSpace input:checked')
  // Search bar
  var orderSearch = $('input[type="text"][name="orderSearch"]')
  var state = new Object()
  var searchQuery = orderSearch.val()
  state['searchQuery'] = searchQuery

  var signedItems = []
  newSignedOrders.each(function(index){
    signedItems.push($(this).val() + '|' + $(this).attr('data-list') + '|' + $(this).attr('data-query') + '|' + $(this).attr('data-search-mode') + '|' + $(this).attr('data-list-idx'))
  })

  var currTime = Date.now()
  signedItemsTracker[currTime] = signedItems
  // console.log(signedItemsTracker)
}

/**
* Track seen and signed orders
*/
function trackOrders(){
  var resultsTable = $('#searchResultsTableSpace')
  var newOrdersTable = $('#newOrdersDetailSpace')

  // Track changes to new orders table
  var newOrdersObserver = new MutationObserver(function(mutations){
    attachNewOrderBindings()
  })
  newOrdersObserver.observe(newOrdersTable.get(0), {
    attributes: true,
    characterData: true,
    childList: true,
    subtree: true,
    attributeOldValue: true,
    characterDataOldValue: true
  })

  // Track changes to results checkboxes
  var resultInputsObserver = new MutationObserver(function(mutations) {
    attachResultBindings();
    // Record any new results

  })
  resultInputsObserver.observe(resultsTable.get(0), {
    attributes: true,
    characterData: true,
    childList: true,
    subtree: true,
    attributeOldValue: true,
    characterDataOldValue: true
  })
}

/**
* Attach bindings to New Orders section (selected order checkboxes and "sign")
*/
function attachNewOrderBindings(){
  var newOrders = $('#newOrdersDetailSpace input[type="checkbox"]')
  // Search bar
  var orderSearch = $('input[type="text"][name="orderSearch"]')
  // Remove any existing listeners on result inputs
  newOrders.unbind('change')
  newOrders.on('change', function(){
    var state = new Object()
    var searchQuery = orderSearch.val()
    state['searchQuery'] = searchQuery
    var itemInfo = $(this).val()
    // Item info for later analysis
    state['itemInfo'] = itemInfo
    // Determine what action was done on result item
    var selected = $(this).prop('checked')
    var action = selected ? 'selected' : 'unselected'
    state['action'] = action
    incrementCounter("NewOrderInteraction", state)
  })
}

/**
* Attach bindings to Results section (results checkboxes)
* Very similr to attachNewOrderBindings above
*/
function attachResultBindings(){
  var results = $('#searchResultsTableSpace input[type="checkbox"]')
  // Search bar
  var orderSearch = $('input[type="text"][name="orderSearch"]')
  // Remove any existing listeners on result inputs
  results.unbind('change')
  results.on('change', function(){
    var state = new Object()
    var searchQuery = orderSearch.val()
    state['searchQuery'] = searchQuery
    var itemInfo = $(this).val()
    // Item info for later analysis
    state['itemInfo'] = itemInfo
    // List container for later analysis
    var listContaining;
    if ($(this).parents('#resultSpace1').length > 0) {
      listContaining = 'resultSpace1'
    } else if ($(this).parents('#resultSpace2').length > 0) {
      listContaining = 'resultSpace2'
    } else {
      listContaining = 'non-recommender'
    }
    state['listContaining'] = listContaining
    // Determine what action was done on result item
    var selected = $(this).prop('checked')
    var action = selected ? 'selected' : 'unselected'
    state['action'] = action
    incrementCounter("ResultInteraction", state)
  })

  // Related links
  var related = $("a[href^='javascript:loadRelatedOrders']")
  // Remove any existing listeners on related links
  related.unbind('click')
  related.on('click', function() {
    // event.preventDefault();
    console.log($(this).attr('href').match(/\('([^)]+)'\)/)[1])
    // Update lastButtonClicked
    lastButtonClicked = "Related"
    var state = new Object()
    var query = $(this).attr('href').match(/\('([^)]+)'\)/)[1] // Item being explored
    state['searchQuery'] = query
    incrementCounter("Related", state)
  })
}

/**
* Keep track of results (items and their placement in results list)
* Collect items and preprocess them to be stored
*/
function recordNewResults(queryType){
  // Search bar
  var orderSearch = $('input[type="text"][name="orderSearch"]')
  // Common Orders list
  var commonOrdersView = $('#resultSpace1')
  var commonOrders = $('#resultSpace1 input[type="checkbox"]')
  // Specific Orders list
  var specificOrdersView = $('#resultSpace2')
  var specificOrders = $('#resultSpace2 input[type="checkbox"]')
  // General data list
  var dataTableView = $('#searchResultsTableSpace')
  var dataTable = $('#searchResultsTableSpace input[type="checkbox"]')
  // Current query (either from search or from clicking related link)
  var currentQuery = $('input[name="currentQuery"]')

  var results = new Object()

  // Store current index of results
  results['listIndex'] = listIdxTracker
  // Update result list index for next batch of results
  listIdxTracker = listIdxTracker + 1
  // If resultSpace2 and resultSpace1 present, collect lists separately
  if (queryType == 'resultSpace1'){
    // Get value of each input
    var commonOrdersValues = commonOrders.toArray().map(elem => elem.value)
    results['commonOrders'] = commonOrdersValues
  }
  else if (queryType == 'resultSpace2'){
    // Get value of each input
    var specificOrdersValues = specificOrders.toArray().map(elem => elem.value)
    results['specificOrders'] = specificOrdersValues
  }
  else {
    // Get value of each input
    var dataValues = dataTable.toArray().map(elem => elem.value)
    results['data'] = dataValues
  }

  // Store results
  var state = new Object()
  var searchQuery = currentQuery.val()
  state['searchQuery'] = searchQuery
  storeResults(results, state)
}
