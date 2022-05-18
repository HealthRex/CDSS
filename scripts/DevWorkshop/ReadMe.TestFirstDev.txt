= Dev Workshop =
Test First Development

== Learning Goals ==
- Unit test execution and debugging
- Test First Development example
- Python command-line processing tips
- Further reading:
  http://agiledata.org/essays/tdd.html

== Preconditions ==
- Python 3.6+ installed and executable from command-line / terminal
- Git installed so able to download / clone code repository

== Workshop Steps ==
- Download copy of the code repository
    git clone https://github.com/HealthRex/CDSS.git
       or if you just need to update existing copy...
    git pull

- Go to the CDSS/scripts/DevWorkshop/UnitTesting directory

- Verify you can run the example ApplicationModule and respective test
    python ApplicationModule.py -w 3 ../sampleData/abstractLines.txt abstractWords.3.txt
		The abstractLines.txt input file contains a bunch of research abstract text (one per line).
		Running the above should create an output file with a sample word for each input line.
    
    python TestApplicationModule.py
		Unit test to automatically verify the correct function of the respective application code.
		Running the above should yield a "failed" test at this point,
			but just make sure it doesn't yield a compiler error, or python dependency issue, etc.

- Review the ApplicationModule
	- Example usage of setting up a main function and OptionParser to enable command-line interaction
	- Example of outputting the argv and other metadata as a comment line in the output file, 
		to make it easier to retrace/reproduce your data pipelines. 
		This is the meta-data that allows you to reconstruct where your (intermediate) data files, 
		without having to come up with excessively detailed and unreliable filenames.

- Review the TestApplicationModule
	- Example suite function called from main driver code to tell the test runner where to find tests to run
		(default is any method that starts with "test").
	- Standard setUp and tearDown to run before and after each test within the test class.
		For example, creating temporary input files (and deleting them when done) or database contents, etc.
	- Example test_extractWordsByIndex test, following basic repeated structure: 
		(1) Setup test input, 
		(2) Run application code on input, 
		(3) Verify (assert) output matches expected results.

- Test and Debug
	- Figure out why the test_extractWordsByIndex fails and modify the code until it passes.
	- When there is an error/failure, beware the urge to change the test to match the application's behavior!
		Unless you're sure the application is the one that is correct... 
		which you can't be sure of unless you've (manually) run some tests on it.

- Test First Development Example
	- Try adding another application function and test case, such as the simple Fibonacci example.
	- Test First Dev: 
		(1) Write the application function stub + documentation of what you want it to do in English, 
			but NOT the actual implementation. 
		(2) Write the unit test function which asserts manually verified expected output given
			specific test input data if your application function does what it's supposed to do.
			Again, do this BEFORE you've implemented the actual application code.
			Forces you to effectively design your code API
			(application programming interface, i.e., function names, parameters, return values).
		(3) Run the unit test above, expecting it to fail (since application code not written),
			but verifies you stitched the API calls together correctly.
			Mimics how easy/hard it will be for a user of your code to follow.
		(4) Implement the application code, run the unit test, and iterate until your unit tests pass.

- Automated Regression Testing Empowers Bold Changes in Implementation
	- If you got the Fibonacci example working, including a unit test to verify,
		try running it from the command line for say, the 5th value:

		python ApplicationModule.py -f 5

	- Now try against an example input value of 50 or more
		(i.e., you'll be calculating the 50th Fibonacci value, or higher).

		python ApplicationModule.py -f 50

	- What happened? Depending on how you implemented the Fibonacci application code,
		it is highly likely that the above will never finish (you'll have to Ctrl-C to cancel the process).
	- Try implementing the application code a different way,
		while confidently being able to re-run your existing unit test 
		to verify that whatever changes you make will still produce valid results (but hopefully much faster).
