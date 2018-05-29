Problem Set 3 HMM part 2 README file

The file HMM2.py takes a text file of words, number of states, and VerboseFlag(True or False) and outputs a text file of the expected counts for each letter in the text file. The format of the text will be:

letter         from_state         to_state       expected_counts

Directions on running the program: 

	First use the terminal and navigate to the location of both HMM2.py and the text file. Type ls into the directory to check if they are both there. For this assignment, we are using two states, and the ouput will only include the expected counts for each letter in the unique from_state and to_state. Then in the terminal command line, type:

		python3 HMM2.py 'TEXTFILE.txt' num_states True/False

	Replace 'TEXTFILE.txt' with the text file of words, num_states as the numer of states, and True/False as False to not print all the steps and sum of 1 confirmation. In the case of the PSet, the command will be:

		python3 HMM2.py 'english1000.txt' 2 False

	This will have created a text file named 'expected_counts.txt' of the expected counts in the same directory.

	Summary of Results:

		Each letter's expected soft counts sums up to the total number of words that start with that letter. 

