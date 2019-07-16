= Dev Workshop =
Test First Development

== Learning Goals ==
- Unit test execution and debugging
- Test First Development example
- Python command-line processing tips
    - Data pipes (stdin, stdout, stderr)
- Further reading:
  http://agiledata.org/essays/tdd.html

== Preconditions ==
- Python *2.7* installed and executable from command-line / terminal
- Git installed so able to download / clone code repository

== Workshop Steps ==
- Download copy of the code repository
    git clone https://github.com/HealthRex/CDSS.git
       or if you just need to update existing copy...
    git pull

- Go to the CDSS/scripts/DevWorkshop/ directory

- Verify you can run the example ApplicationModule and respective test
    python ApplicationModule.py -w 3 sampleData/abstractLines.txt results/abstractWords.txt
		The above should create a results.txt file with a sample of words extracted from the abstractLines.txt file.
    
    python TestApplicationModule.py
		The above is expected to yield a "failed" test, but just make sure it doesn't yield a compiler error, or python dependency issue, etc.

- Review the ApplicationModule
	- Example usage of setting up a main function and OptionParser to enable command-line interaction
	- Example of outputting the argv as a comment line in the output file, to make it easier to retrace/reproduce your data pipelines. This is the meta-data that allows you to reconstruct where your (intermediate) data files came from, without having to come up with excessively detailed and unreliable filenames.

- Review the TestApplicationModule
	- Example suite function to tell the test runner where to find test to run (default is any method that starts with "test").
	- Standard setUp and tearDown to run before and after each test within the test class.
	- Example test_extractWordsByIndex test, following basic repeated structure: Setup test input, run application code on input, verify (assert) output matches expected results.

- Test and Debug
	- Figure out why the test_extractWordsByIndex fails and modify the code until it passes.
	- When there is an error/failure, beware the urge to change the test to match the application's behavior. Unless you're sure the application is the one that is correct... which you can't be sure of unless you've run some tests on it.

- Test First Development Example
	- Try adding another application function and test case to these files, such as the Fibonacci or cooccurrence counting ideas.
	- Test First Dev: 
		(1) Write the application function stub + documentation of what you want it to do, but NOT the actual implementation. 
		(2) Write the unit test function which asserts expected output if your application function does what you want it to (again, BEFORE you've implemented the actual application code). Forces you to effectively design your code API (application programming interface, i.e., function names, parameters, return values).
		(3) Run the unit test above, expecting it to fail (since application code not written), but verifies you stitched the API calls together correctly. Mimics how easy/hard it will be for a user of your code to follow.
		(4) Implement the application code, and run the unit test, and continue iterating until your unit tests pass.

- Automated Regression Testing Empowers Bold Changes in Implementation
	- If you got the Fibonacci example working, including a unit test to verify, try running it against an example input value of 50 or more (i.e., you'll be calculating the 50th Fibonacci value, or higher).
		For example, copy and paste one of the sample input text lines multiple times over until it is at least 50 words long.
	- Depending on how you implemented the Fibonacci application code, it is highly likely that the above will never finish (you'll have to Ctrl-C to cancel the process).
	- Try implementing the application code a different way, while confidently being able to re-run your existing unit test to verify that whatever changes you make will still produce valid results (but hopefully much faster).
