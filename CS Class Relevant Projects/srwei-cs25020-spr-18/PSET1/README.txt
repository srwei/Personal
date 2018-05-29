Problem Set 1 Anagrams ReadMe File

The file pset1.py takes a text file of words and outputs a csv file of the anagrams in the original file ordered first by size of anagrams and then the length of the words. It uses the Python virtual dictionary to keep track of the discovered anagrams. 

Direction on running the program:

	First use the terminal and navigate to the location of both the pset1.py and the text file. Type ls into the directory to check if they are both there. Then in the terminal command line, type:

		python3 pset1.py 'TEXTFILE.txt'

	Replace 'TEXTFILE.txt' with the text file of words. In the case of the PSet, the command line will be 

		python3 pset1.py 'dict.txt'

	This will have created a csv file named 'anagrams_output.csv' of the ordered anagrams in the same directory. 

Summary of result:

	There were a total of 5,998 anagrams. The size of the anagrams ranged from 2 to 7, although there weren't any anagrams with the size 6. The majority of anagrams had a size of 2 and 3. From observation, it also seems like most anagrams contain the same prefixes/suffixes with differences in the rest of the word. 

