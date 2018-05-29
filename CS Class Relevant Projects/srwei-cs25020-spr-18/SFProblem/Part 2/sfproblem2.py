import sys
import random

def final(text_file, position):

	wordlist = file_to_list(text_file, position, reverse=False)
	back_words = file_to_list(text_file, position, reverse=True)
	
	left_to_right = word_split(wordlist, position)
	lexicon = getLexicon(left_to_right)
	lexicon = update_lexicon(lexicon)

	signatures = {}
	signatures_count = {}
	for stem in lexicon:
		signature = lexicon[stem]
		if signature not in signatures:
			signatures[signature] = [stem]
			signatures_count[signature] = 1
		else:
			signatures[signature].append(stem)
			signatures_count[signature] += 1

	signatures_count = sorted(signatures_count.items(), key=lambda x: x[1], reverse=True)
	
	#Change these two inputs here, for either the 1K Signatures or the English Encarta Signatures
	with open('1K-Signatures.txt', 'w') as f:
	#with open('EnglishSignatures.txt', 'w') as f:
		f.write('-'*35 + '1K Signatures' + '-'*35 + '\n')
		#f.write('-'*35 + 'English Signatures' + '-'*35 + '\n')
		for i, stem in enumerate(signatures_count[:20]):
			count = stem[1]
			suffix_number = len(signatures[stem[0]])
			if suffix_number < 3:
				signatures[stem[0]].extend(['']*(3-suffix_number))
				f.write('{: <20} {: <10} {: <25} {: <25} {: <25} \n'.format(stem[0], count,
					signatures[stem[0]][0], signatures[stem[0]][1], signatures[stem[0]][2]))
			else:
				stem_examples = random.sample(signatures[stem[0]], 3)
				f.write('{: <20} {: <10} {: <25} {: <25} {: <25} \n'.format(stem[0], count,
					stem_examples[0], stem_examples[1], stem_examples[2]))

def getLexicon(stem_dict):

	lex_dict = {}
	for stem in stem_dict:
		for suffixes in stem_dict[stem]:
			temp_stem = ''
			temp_stem = temp_stem+stem
			init_suffixes = ''.join(suffixes)
			if init_suffixes == '':
				init_suffixes = 'NULL'
			if stem not in lex_dict:
				lex_dict[stem] = [init_suffixes]
			else:
				if init_suffixes not in lex_dict[stem]:
					lex_dict[stem].append(init_suffixes)

			for i, suffix in enumerate(suffixes):
				temp_stem = temp_stem+suffix
				if temp_stem not in lex_dict:
					if i < len(suffixes) - 1:
						new_suffix = ''.join(suffixes[i+1:])
						lex_dict[temp_stem] = [new_suffix]
					else:
						lex_dict[temp_stem] = ['NULL']
				if temp_stem in lex_dict:
					if i < len(suffixes) - 1:
						new_suffix = ''.join(suffixes[i+1:])
					else:
						new_suffix = 'NULL'
					if new_suffix not in lex_dict[temp_stem]:
							lex_dict[temp_stem].append(new_suffix)
	return lex_dict


def update_lexicon(lex_dict):

	for stem in lex_dict:
		lex_dict[stem] = '='.join(lex_dict[stem])
	return lex_dict

def get_signatures(lexicon):

	signatures = {}
	for stem in lexicon:
		signature = lexicon[stem]
		if signature not in signatures:
			signatures[signature] = [stem]
		else:
			signatures[signature].append(stem)

	return signatures

def file_to_list(filename, position, reverse):

	if reverse == False:
		word_list = []
		with open(filename, 'r') as f:
			for word in f:
				word = word.rstrip('\n')
				word = word.lower()
				if len(word) >= position:
					#word = word+' '
					word_list.append(word)
		return sorted(word_list)

	if reverse == True:
		word_list = []
		with open(filename, 'r') as f:
			for word in f:
				word = word.rstrip('\n')
				word = word.lower()
				if len(word) >= position:
					word = word[::-1]
					word_list.append(word)
		return sorted(word_list)

def word_split(wordlist, position):

	root = {}
	split_list = []
	for i, word in enumerate(wordlist[:-1]):
		stem = word[:position]
		if len(word) > position:
			if word[:position] == wordlist[i+1][:position]:
				if stem not in root:
					root[stem] = []

	previous_breaks = []
	previous_position = position
	last_stem = ''
	for i, word in enumerate(wordlist[:-1]):

		stem = word[:position]
		if stem != last_stem:
			previous_breaks = []
			previous_position = position
			last_stem = stem

		last_stem = stem
		if stem in root:
			post_stem = word[previous_position:]
			common_prefix = find_common_prefix(post_stem, wordlist[i+1][previous_position:])
			if common_prefix != '':

				previous_breaks.append(common_prefix)

				if post_stem != common_prefix:
					previous_breaks.append(word[previous_position+len(common_prefix):])
					root[stem].append(previous_breaks[:])
					split_list.append([stem]+previous_breaks[:])
					previous_breaks = previous_breaks[:-1]

				if post_stem == common_prefix:

					root[stem].append(previous_breaks[:])
					split_list.append([stem]+previous_breaks[:])
				previous_position = previous_position + len(common_prefix)
			else:
				previous_breaks.append(word[previous_position:])
				root[stem].append(previous_breaks[:])
				split_list.append([stem]+previous_breaks[:])
				if len(word) >= len(wordlist[i+1]):

					previous_breaks = previous_breaks[:-1]
					while word[:previous_position] != wordlist[i+1][:previous_position]: 
						if len(previous_breaks) == 0:
							break
						previous_position -= len(previous_breaks[-1])
						previous_breaks = previous_breaks[:-1]
						if previous_position == position:
							break
				else:

					previous_breaks = previous_breaks[:-1]
					while word[:previous_position] != wordlist[i+1][:previous_position]: 

						if len(previous_breaks) == 0:
							break
						previous_position -= len(previous_breaks[-1])
						previous_breaks = previous_breaks[:-1]
						if previous_position == position:
							break
	return root

def find_common_prefix(word1, word2):
	return word1[:([x[0]==x[1] for x in zip(word1,word2)]+[0]).index(0)]



if __name__ == '__main__':
	if len(sys.argv) > 2:
		final(sys.argv[1], int(sys.argv[2]))
			
				