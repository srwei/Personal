import sys
import xmltodict
import pandas as pd
import numpy as np
import re

def main():

	with open(sys.argv[1]) as fd:
		doc = xmltodict.parse(fd.read())
	columns = ['sentence', 'target_words', 'directive-subjective-intensity', 'directive-subjective-expression-intensity', 'expressive-subjective-intensity', 'objective-uncertain']
	df = pd.DataFrame(columns=columns)
	text = doc['GateDocument']['TextWithNodes']['#text']
	period_list = []
	sentence_indexes = []
	for i, character in enumerate(text):
		if character == ".":
			period_list.append(i)
	period_list.insert(0,-2)
	for i, period in enumerate(period_list[:-1]):
		sentence_indexes.append((period, period_list[i+1]))

	annotation_list = doc['GateDocument']['AnnotationSet'][1]['Annotation']
	df_index = 0
	for annotation in annotation_list:
		if annotation['@Type'] == 'direct-subjective':
			position = int(annotation['@StartNode'])-2
			sentence = get_sentence(text, sentence_indexes, position)
			end_index = int(annotation['@EndNode'])-2
			for attribute in annotation['Feature']:
				if attribute['Name']['#text'] == 'intensity':
					intensity = attribute['Value']['#text']
				if attribute['Name']['#text'] == 'expression-intensity':
					expression_intensity = attribute['Value']['#text']
			df.loc[df_index] = [sentence, text[position:end_index],intensity, expression_intensity, np.nan, np.nan]
			df_index += 1
		if annotation['@Type'] == 'expressive-subjectivity':
			position = int(annotation['@StartNode'])-2
			sentence = get_sentence(text, sentence_indexes, position)
			end_index = int(annotation['@EndNode'])-2
			for attribute in annotation['Feature']:
				if attribute['Name']['#text'] == 'intensity':
					intensity = attribute['Value']['#text']
					df.loc[df_index] = [sentence, text[position:end_index],np.nan, np.nan, intensity, np.nan]
					df_index += 1

		if annotation['@Type'] == 'objective-speech-event':
			position = int(annotation['@StartNode'])-2
			sentence = get_sentence(text, sentence_indexes, position)
			end_index = int(annotation['@EndNode'])-2	
			for attribute in annotation['Feature']:
				if attribute['Name']['#text'] == 'objective-uncertain':
					uncertain_score = attribute['Value']['#text']
					df.loc[df_index] = [sentence, text[position:end_index],np.nan, np.nan, np.nan, uncertain_score]
					df_index += 1

	df.to_pickle(sys.argv[2])

def get_sentence(text, sentence_indexes, position):
	for sentence in sentence_indexes:
		if sentence[0]<position<sentence[1]:
			indexed_sentence = text[sentence[0]+2:sentence[1]]
			regex = re.compile(r'[\n\r\t]')
			indexed_sentence = regex.sub(' ', indexed_sentence)
			return indexed_sentence


if __name__ == "__main__":
	main()

