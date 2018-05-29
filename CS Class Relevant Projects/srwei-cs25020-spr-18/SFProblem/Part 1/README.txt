Problem Set 5 SFProblem Part 1 README file

The file sfproblem.py takes a text file of words and an integer minimum stem length and outputs 2 text files: one with the successor splits and another with the predecessor splits. 

Directions on running the program:

	First use the terminal and navigate to the location of both sfproblem.py and the text file. Type ls into the directory to check if they are both there. Because the textfile we are using is very large, it is more efficient to use bash to lowercase all the words in the file and then remove the duplicates. To do this, we use the following commands in the terminal:


		grep -v '#' english-encarta.dx1 |awk '{print $1}' > english-encarta.txt

		tr A-Z a-z < english-encarta.txt > lowercase-english-encarta.txt

		sort lowercase-english-encarta.txt | uniq > unique-english-encarta.txt

	
	By doing these three commands (assuming the original file is the english-encarta.dx1), we will have created 3 more new files in the directory. The last one is the one we will use, which is this case, is unique-english-encarta.txt. To use the program, the command will be:


		python3 sfproblem.py unique-english-encarta.txt 5


	We set K to 5, as that is the minimum stem length for this particular problem. This will have created two text files in the directory, named 'successor-splits.txt' and 'predecessor-splits.txt'

