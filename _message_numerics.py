#! /usr/bin/python3

from collections import Counter


'''
@input 	chat (dict)
@output metrics (dict)

calculates all the numerical metrics
'''
def _message_numerics(chat):
	metrics = {}
	metrics['A'] = {}
	metrics['B'] = {}
	metrics['A']['text'] = u''
	metrics['B']['text'] = u''
	metrics['A']['media'] = {}
	metrics['B']['media'] = {}
	metrics['A']['name'] = chat['messages'][0]['from'] # person A is the first message
	metrics['total'] = len(chat['messages'])

	for message in chat['messages']:
		if(message['type'] == 'message'):  # there are other types like calls
			person = 'B'
			if metrics['A']['name'] in message['from']:
				person = 'A'
			metrics[person]['name'] = message['from']
			metrics[person]['total_messages'] = metrics[person].get('total_messages', 0) + 1  # count messages
			if('media_type' in message):  	# automatically count the different media types
				metrics[person]['media'][message['media_type']] = metrics[person]['media'].get(message['media_type'], 0) + 1
			if('photo' in message):
				metrics[person]['photo'] = metrics[person].get('photo', 0) + 1
			if(type(message['text']) is list):   # multiple elements in one message
				used_markdown = False
				for line in message['text']:
					if('type' in line and type(line) is dict):
						if(line['type'] == 'link'):
							metrics[person]['urls'] = metrics[person].get('urls', 0) + 1
						if(line['type'] == 'pre' or line['type'] == 'italic' or line['type'] == 'bold'):
							used_markdown = True  # only count markdown once per message, not per use
						metrics[person]['markdown'] = metrics[person].get('markdown', 0) + used_markdown
					elif(type(line) is str):
						metrics[person]['text'] = (metrics[person].get('text', 0) + ' ' + line)
			else:
				metrics[person]['text'] = (metrics[person].get('text', 0) + ' ' + message['text'])

	metrics['A']['total_chars'] = len(metrics['A']['text'])
	metrics['B']['total_chars'] = len(metrics['B']['text'])
	metrics['A']['wordlist'] = count_word_frequency(metrics['A']['text'])
	metrics['B']['wordlist'] = count_word_frequency(metrics['B']['text'])
	metrics['A']['total_words'] = count_words(metrics['A']['text'])
	metrics['B']['total_words'] = count_words(metrics['B']['text'])
	metrics['words'] = count_word_frequency(metrics['A']['text'] + ' \n' + metrics['B']['text'])
	metrics['unique_words'] = len(metrics['words'])
	metrics['A']['unique_words'] = len(metrics['A']['wordlist'])
	metrics['B']['unique_words'] = len(metrics['B']['wordlist'])
	metrics['A']['emojilist'] = count_emojis(metrics['A']['text'])
	metrics['B']['emojilist'] = count_emojis(metrics['B']['text'])
	metrics['A']['avg_chars'] = metrics['A']['total_chars'] / metrics['A']['total_messages']
	metrics['B']['avg_chars'] = metrics['B']['total_chars'] / metrics['B']['total_messages']
	metrics['A']['avg_words'] = metrics['A']['total_words'] / metrics['A']['total_messages']
	metrics['B']['avg_words'] = metrics['B']['total_words'] / metrics['B']['total_messages']
	return metrics

def count_words(text):
	text = text.lower()
	words = text.split()
	# remove non alphanumerics (this does not affect äöüéèà...)
	for i in range(len(words)):
		words[i] = ''.join(e for e in words[i] if e.isalnum())
	return len(words)

def count_word_frequency(text):
	text = text.lower()
	words = text.split()
	# remove non alphanumerics (this does not affect äöüéèà...)
	for i in range(len(words)):
		words[i] = ''.join(e for e in words[i] if e.isalnum())
	wordcount = len(words)
	# count ocurrences of each word
	wordlist = {}
	for word in words:
		if len(word) > 0:
			wordlist[word] = wordlist.get(word, 0) + 1
	# convert dict to list
	wordfreq = []
	for key, value in wordlist.items():
		wordfreq.append((value, key))
	wordfreq.sort(reverse=True) # sort
	return wordfreq

def count_emojis(text):
	# count ocurrences of each word
	emlist = {}
	for em in text:
		if(len(em.encode('utf-8')) > 3):
			emlist[em] = emlist.get(em, 0) + 1
	# convert dict to list
	emfreq = []
	for key, value in emlist.items():
		emfreq.append((value, key))
	emfreq.sort(reverse=True) # sort
	return emfreq
