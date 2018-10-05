#! /usr/bin/python3

from collections import Counter

def _message_numerics(chat):
	metrics = {}
	metrics['A'] = {}
	metrics['B'] = {}
	metrics['A']['text'] = u''
	metrics['B']['text'] = u''
	metrics['A']['name'] = chat['messages'][0]['from']
	metrics['total'] = len(chat['messages'])

	for message in chat['messages']:
		if(message['type'] == 'message'):
			person = 'B'
			if metrics['A']['name'] in message['from']:
				person = 'A'
			metrics[person]['name'] = message['from']
			metrics[person]['total'] = metrics[person].get('total', 0) + 1
			if('media_type' in message):
				metrics[person][message['media_type']] = metrics[person].get(message['media_type'], 0) + 1
			if('photo' in message):
				metrics[person]['photo'] = metrics[person].get('photo', 0) + 1
			if(type(message['text']) is list):
				used_markdown = False
				for line in message['text']:
					if('type' in line and type(line) is dict):
						if(line['type'] == 'link'):
							metrics[person]['url'] = metrics[person].get('url', 0) + 1
						if(line['type'] == 'pre' or line['type'] == 'italic' or line['type'] == 'bold'):
							used_markdown = True
						metrics[person]['markdown'] = metrics[person].get('markdown', 0) + used_markdown
					elif(type(line) is str):
						metrics[person]['text'] = (metrics[person].get('text', 0) + ' ' + line)
			else:
				metrics[person]['text'] = (metrics[person].get('text', 0) + ' ' + message['text'])

	'''
	print('Person A: ' + metrics['A']['name'] + '\t sent \t' + str(metrics['A']['total'])   + '\t messages')
	print('Person B: ' + metrics['B']['name'] + '\t sent \t' + str(metrics['B']['total'])   + '\t messages')
	print('Person A: ' + metrics['A']['name'] + '\t sent \t' + str(metrics['A']['sticker']) + '\t stickers')
	print('Person B: ' + metrics['B']['name'] + '\t sent \t' + str(metrics['B']['sticker']) + '\t stickers')
	print('Person A: ' + metrics['A']['name'] + '\t sent \t' + str(metrics['A']['animation'])      + '\t GIFs')
	print('Person B: ' + metrics['B']['name'] + '\t sent \t' + str(metrics['B']['animation'])      + '\t GIFs')
	print('Person A: ' + metrics['A']['name'] + '\t sent \t' + str(metrics['A']['url'])     + '\t links')
	print('Person B: ' + metrics['B']['name'] + '\t sent \t' + str(metrics['B']['url'])     + '\t links')
	print('Person A: ' + metrics['A']['name'] + '\t sent \t' + str(metrics['A']['voice_message'])    + '\t voice messages')
	print('Person B: ' + metrics['B']['name'] + '\t sent \t' + str(metrics['B']['voice_message'])    + '\t voice messages')
	print('Person A: ' + metrics['A']['name'] + '\t sent \t' + str(metrics['A']['photo'])    + '\t photos')
	print('Person B: ' + metrics['B']['name'] + '\t sent \t' + str(metrics['B']['photo'])    + '\t photos')
	print('Person A: ' + metrics['A']['name'] + '\t used formating in ' + str(metrics['A']['markdown']) + '\t of their messages')
	print('Person B: ' + metrics['B']['name'] + '\t used formating in ' + str(metrics['B']['markdown']) + '\t of their messages')
	print('Total Messages: ' + str(metrics['total']))
	print('Total Texts: ' + str(metrics['A']['total'] + metrics['B']['total']))
	'''
	metrics['A']['total_chars'] = len(metrics['A']['text'])
	metrics['B']['total_chars'] = len(metrics['B']['text'])
	metrics['A']['wordlist'] = count_words(metrics['A']['text'])
	metrics['B']['wordlist'] = count_words(metrics['B']['text'])
	metrics['A']['emojilist'] = count_emojis(metrics['A']['text'])
	metrics['B']['emojilist'] = count_emojis(metrics['B']['text'])
	return metrics

	
def count_words(text):
	text = text.lower()
	words = text.split()
	# remove non alphanumerics (this does not affect äöüéèà...)
	for i in range(len(words)):
		words[i] = ''.join(e for e in words[i] if e.isalnum())
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
