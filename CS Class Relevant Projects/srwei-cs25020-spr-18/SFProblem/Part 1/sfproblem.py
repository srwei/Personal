import sys

def final(text_file, position):

	wordlist = file_to_list(text_file, position, reverse=False)
	back_words = file_to_list(text_file, position, reverse=True)
	
	left_to_right = word_split(wordlist, position)
	left_to_right
	l2r_max_col = get_column_length(left_to_right)
	for word in left_to_right:
		for i, sub in enumerate(word):
			if len(sub) < l2r_max_col[i]:
				missing_space = l2r_max_col[i] - len(sub)
				word[i] = sub+(' '*missing_space)

	with open('successor-splits.txt', 'w') as text_file:
		text_file.write('-'*35 + 'Successor Splits' + '-'*35 + '\n')
		for word in left_to_right:
			text_file.write(''.join(word))
			text_file.write('\n')
	
	right_to_left = word_split(back_words, position)
	back_fill = []
	max_split = 0
	for word in right_to_left:
		temp = []
		for sub in word:
			temp.insert(0, sub[::-1])
		back_fill.append(temp)
		if len(temp) > max_split:
			max_split = len(temp)

	right_to_left = back_fill

	for word in right_to_left:
		if len(word) < max_split:
			missing_split = max_split - len(word)
			for i in range(missing_split):
				word.insert(0, '')

	r2l_max_col = get_column_length(right_to_left)
	for word in right_to_left:
		for i, sub in enumerate(word):
			if len(sub) < r2l_max_col[i]:
				missing_space = r2l_max_col[i] - len(sub)
				word[i] = sub+(' '*missing_space)
			word[i] = ' '+word[i]

	with open('predecessor-splits.txt', 'w') as text_file:
		text_file.write('-'*35 + 'Predecessor Splits' + '-'*35 + '\n')
		for word in right_to_left:
			text_file.write(''.join(word))
			text_file.write('\n')

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

def get_column_length(word_split):
	max_col = []
	for stem in word_split:
		for i, sub in enumerate(stem):
			if i+1 > len(max_col):
				max_col.append(len(sub))
			else:
				if len(sub) > max_col[i]:
					max_col[i] = len(sub)
	max_col[0]+=1
	return max_col

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
	return split_list

def find_common_prefix(word1, word2):
	return word1[:([x[0]==x[1] for x in zip(word1,word2)]+[0]).index(0)]

if __name__ == '__main__':
	if len(sys.argv) > 2:
		final(sys.argv[1], int(sys.argv[2]))
			
				