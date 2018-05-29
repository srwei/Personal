Problem Set 4 HMM part 3 README file

The file HMM3.py takes a text file of words, number of states, and VerboseFlag(True or False) and outputs a text file of the 25 maximization results of local maxima using each of the various starting A-parameters. 

Directions on running the program:

	First use the terminal and navigate to the location of both HMM3.py and the text file. Type ls into the directory to check if they are both there. For this assignment, we are using two states, and the ouput will only include final maximization output for the 25 distinct runs of various A-parameters. Then in the terminal command line, type:

		python3 HMM3.py 'TEXTFILE.txt' num_states True/False

	Replace 'TEXTFILE.txt' with the text file of words, num_states as the numer of states, and True/False as False to not print all the steps of maximizing the parameters A, B, and Pi. In the case of the PSet, the command will be:

		python3 HMM3.py english1000.txt 2 False

	This will have created a text file named 'maximization_results.txt' of the maximization output in the same directory.

Summary of Results:

	After looking at the various local maxima in the 25 distinct A-parameters, it seems that the most accurate model for distinguishing vowels and consonants was when the starting transition probabilities was:

		0 to 0: 0.3
		0 to 1: 0.7
		1 to 0: 0.5
		1 to 1: 0.5

	At the local maxima, the transition probabilities seems to favor the cross states, increases in 0 to 1 and 1 to 0 transitions. Looking at the Log ratio of the emissions, all of the vowels and '#' and 'x' were found on the state 1 (negative log ratio) side. This shows that this model was very accurate in finding vowels compared to the other letters. 

	The pi probabilities ended up being highly favored to state 0, being 0.9944. This makes sense, as most of the occurance of vowels probably does not occur at the beginning of words, but rather after consonants (higher cross state transition probabilities). This change in pi probabilities was seen in almost all of the different runs through iterations. 
