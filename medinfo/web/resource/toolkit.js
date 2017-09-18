/**
 * Sentinel constant value to take place of empty strings
 */
var NULL_TAG = '<NULL>';

/**
 * String trimming functions (eliminates leading and trailing white-space)
 */
function strltrim() {
    return this.replace(/^\s+/,'');
}

function strrtrim() {
    return this.replace(/\s+$/,'');
}
function strtrim() {
    return this.replace(/^\s+/,'').replace(/\s+$/,'');
}

String.prototype.ltrim = strltrim;
String.prototype.rtrim = strrtrim;
String.prototype.trim = strtrim;

/**
 * Moves all of the selected items from the sourceList to the target List.
 * If targetList is null, will just delete the items from the sourceList
 * If copyOnly set, a copy will be left with the source list.
 */
function selectMoveCopy( sourceList, targetList, copyOnly )
{
    if ( targetList )
    {
        for( var i=0; i < sourceList.options.length; i++ )
        {
            var nextOp = sourceList.options[i];
            if ( nextOp.selected )
            {
                targetList.options.add( new Option( nextOp.text, nextOp.value ) );
            }
        }
    }

    if ( !copyOnly )
    {   // Iterate through backwards otherwise might miss some as delete and shift positions
        for( var i=sourceList.options.length-1; i > -1; i-- )
        {
            var nextOp = sourceList.options[i];
            if ( nextOp.selected )
            {
                sourceList.remove(i);
            }
        }
    }
}

/**
 * Sets the selected attribute of all options in the itemList to the
 * specified value (true/false).  This is handy if you want to select
 * all items in a list such that they will all be submitted with an HttpRequest
 */
function selectAllList( itemList, selectValue )
{
   for( var i=0; i < itemList.options.length; i++ )
   {
      itemList.options[i].selected = selectValue;
   }
}


/**
 * <p>Iterates through the field array and sets the value
 * to that specified for each.  If field is not an array,
 * but a single object, then just set that one.
 *
 * <p> Attribute is the field attribute to set.  Normally is just the field "value,"
 * but could specify something else like the fields "checked" or selected attribute.
 */
function setAll( field, value, attribute )
{
    setAllWhere( field, value, null, attribute );
}

/**
 * Like setAll, but only set the fields where the current
 * value is equal to the specified condition value.
 *
 * <p> Attribute is the field attribute to set.  Normally is just the field "value,"
 * but could specify something else like the fields "checked" or selected attribute.
 */
function setAllWhere( field, value, condition, attribute )
{
    if ( attribute == null ) { attribute = 'value'; }

    if ( field.length )
    {   // Is an array
        for( var i=0; i < field.length; i++ )
        {
            if ( condition == null || field[i].value == condition )
            {
                eval('field[i].'+ attribute +' = value');
            }
        }
    }
    else
    {
        if ( condition == null || field.value == condition )
        {
            eval('field.'+ attribute +' = value');
        }
    }
}

/**
 * Given an option select list field, 
 *  return all of the (selected) values in an array.
 * 
 * selectField - Object Reference to the select field
 * selectedOnly - Only include values for options that are selected.
 *                  Default to false, just include all option values
 */
function selectFieldValues( selectField, selectedOnly )
{
    var valueList = new Array();
    for ( var i=0; i < selectField.options.length; i++ )
    {
        if ( !selectedOnly || selectField.options[i].selected )
        {
            valueList.push( selectField.options[i].value );
        }
    }
    return valueList;
}

/**
 * Popup window with standard configuration.
 */
function stdPopup( url, queryString, width, height )
{   // Default values
    if (!width ) { width = 600; }
    if (!height) { height= 600; }

    var popup =
        window.open
        (   url+'?'+queryString,
            url.replace(/[^a-zA-Z]/,'_'),
            'width='+width+',height='+height+',resizable=yes,status=yes,toolbar=yes,scrollbars=yes'
        );
    //popup.caller = window.self;
    popup.focus();
}

/**
 * Close the current window (popup) and refresh the calling window
 * that opened this popup.
 * Requires that the calling window, when creating this popup,
 * added a reference in the popup to the caller like (popup.caller = self).
 *
 */
/* Forget it, this is unreliable.  If popup window's page changed (after a
 * form submit) the caller reference is gone too.
function returnToCaller(popup,noReload)
{
    if ( !noReload )
    {
        popup.caller.document.location.reload();
    }
    popup.caller.focus();
    popup.close();
}
 */

/**
 * Given a form, determines if any fields have changed
 * from the default values the page started with
 */
function changesMade( theForm )
{
    for( var i=0; i < theForm.elements.length; i++ )
    {
        var field = theForm.elements[i];
        if ( field.type == "select-one" || field.type == "select-multiple" )
        {   // Select lists require special attention to check default values
            for( var j=0; j < field.options.length; j++ )
            {
                if ( field.options[j].defaultSelected != field.options[j].selected )
                {
                    //alert(field.name+':'+field.options[j].value);
                    return true;
                }
            }
        }
        else
        {   // Most fields just have to do simple default value check
            if ( field.defaultValue != field.value )
            {
                //alert(field.name+':'+field.defaultValue);
                return true;
            }
        }
    }
    return false;
}

/**
 * Check if any of the form fields have changed.
 * If so, then alert the user with a message box
 * to confirm that they don't want to save those changes.
 */
function confirmNoSave( theForm, message )
{
    if ( changesMade(theForm) )
    {
        return window.confirm(message);
    }
    return true;
}

// Support functions for dynamic HTTP requests, adapted from
//  http://eloquentjavascript.net/chapter14.html

/**
 * General method for preparing request object for different browser environments
 */
function makeHttpRequest()
{
  try {return new XMLHttpRequest();}
  catch (error) {}
  try {return new ActiveXObject("Msxml2.XMLHTTP");}
  catch (error) {}
  try {return new ActiveXObject("Microsoft.XMLHTTP");}
  catch (error) {}

  throw new Error("Could not create HTTP request object.");
}

/**
 * Simple URL based HTTP request.
 * The success and failure parameters should be functions that
 *  will be called on the responseText of any requests that come back
 *  asynchronously from this function.
 * These can be defined in-line for convenience.  For example:
 *  ajaxRequest('dynamicData/InventoryTable.py', function(data){ invSpace.innerHTML = data; } );
 */
function ajaxRequest(url, successFunction, failureFunction)
{
  var request = makeHttpRequest();
  request.open("GET", url, true);
  request.send(null);
  request.onreadystatechange = function()
  {
    if (request.readyState == 4)
    {
      if (request.status == 200)
      {  successFunction(request.responseText); }
      else if (failureFunction)
      { failureFunction(request.status, request.statusText); }
    }
  };
}
