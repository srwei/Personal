import csv
import sys

#filepath = "dict.txt"

def final(filename):
	alphabetizing = returnhash(filename)
	alphabetized_dict = ordered_anagrams_by_size(alphabetizing)
	ordered_output = ordered_anagrams_by_length(alphabetized_dict)
	with open('anagrams_output.csv', 'w') as f:
		writer = csv.writer(f)
		writer.writerows(ordered_output)


def returnhash(filename):
	hash_table = {}
	with open(filename, 'r') as f:
		for word in f:
			word = word.rstrip('\n')
			word = word.lower()
			if len(word) >= 8:
				key = sorted(list(word))
				key = ''.join(key)
				if key in hash_table:
					if word not in hash_table[key]:
						hash_table[key].append(word)
				else:
					hash_table[key] = [word]

	return(hash_table)

def ordered_anagrams_by_size(hash_table):
	sorted_anagrams = {}
	for key in hash_table:
		if len(hash_table[key]) > 1:
			size = len(hash_table[key])
			if size in sorted_anagrams:
				sorted_anagrams[size].append(hash_table[key])
			else:
				sorted_anagrams[size] = [hash_table[key]]
	sorted_anagrams = dict(sorted(sorted_anagrams.items()))
	return sorted_anagrams

def ordered_anagrams_by_length(sorted_anagrams):
	anagrams_list = []
	for size in sorted_anagrams:
		for anagram in sorted_anagrams[size]:
			length = len(anagram[0])
			anagram.insert(0, length)
	for size in sorted_anagrams:
		sorted_anagrams[size] = sorted(sorted_anagrams[size], key=lambda x: x[0])
	for size in sorted_anagrams:
		for anagram in sorted_anagrams[size]:
			anagrams_list.append(anagram[1:])

	return anagrams_list

if __name__ == '__main__':
	if len(sys.argv) > 1:
		final(sys.argv[1])







