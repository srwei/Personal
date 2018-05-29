Problem Set 6 SFProblem Part 2 README file

The file sfproblem2.py takes a text file of words and an integer minimum stem length and outputs 2 text files that contain the top 20 signatures, number of occurances in stems, and 3 example stems (one for 'english1000.txt' and one for the English Encarta wordset)

Directions on running the program:

	First use the terminal and navigate to the location of both sfproblem2.py and the text files. Type ls into the directory to check if they are all there. Because the textfile we are using is very large, it is more efficient to use bash to lowercase all the words in the file and then remove the duplicates. To do this, we use the following commands in the terminal:


		grep -v '#' english-encarta.dx1 |awk '{print $1}' > english-encarta.txt

		tr A-Z a-z < english-encarta.txt > lowercase-english-encarta.txt

		sort lowercase-english-encarta.txt | uniq > unique-english-encarta.txt

	
	By doing these three commands (assuming the original file is the english-encarta.dx1), we will have created 3 more new files in the directory. The last one is the one we will use, which is this case, is unique-english-encarta.txt. To use the program for the 1K Signatures, go to the final function in sfproblem2.py and change both write files to the ones with the 'english1000.txt' file. We are using 5 as the minimum stem length. Run this in the terminal:


		python3 sfproblem2.py english1000.txt 5

	Then, to get the EnglishSignatures text file, change the write file lines in sfproblem2.py with the 'unique-english-encarta.txt' file. Run this in the terminal:

		python sfproblem2.py unique-english-encarta.txt 5

	Doing these two commands, and changing for the appropriate text file will result in two text files of top 20 signatures ('1K-Signatures.txt' and 'EnglishSignatures.txt') in the same directory

Summary

	It is not surprising that the most frequent signatures are ones like NULL=s, NULL=ly, NULL=ed, as they are common endings in English words to describe nouns, verbs, adjectives, etc. 

