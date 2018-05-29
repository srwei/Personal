Problem Set 2 HMM part 1 README file

The file HMM1.py takes a text file of words, number of states, and VerboseFlag(True or False) and outputs a text file of each of the words and their respective string probability and plog, followed by the sum of the plogs of all the words. The format will be:

word        string probability       plog
sum of plogs

Directions on running the program:

	First use the terminal and navigate to the location of both HMM1.py and the text file. Type ls into the directory to check if they are both there. For this assignment, we are using two states, and the output will only include the final word string probabilities and plogs, not the alpha/beta steps (setting VerboseFlag as False). Then in the terminal command line, type:

		python3 HMM1.py 'TEXTFILE.txt' num_states True/False

	Replace 'TEXTFILE.txt' with the text file of words, num_states as the number of states, and True/False as False to not print the alpha/beta steps. In the case of the PSet, the command line will be 

		python3 HMM1.py 'english1000.txt' 2 False

	This will have created a text file named 'strings_plogs.txt' of the words and their plogs in the same directory. 

Summary of Results:

	Each of the word plogs are between 10-35 (depends on randomization). Typically, the shorter words will have a smaller plog. The sum of plogs will help give a good indicator of how accurate our model is. 