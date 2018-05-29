import numpy as np, numpy.random
import math
import sys

def final(filename, num_states, VerboseFlag=False):

	words = file_to_list(filename)
	init_state_transitions = initialize_state_probabilities(num_states)
	init_pi_probabilities = initialize_pi_probability(num_states)
	emission_probabilities = initialize_emissions(words, num_states)
	sum_of_plogs = 0
	with open('strings_plogs.txt', 'w') as text_file:

		for i, word in enumerate(words):
			if VerboseFlag == True:
				print('------------------------------------------------------------------')
				print('---------Iteration Number {}'.format(i))
				print('------------------------------------------------------------------')
			all_alphas = forward_algorithm(word, num_states, init_state_transitions, 
						emission_probabilities, init_pi_probabilities, VerboseFlag = False)
			all_betas = backward_algorithm(word, num_states, init_state_transitions, 
						emission_probabilities)
			if VerboseFlag == True:
				alpha_beta_display(all_alphas, all_betas)
			string_probability = all_alphas[-1]
			string_plog = -1 * math.log((string_probability), 2)
			sum_of_plogs += string_plog
			text_file.write(word + '              ' + "{0:.4g}".format(string_probability) + '              ' + "{0:.4g}\n".format(string_plog))
	
	with open('strings_plogs.txt', 'a') as text_file:
		text_file.write("\n" + "Sum of the plogs:     {0}".format(sum_of_plogs))

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

def forward_algorithm(word, num_states, state_transitions, emission_probabilities, pi_probabilities, VerboseFlag = False):

	if VerboseFlag == True:
		print('')
		print('*** word: {}***'.format(word))
		print('')
		print('Forward')
		for state in range(num_states):
			print('Pi of state     {0}      {1:.4g}'.format(state, pi_probabilities[state]))

	probabilities = dict(pi_probabilities)
	all_alphas = [tuple(probabilities.values())]
	for i, letter in enumerate(word):
		t = i+2
		if VerboseFlag == True:
			print("   time {0}: '{1}'".format(t, letter))
		alpha_sum = 0
		for to_state in range(num_states):
			if VerboseFlag == True:
				print('      to state: {0}'.format(to_state))
			alpha = 0
			for from_state in range(num_states):
				previous_alphas = state_transitions[from_state][to_state] * probabilities[from_state] * emission_probabilities[from_state][letter]
				if VerboseFlag == True:
					print('         from state {0}   previous alpha: {1:.4g}'.format(from_state, previous_alphas))
				alpha += previous_alphas
			if VerboseFlag == True:	
				print('      Alpha at time = {0}, state = {1}: {2:.4g}'.format(t, to_state, alpha))
			alpha_sum += alpha
		for state in range(num_states):
			probabilities[state] = alpha
		all_alphas.append((alpha, alpha))
		if VerboseFlag == True:
			print('')
			print("      Sum of alpha's at time {0}: {1:.4g}".format(t, alpha_sum))
			print('')
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

def alpha_beta_display(all_alphas, all_betas):

	print('Alpha:')
	for time, (state1, state2) in enumerate(all_alphas[:-1]):
		print('Time    {0:.4g}  State  0:      {1:.4g}       State  1:      {2:.4g}'.format(time+1, state1, state2))

	print('Beta:')
	for time, (state1, state2) in enumerate(all_betas):
		print('Time    {0:.4g}  State  0:      {1:.4g}       State  1:      {2:.4g}'.format(time+1, state1, state2))

	print('')
	print('String probability from Alphas:  {0:.4g}'.format(all_alphas[-1]))
	print('')
	print('String probability from Betas:  {0:.4g}'.format(all_betas[0][0]*all_alphas[0][0] + all_betas[0][1]*all_alphas[0][1]))

'''
def set_hw_numbers():

	words = ['babi#', 'dida#']
	state_transitions = [{0: 0.5, 1: 0.5}, {0: 0.5, 1: 0.5}]
	emission_probabilities = [{'i': 0.3744, 'a': .1896, '#': .1680, 'b': .1571, 'd': .1109}, 
							  {'d': .3272, 'b': .2787, 'i': .2393, 'a': .0916, '#': .0633}]
	pi_probabilities = {0: .6814, 1: .3186}
'''

if __name__ == '__main__':
	if len(sys.argv) > 3:
		#print(sys.argv)
		final(sys.argv[1], int(sys.argv[2]), sys.argv[3])
