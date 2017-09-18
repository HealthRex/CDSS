// Query String parsing
// chenjh@uci.edu

// By including this to your HTML file, you can then call
//  getReqParam to get any request parameters that were in the
//  query string of the URL

var requestParams;

// Automatically called to initialize the requestParams object
//  with the names and values of all the query string parameters
//  that this pages URL request contained
function initializeParamList( searchStr )
{
	if ( !searchStr )
	{	// None provided, get from URL and remove leading '?' char
		searchStr = window.location.search.substring(1);
	}

    // Split into sets of name, value pairs
    requestParams = searchStr.split('&');
    for( var i=0; i < requestParams.length; i++ )
    {
        // Split names from values
        requestParams[i] = requestParams[i].split('=');
        requestParams[i].name  = requestParams[i][0];
        requestParams[i].value = requestParams[i][1];
    }
}
initializeParamList();

// Lookup in the requestParams array for the paramName supplied
//  and return the matching value. If not found, returns null
function getReqParam( paramName )
{
    for( var i=0; i < requestParams.length; i++ )
    {
        if ( requestParams[i].name == paramName )
            return requestParams[i].value;
    }
    return null;
}
