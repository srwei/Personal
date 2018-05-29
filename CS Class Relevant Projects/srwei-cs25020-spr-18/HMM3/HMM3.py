import numpy as np, numpy.random
import math
import sys


def final(filename, num_states, VerboseFlag=False):

	words = file_to_list(filename)
	a_paramaters = [0.1, 0.3, 0.5, 0.7, 0.9]

	with open('maximization_results.txt', 'w') as text_file:
		for a1 in a_paramaters:
			for a2 in a_paramaters:
				#transition_probabilities = initialize_state_probabilities(num_states)
				pi_probabilities = initialize_pi_probability(num_states)
				emission_probabilities = initialize_emissions(words, num_states)
				transition_probabilities = [{0: a1, 1: 1 - a1}, {0: a2, 1: 1 - a2}]
				iterations = 0
				min_plog = 9999999
				opt_transition_probability = 0
				opt_emission_probability = 0
				opt_pi_probability = 0
				opt_emission_log_ratios = 0
				
				while iterations <= 20:
					sum_of_plogs = 0
					initial_expected_counts = get_SC(filename, num_states, transition_probabilities, \
						emission_probabilities, pi_probabilities, VerboseFlag=False)
					expected_counts = initial_expected_counts[0]
					initial_soft_counts = initial_expected_counts[1]
					log_ratio_emissions = {}
					for letter in emission_probabilities[0]:
						
						if emission_probabilities[0][letter] < 10**-100:
							emission_probabilities[0][letter] = 10**-100
						if emission_probabilities[1][letter] < 10**-100:
							emission_probabilities[1][letter] = 10**-100
						
						log_ratio_emissions[letter] = (math.log10(emission_probabilities[0][letter]) \
							- math.log10(emission_probabilities[1][letter])) / math.log10(2)

					for i, word in enumerate(words):
						all_alphas = forward_algorithm(word, num_states, transition_probabilities, 
								emission_probabilities, pi_probabilities)
						string_probability = all_alphas[-1]
						if string_probability < (10**-50):
							string_probability = 10**-50
						string_plog = -1 * math.log((string_probability), 2)
						sum_of_plogs += string_plog

					if sum_of_plogs < min_plog:
						min_plog = sum_of_plogs
						opt_transition_probability = transition_probabilities
						opt_emission_probability = emission_probabilities
						opt_pi_probability = pi_probabilities
						opt_emission_log_ratios = log_ratio_emissions

					transition_probabilities = get_max_transition_probabilities(expected_counts, VerboseFlag)
					emission_probabilities = get_max_emission_probabilities(expected_counts, num_states, VerboseFlag)
					pi_probabilities = get_max_pi_probabilities(initial_soft_counts, num_states, VerboseFlag)
					iterations += 1

				text_file.write('\n -------Local Maxima--------- \n')
				text_file.write('\n Starting Transition Probabilities:  \n')
				text_file.write('From State 0 to State 0: {}         From State 0 to State 1: {} \n'.format(a1, 1 - a1))
				text_file.write('From State 1 to State 0: {}         From State 1 to State 1: {} \n'.format(a2, 1 - a2))
				text_file.write('\n Sum of Plogs:   {} \n'.format(min_plog))
				text_file.write('\n    Transition Probabilities \n')
				text_file.write('From State 0 to State 0: {}         From State 0 to State 1: {} \n'.format(opt_transition_probability[0][0], opt_transition_probability[0][1]))
				text_file.write('From State 1 to State 0: {}         From State 1 to State 1: {} \n'.format(opt_transition_probability[1][0], opt_transition_probability[1][1]))
				text_file.write('\n    Emission Probabilities \n')
				for state in opt_emission_probability:
					for letter in state:
						text_file.write('{}   {} \n'.format(letter, state[letter]))
				text_file.write('\n    Pi Probabilities \n')
				text_file.write('State 0: {} \n'.format(opt_pi_probability[0]))
				text_file.write('State 1: {} \n'.format(opt_pi_probability[1]))
				text_file.write('\n    Log Emissions \n')
				state0letters = []
				state1letters = []
				for letter in opt_emission_log_ratios:
					if opt_emission_log_ratios[letter] > 0:
						state0letters.append((letter, opt_emission_log_ratios[letter]))
					else:
						state1letters.append((letter, opt_emission_log_ratios[letter]))
				state0letters = sorted(state0letters, key=lambda x: x[1], reverse=True)
				state1letters = sorted(state1letters, key=lambda x: x[1])
				for i in range(len(opt_emission_log_ratios)):
					a = ('                   ', '')
					b = ('', '')
					if i < len(state0letters):
						a = state0letters[i]
					if i < len(state1letters):
						b = state1letters[i]
					text_file.write('{} {}         {} {} \n'.format(a[0], a[1], \
						b[0], b[1]))


def get_max_emission_probabilities(expected_counts, num_states, VerboseFlag):

	expected_list = []
	emission_probabilities = []
	for state in range(num_states):
		emission_probabilities.append({})
	for state in range(num_states):
		expected_list.append({})
	for unique_states in expected_counts:
		expected_list[unique_states[1]][(unique_states[0], unique_states[2])] = expected_counts[unique_states]
	done_letters = []
	total_sc_sum = 0
	if VerboseFlag == True:
		print("Emission \n")
	for i, from_state in enumerate(expected_list):
		normalize_sc = []
		total = 0
		if VerboseFlag == True:
			print('From State: {} \n'.format(i))
		for letter_to_state in from_state:
			if letter_to_state[0] not in done_letters:
				done_letters.append(letter_to_state[0])
				if VerboseFlag == True:
					print('    letter:  {} \n'.format(letter_to_state[0]))
					print('         to state   {}       {} \n'.format(letter_to_state[1], from_state[letter_to_state]))
				total_sc_sum += from_state[letter_to_state]
				total += from_state[letter_to_state]
			else:
				total_sc_sum += from_state[letter_to_state]
				total += from_state[letter_to_state]
				if VerboseFlag == True:
					print('         to state   {}       {} \n'.format(letter_to_state[1], from_state[letter_to_state]))
					print("         Total soft count of '{}' from state= {} equals: {} \n".format(letter_to_state[0], i, total_sc_sum) )
				normalize_sc.append((letter_to_state[0], total_sc_sum))
				total_sc_sum = 0
		done_letters = []
		if VerboseFlag == True:
			print('    Normalize soft counts to get emission probabilities')
		for letter in normalize_sc:
			if VerboseFlag == True:
				print('             letter:  {}    probability  {}'.format(letter[0], letter[1] / total))
			emission_probabilities[i][letter[0]] = letter[1] / total
	return emission_probabilities

def get_max_pi_probabilities(initial_soft_counts, num_states, VerboseFlag):

	max_pi_probabilities = {}
	total_words = 0
	for i in range(num_states):
		max_pi_probabilities[i] = 0
	for unique_states in initial_soft_counts:
		max_pi_probabilities[unique_states[1]] += initial_soft_counts[unique_states]
		total_words += initial_soft_counts[unique_states]
	for from_state in max_pi_probabilities:
		max_pi_probabilities[from_state] = max_pi_probabilities[from_state] / total_words
	if VerboseFlag == True:
		print('\n Pi: \n')
		print('State   0    {}'.format(max_pi_probabilities[0]))
		print('State   1    {}'.format(max_pi_probabilities[1]))
	return max_pi_probabilities

def get_max_transition_probabilities(expected_counts, VerboseFlag):
	# {(letter, from_state, to state): soft counts, etc}
	#  WANT
	#   [{0: 0.4, 1: 0.6}, {0: 0.85, 1: 0.15}]

	max_state_transitions = []

	if VerboseFlag == True:
		print('\n Transition Probabilities \n')

	for unique_states in expected_counts:
		letter = unique_states[0]
		from_state = unique_states[1]
		to_state = unique_states[2]
		if len(max_state_transitions) <= from_state:
			max_state_transitions.insert(from_state, {to_state: expected_counts[unique_states]})
		else:
			if to_state not in max_state_transitions[from_state]:
				max_state_transitions[from_state][to_state] = expected_counts[unique_states]
			else:
				max_state_transitions[from_state][to_state] += expected_counts[unique_states]

	for from_state in max_state_transitions:
		if VerboseFlag == True:
			print('     From State: {} \n'.format(from_state))
		total_sum = 0
		for to_state in from_state:
			total_sum += from_state[to_state]
		for to_state in from_state:
			if VerboseFlag == True:
				print('          To State: {}     Probability: {} \n'.format(to_state, from_state[to_state] / total_sum))
			from_state[to_state] = from_state[to_state] / total_sum

	return max_state_transitions


def get_SC(filename, num_states, transition_probabilities, \
	emission_probabilities, pi_probabilities, VerboseFlag=False):

	words = file_to_list(filename)
	init_state_transitions = transition_probabilities
	init_pi_probabilities = pi_probabilities
	emission_probabilities = emission_probabilities
	both_counts = []
	all_expected_counts = {}
	initial_sc = {}
	for i, word in enumerate(words):

		all_alphas = forward_algorithm(word, num_states, init_state_transitions, 
					emission_probabilities, init_pi_probabilities)
		all_betas = backward_algorithm(word, num_states, init_state_transitions, 
					emission_probabilities)
		string_probability = all_alphas[-1]

		for i, letter in enumerate(word):
			sum_counts = 0
			for from_state in range(num_states):
				for to_state in range(num_states):
					counts = (all_alphas[i][from_state] * all_betas[i+1][to_state] * init_state_transitions[from_state][to_state] * emission_probabilities[from_state][letter]) / string_probability
					sum_counts += counts
					if (letter, from_state, to_state) not in all_expected_counts:
						all_expected_counts[(letter, from_state, to_state)] = counts
					else:
						all_expected_counts[(letter, from_state, to_state)] += counts

		for i, letter in enumerate(word[0]):
			sum_counts2 = 0
			for from_state in range(num_states):
				for to_state in range(num_states):
					counts = (all_alphas[i][from_state] * all_betas[i+1][to_state] * init_state_transitions[from_state][to_state] * emission_probabilities[from_state][letter]) / string_probability
					sum_counts2 += counts
					if (letter, from_state, to_state) not in initial_sc:
						initial_sc[(letter, from_state, to_state)] = counts
					else:
						initial_sc[(letter, from_state, to_state)] += counts
	both_counts.append(all_expected_counts)
	both_counts.append(initial_sc)
	return both_counts  # {(letter, from_state, to state): soft counts, etc}



def file_to_list(filename):

	word_list = []
	with open(filename, 'r') as f:
		for word in f:
			word = word.rstrip('\n')
			word = word.lower()
			word = word + '#'
			word_list.append(word)

	return word_list

def initialize_state_probabilities(num_states):

	state_transitions = []
	for state in range(num_states):
		per_state_transition = {}
		for state in range(num_states):
			per_state_transition[state] = 1/num_states 
		state_transitions.append(per_state_transition)

	return state_transitions 

def initialize_emissions(words, num_states):

	init_probabilities = []
	unique_letters = list({letter for word in words for letter in word})
	emission_probabilities = np.random.dirichlet(np.ones(len(unique_letters)), size=1)[0]

	for i in range(0, num_states):
		state_probabilities = np.random.dirichlet(np.ones(len(unique_letters)), size=1)[0]
		emission_probabilities = {}
		for i, letter in enumerate(unique_letters):
			emission_probabilities[letter] = state_probabilities[i]
		init_probabilities.append(emission_probabilities)

	return init_probabilities    

def initialize_pi_probability(num_states):
	
	pi_probabilities = {}
	init_pi_probabilities = np.random.dirichlet(np.ones(num_states), size=1)[0]
	for state in range(num_states):
		pi_probabilities[state] = init_pi_probabilities[state]
	return pi_probabilities

def forward_algorithm(word, num_states, state_transitions, emission_probabilities, pi_probabilities):

	probabilities = dict(pi_probabilities)
	all_alphas = [tuple(probabilities.values())]
	for i, letter in enumerate(word):
		t = i+2
		alpha_sum = 0
		for to_state in range(num_states):
			alpha = 0
			for from_state in range(num_states):
				previous_alphas = state_transitions[from_state][to_state] * probabilities[from_state] * emission_probabilities[from_state][letter]
				alpha += previous_alphas
			alpha_sum += alpha
		for state in range(num_states):
			probabilities[state] = alpha
		all_alphas.append((alpha, alpha))
	all_alphas.append(alpha_sum)
	
	return all_alphas

def backward_algorithm(word, num_states, state_transitions, emission_probabilities):

	pi_probabilities = {0: 1, 1: 1}
	all_betas = [tuple(pi_probabilities.values())]

	for letter in range(len(word), 0, -1):

		new_pi_probabilities = {}
		for from_state in range(num_states):
			beta = 0
			for to_state in range(num_states):
				previous_betas = state_transitions[from_state][to_state] * pi_probabilities[to_state] * emission_probabilities[from_state][word[letter-1]]
				beta += previous_betas
			new_pi_probabilities[from_state] = beta
		pi_probabilities = new_pi_probabilities	
		all_betas.insert(0, tuple(pi_probabilities.values()))

	return all_betas

if __name__ == '__main__':
	if len(sys.argv) > 3:
		#print(sys.argv)
		final(sys.argv[1], int(sys.argv[2]), sys.argv[3])
