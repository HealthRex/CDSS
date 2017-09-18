// Date helper methods
// chenjh@uci.edu
// September 14, 2000
// --------------- Date Helper Methods ------------------ //

// Create prototype object
new Date();

Date.DAYS_PER_WEEK   = 7;
Date.WEEKS_PER_MONTH = 6;
Date.MONTHS_PER_YEAR = 12;

Date.days = new Array( Date.DAYS_PER_WEEK );
Date.days[0] = 'Sun';
Date.days[1] = 'Mon';
Date.days[2] = 'Tue';
Date.days[3] = 'Wed';
Date.days[4] = 'Thu';
Date.days[5] = 'Fri';
Date.days[6] = 'Sat';

Date.months = new Array( Date.MONTHS_PER_YEAR );
Date.months[0]  = 'January';
Date.months[1]  = 'February';
Date.months[2]  = 'March';
Date.months[3]  = 'April';
Date.months[4]  = 'May';
Date.months[5]  = 'June';
Date.months[6]  = 'July';
Date.months[7]  = 'August';
Date.months[8]  = 'September';
Date.months[9]  = 'October';
Date.months[10] = 'November';
Date.months[11] = 'December';

// For the Date object's current value, it returns the
//  number of days that the current month value selected has
function Date_daysPerMonth()
{
    var nextMonth = new Date( this.getTime() );
    nextMonth.setMonth( this.getMonth()+1 );

    nextMonth.setDate( 0 ); // 1 less than 1st of next month is last day of this

    return nextMonth.getDate();
}
Date.prototype.daysPerMonth = Date_daysPerMonth;

// Date to String format method
//  should be overwritten as needed to format your dates as desired
/*
// mmm dd, yyyy format
function Date_format()
{
    var formatString = '';

    formatString += Date.months[ this.getMonth() ].substring( 0, 3 );

    formatString += ' '

    if ( this.getDate() < 10 ) formatString += '0';
    formatString += this.getDate();

    formatString += ', '

    formatString += this.getFullYear();

    return formatString;
}
// mm/dd/yyyy format
function Date_format()
{
    var formatString = '';

    if ( this.getMonth()+1 < 10 ) formatString += '0';
    formatString += this.getMonth()+1;

    formatString += '/'

    if ( this.getDate() < 10 ) formatString += '0';
    formatString += this.getDate();

    formatString += '/'

    formatString += this.getFullYear();

    return formatString;
}
// yyyy-mm-dd format
function Date_format()
{
    var formatString = '';

    formatString += this.getFullYear();

    formatString += '-'

    if ( this.getMonth()+1 < 10 ) formatString += '0';
    formatString += this.getMonth()+1;

    formatString += '-'

    if ( this.getDate() < 10 ) formatString += '0';
    formatString += this.getDate();

    return formatString;
}
*/
// dd-mmm-yyyy format
function Date_format()
{
    var formatString = '';

    if ( this.getDate() < 10 ) formatString += '0';
    formatString += this.getDate();

    formatString += '-'

    formatString += Date.months[ this.getMonth() ].substring( 0, 3 );

    formatString += '-'

    formatString += this.getFullYear();

    return formatString;
}
Date.prototype.format = Date_format;

// String to Date parse method
//  should be overwritten as needed to parse your date strings as desired
/*
// mmm dd, yyyy format
function Date_valueOf( dateString )
{
    var dateValue = new Date();

    var monthString = dateString.substring(0,3);

    for( var i=0; i < Date.months.length; i++ )
    {
        if ( Date.months[i].substring(0,3).toUpperCase() == monthString.toUpperCase() )
            dateValue.setMonth(i);
    }
    if ( !isNaN( parseInt( dateString.substring(4,6) ) ) )
        dateValue.setDate( parseInt( dateString.substring(4,6) ) );
    if ( !isNaN( parseInt( dateString.substring(8,12) ) ) )
        dateValue.setFullYear( parseInt( dateString.substring(8,12) ) );

    return dateValue;
}
// mm/dd/yyyy format
function Date_valueOf( dateString )
{
    var dateValue = new Date();

    if ( !isNaN( parseInt( dateString.substring(0,2), 10 ) ) )
        dateValue.setMonth( parseInt( dateString.substring(0,2), 10 )-1 );
    if ( !isNaN( parseInt( dateString.substring(3,5), 10 ) ) )
        dateValue.setDate( parseInt( dateString.substring(3,5), 10 ) );
    if ( !isNaN( parseInt( dateString.substring(6,10), 10 ) ) )
        dateValue.setFullYear( parseInt( dateString.substring(6,10), 10 ) );

    return dateValue;
}
// yyyy-mm-dd format
function Date_valueOf( dateString )
{
    var dateValue = new Date();	dateValue.setDate(1);
    var today = new Date();

    if ( !isNaN( parseInt( dateString.substring(5,7), 10 ) ) )
    {
        dateValue.setMonth( parseInt( dateString.substring(5,7), 10 )-1 );
    }
    if ( !isNaN( parseInt( dateString.substring(8,10), 10 ) ) )
    {
        dateValue.setDate( parseInt( dateString.substring(8,10), 10 ) );
    }
    else
    {
    	dateValue.setDate( today.getDate() );
    }
    if ( !isNaN( parseInt( dateString.substring(0,4), 10 ) ) )
    {
        dateValue.setFullYear( parseInt( dateString.substring(0,4), 10 ) );
    }

    return dateValue;
}
*/
// dd-mmm-yyyy format
function Date_valueOf( dateString )
{
    // Start with contrived date, not today, or else risk bad behavior when 
    //  say, today is 10/31 and set month to November, but November has no 31st day
    var dateValue   = new Date(); dateValue.setDate(1);
    var today       = new Date();

    if ( !isNaN( parseInt( dateString.substring(7,11) ) ) )
    {
        dateValue.setFullYear( parseInt( dateString.substring(7,11) ) );
    }
    else
    {
        dateValue.setFullYear(today.getFullYear())
    }

    var monthString = dateString.substring(3,6);
    for( var i=0; i < Date.months.length; i++ )
    {
        if ( Date.months[i].substring(0,3).toUpperCase() == monthString.toUpperCase() )
        {
            dateValue.setMonth(i);
            monthString = "blah";
        }
    }
    if ( monthString != "blah" )
    {   // No valid month value found, default to current month
        dateValue.setMonth(today.getMonth())
    }

    if ( !isNaN( parseInt(dateString.substring(0,2), 10) ) )
    {
        dateValue.setDate( parseInt(dateString.substring(0,2), 10) );
    }
    else
    {
        dateValue.setDate(today.getDate())
    }
    return dateValue;
}
Date.valueOf = Date_valueOf;

// --------------- Date Helper Methods ------------------ //
