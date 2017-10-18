//------------- Begin define Color class and helpers -------------------//
/*
    Jonathan H. Chen
   Created:         August 19, 1998
   Last Modified:   March 11, 1999
*/
  //------------- Required helper functions --------------------------//

   //Postcondition: Returns index in array of first found entry of argument
   //               coming on or after the start index (default=0) entry,
   //               else if not found, returns -1
   function Array_indexOf( key, start )
   {
      if ( !start ) start = 0;
      for( var walk = start; walk < this.length; walk++ )
         if ( this[walk] == key ) return walk;
      return -1;
   }
   Array.prototype.indexOf = Array_indexOf;

   //Define hexadecimal values for Math class
   Math.hexadec = new Array(16);
   for( var hd=0; hd < 10; hd++ ) Math.hexadec[hd] = hd + '';
   Math.hexadec[10] = 'a'; Math.hexadec[11] = 'b';
   Math.hexadec[12] = 'c'; Math.hexadec[13] = 'd';
   Math.hexadec[14] = 'e'; Math.hexadec[15] = 'f';

   //Precondition:  Parsable int argument
   //Postcondition: Returns string of hexadecimal representation
   //               with appended 0s for min length = 2
   function Math_dec2hex( dec )
   {
      dec = parseInt( dec );
      var hex = '';
      while ( dec > 0 )
      {
         hex = this.hexadec[ this.floor( dec % 16 ) ] + hex;
         dec = this.floor( dec / 16 );
      }
      while ( hex.length < 2 )
         hex = '0' + hex;
      return '0x' + hex;
   }
   Math.dec2hex = Math_dec2hex;

   //Precondition:  Argument can be interpreted as a string with first
   //               length (default=2) chars representing hexadecimal number
   //Postcondition: Returns integer equivalent of hexadecimal argument
   function Math_hex2dec( hex, length )
   {
      if ( !length ) length = 2;
      if ( (hex + '').substring(0,2) == '0x' )
         return parseInt( hex.substring(0,length+2) );
      hex = (hex + '').substring(0,length);
      var dec = 0;
      for ( var pos = 0; pos < length; pos++ )
      {
         dec *= 16;
         if ( this.hexadec.indexOf( hex.charAt(pos) ) != -1 )
            dec += this.hexadec.indexOf( hex.charAt(pos) );
      }
      return dec;
   }
   Math.hex2dec = Math_hex2dec;

  //------------- End Required helper functions -----------------------//
  //---------------- Begin define Color Class -------------------------//

   //Precondition:  Arguments are parsable to integers
   //               Designate hexadec numbers with prefix 0x as in 0xff
   //               Or takes single argument in string format, i.e. "#00ffff"
   //Postcondition: Creates new Color object and assigns RGB values to
   //               object according to args, with default = 0
   function Color( Rval, Gval, Bval )
   {
      this.Red; this.Green; this.Blue;

      if ( (Rval + '').charAt(0) == '#' )
         this.setColor( Rval );
      else
      {
         this.Red = parseInt( Rval );
         if ( !this.Red      ) this.Red = 0;
         if ( this.Red < 0   ) this.Red = 0;
         if ( this.Red > 255 ) this.Red = 255;
         this.Green = parseInt( Gval );
         if ( !this.Green      ) this.Green = 0;
         if ( this.Green < 0   ) this.Green = 0;
         if ( this.Green > 255 ) this.Green = 255;
         this.Blue = parseInt( Bval );
         if ( !this.Blue      ) this.Blue = 0;
         if ( this.Blue < 0   ) this.Blue = 0;
         if ( this.Blue > 255 ) this.Blue = 255;
      }
   }

   //Create and discard object to auto-generate prototype object
   new Color();

   //Postcondition: Returns string equivalent of three RGB values in this as
   //               Red Green Blue hexadecimal values, with '#' prefix.
   function Color_toString()
   {
      var strColor  = '#';

      strColor += Math.hexadec[ Math.floor( this.Red   / 16 ) ];
      strColor += Math.hexadec[ Math.floor( this.Red   % 16 ) ];
      strColor += Math.hexadec[ Math.floor( this.Green / 16 ) ];
      strColor += Math.hexadec[ Math.floor( this.Green % 16 ) ];
      strColor += Math.hexadec[ Math.floor( this.Blue  / 16 ) ];
      strColor += Math.hexadec[ Math.floor( this.Blue  % 16 ) ];

      return strColor;
   }
   Color.prototype.toString = Color_toString;
   Color.prototype.valueOf  = Color_toString;

   //Postcondition: Returns the value in decimal, or hexadecimal
   //               string format if format == '0x', of the particular
   //               RGB value (i.e. 255 or 0xff)
   function Color_getRed( format )
   {
      if ( (format+'').substring(0,2) == '0x' )
         return Math.dec2hex( this.Red );
      else
         return this.Red;
   }
   Color.prototype.getRed = Color_getRed;

   function Color_getGreen( format )
   {
      if ( (format+'').substring(0,2) == '0x' )
         return Math.dec2hex( this.Green );
      else
         return this.Green;
   }
   Color.prototype.getGreen = Color_getGreen;

   function Color_getBlue( format )
   {
      if ( (format+'').substring(0,2) == '0x' )
         return Math.dec2hex( this.Blue );
      else
         return this.Blue;
   }
   Color.prototype.getBlue = Color_getBlue;

   //Precondition:  newColor is in color string format, i.e. #00ffff
   //Postcondition: Sets appropriate RGB values corresponding to string.
   function Color_setColor( newColor )
   {
      newColor = newColor.substring( 1, 7 ); //Truncate '#' char
      var RVal, Gval, Bval;

      RVal = Math.hex2dec( newColor.substring(0,2) );
      GVal = Math.hex2dec( newColor.substring(2,4) );
      BVal = Math.hex2dec( newColor.substring(4,6) );

      if ( RVal > 255 ) RVal = 255;
      if ( RVal <  0  ) RVal = 0;
      this.Red = RVal;
      if ( GVal > 255 ) GVal = 255;
      if ( GVal <  0  ) GVal = 0;
      this.Green = GVal;
      if ( BVal > 255 ) BVal = 255;
      if ( BVal <  0  ) BVal = 0;
      this.Blue = BVal;
   }
   Color.prototype.setColor = Color_setColor;

   //Precondition:  Argument newColor is parseable to an int.
   //Postcondition: Specific RGB value is set to newColor amount
   function Color_setRed( newColor )
   {
      newColor = parseInt( newColor );
      this.Red = newColor;
   }
   Color.prototype.setRed = Color_setRed;

   function Color_setGreen( newColor )
   {
      newColor = parseInt( newColor );
      this.Green = newColor;
   }
   Color.prototype.setGreen = Color_setGreen;

   function Color_setBlue( newColor )
   {
      newColor = parseInt( newColor );
      this.Blue = newColor;
   }
   Color.prototype.setBlue = Color_setBlue;
//------------------ End define Color class -----------------------------//
