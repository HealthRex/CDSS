/**
 * Change text highlighting to focus on the selected question
 */
function checkQuestion(questionCheckField)
{
	questionCheckField.checked = !questionCheckField.checked;	// Expect this to be toggled again row click, so cancel out the confusion
}
function checkQuestionByName( questionName, iRecord )
{
	// Default to first form on the page, must go look for the field
	var theForm = document.forms[0];
	var questionCheckField;
	// Manually match checkbox selection	
	var checkOps = theForm.elements['questionCheck.'+iRecord];
	if ( checkOps.length )
	{
		for( var i=0; i < checkOps.length; i++ )
		{
			if (checkOps[i].value == questionName)
			{
				questionCheckField = checkOps[i];
			}
		}
	}
	else	// Single element
	{
		if ( checkOps.value == questionName)
		{
			questionCheckField = checkOps;
		}
	}
	questionCheckField.checked = !questionCheckField.checked;

	highlightQuestion( questionCheckField, iRecord );
}
/**
 * Set color / highlight of a question row and relevant source text
 */
function highlightQuestion( questionCheckField, iRecord )
{
	var questionName = questionCheckField.value;
	var displayFieldName = "questionName."+iRecord+"."+questionName;
	var questionNameDisplay = document.getElementById(displayFieldName);
	questionNameDisplay.style.backgroundColor = ( questionCheckField.checked ? '#ffff00' : '#ffffff' );
	
	// Now look for anchor links of relevant sections of source text related to this question.  
	var textLinks = questionRelatedTextLinks( iRecord );
	var foundMatchingLink = false;
	for( var i=0; i < textLinks.length; i++)
	{
		var isMatchingLink = (textLinks[i].name.indexOf(questionName) >= 0);
		if ( isMatchingLink )
		{
			if ( questionCheckField.checked && !foundMatchingLink )
			{	// First matching link.  Bring browser focus to this item
				foundMatchingLink = true;
				textLinks[i].focus();
			}
			textLinks[i].style.backgroundColor = ( questionCheckField.checked ? '#ffff00' : '#ffffff' );
		}
	}
}
/**
 * Find all of the text links (anchor tags) related to theis record.
 */
function questionRelatedTextLinks( iRecord )
{
	var textLinks = new Array();
	//	Have to iterate through all links for now and work off of naming conventions
	//	May store associative array / dictionary links back in window level object to save time later
	for( var i=0; i < document.links.length; i++ )
	{
		if ( parseInt(document.links[i].name.split(".")[0]) == iRecord )
		{
			textLinks.push( document.links[i] );
		}
	}
	return textLinks;
}

/**
 * Batch function to set multiple question names
 */
function setQuestionsByName( questionNamesStr, iRecord )
{
	// Default to first form on the page, must go look for the field
	var theForm = document.forms[0];
	var questionNames = questionNamesStr.split(",");
	// Manually match checkbox selection	
	var checkOps = theForm.elements['questionCheck.'+iRecord];
	if ( checkOps.length )
	{
		for( var i=0; i < checkOps.length; i++ )
		{
			checkOps[i].checked = (questionNames.indexOf(checkOps[i].value) >= 0);
			highlightQuestion( checkOps[i], iRecord );
		}
	}
	else	// Single element
	{
		checkOps.checked = (questionNames.indexOf(checkOps.value) >= 0);
		highlightQuestion( checkOps, iRecord );
	}
}