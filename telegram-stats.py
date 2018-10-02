#!/usr/bin/python
#_*_ coding: utf-8 _*_

'''
@file 		telegram-stats.py
@author 	Simon Burkhardt - github.com/mnemocron
@date 		2018.10.01
'''

'''
chat statistics vectors:

numerics:
- total messages
- messages per person
- number of attachments
- number of gifs
- number of stickers
- number of videos
- number of voice messages
- use of markdown
- unique words (by person)
- average text length by person
- number of messages of length xy (single letter)

graphs:
- number of messages over time of the day
- number of messages by week/month over total time
- number of messages by weekday
- number of messages by date
(all the above by word count)
- distribution of text length vs. number of that length
- top words frequency by person

misc:
- top words (by person)
'''

try:
	import sys
	import os
	import optparse
	import re
	import json
	from pprint import pprint
	from collections import Counter
except Exception as e:
	print >> sys.stderr, 'Error importing modules'
	print >> sys.stderr, e
	sys.exit(1)

# ===== ARGUMENTS =====
parser = optparse.OptionParser('telegram-stats')
parser.add_option('-i', '--input-file', 	dest='indir', 	type='string', 	help='chat history file')
parser.add_option('-n', '--name', 			dest='name', 	type='string', 	help='name of the person')
(opts, args) = parser.parse_args()

def debugPrint(listed):
	i = 1
	for message in listed:
		print(str(i) + '\t' + message.replace('\n', ' ').replace('\r', ' '))
#		if(message.count('@mnemocron') > 1 or message.count('@continentalskylight') > 1):
#			sys.stderr.write(message + '\n\n')
		i += 1


def load_file_to_raw(path):
	try:
		with open(path) as file:
			data = json.load(file)
			return data
	except IOError:
		print('Error: could not open the file')
		exit(-1)

def from_data_select_chat(data, name):
	try:
		for chat in data['chats']['list']:
			if('name' in chat):
				if(name == chat['name']):
					data = chat
#					print(chat['messages'][0]['text'])
		return data
	except KeyError:
		print('Error: wrong file format (keys not found)')

def number_of_messages(chat):
	number = len(chat['messages'])
	person_A = chat['messages'][0]['from']
	person_B = ''
	number_A = 0
	number_B = 0
	stickers_A = 0
	stickers_B = 0
	gif_A = 0
	gif_B = 0
	link_A = 0
	link_B = 0
	voice_A = 0
	voice_B = 0
	video_A = 0
	video_B = 0
	file_A = 0
	file_B = 0
	photo_A = 0
	photo_B = 0
	markdown_A = 0
	markdown_B = 0
	all_text_A = ''
	all_text_B = ''
	for message in chat['messages']:
		if(message['type'] == 'message'):
			if person_A in message['from']:
				number_A += 1
				if('media_type' in message):
					if(message['media_type'] == 'sticker'):
						stickers_A += 1
					if(message['media_type'] == 'animation'):
						gif_A += 1
					if(message['media_type'] == 'voice_message'):
						voice_A += 1
					if(message['media_type'] == 'video_file'):
						video_A += 1
				if('photo' in message):
					photo_A += 1
				if(type(message['text']) is list):
					# TODO append to all_text_A
					markdown = 0
					for line in message['text']:
						if('type' in line and type(line) is dict):
							if(line['type'] == 'link'):
								link_A += 1
							if(line['type'] == 'pre' or line['type'] == 'italic' or line['type'] == 'bold'):
								markdown = 1 	# only count once per message not per use
							markdown_A += markdown
				else:
					all_text_A += ' ' + message['text'].encode('utf-8')

			else:
				person_B = message['from']
				number_B += 1
				if('media_type' in message):
					if(message['media_type'] == 'sticker'):
						stickers_B += 1
					if(message['media_type'] == 'animation'):
						gif_B += 1
					if(message['media_type'] == 'voice_message'):
						voice_B += 1
				if('photo' in message):
					photo_B += 1
				if(type(message['text']) is list):
					# TODO append to all_text_B 
					markdown = 0
					for line in message['text']:
						if('type' in line and type(line) is dict):
							if(line['type'] == 'link'):
								link_B += 1
							if(line['type'] == 'pre' or line['type'] == 'italic' or line['type'] == 'bold'):
								markdown = 1 	# only count once per message not per use
							markdown_B += markdown
				else:
					all_text_B += ' ' + message['text'].encode('utf-8')

	print('Person A: ' + person_A + '\t sent \t' + str(number_A)   + '\t messages')
	print('Person B: ' + person_B + '\t sent \t' + str(number_B)   + '\t messages')
	print('Person A: ' + person_A + '\t sent \t' + str(stickers_A) + '\t stickers')
	print('Person B: ' + person_B + '\t sent \t' + str(stickers_B) + '\t stickers')
	print('Person A: ' + person_A + '\t sent \t' + str(gif_A)      + '\t GIFs')
	print('Person B: ' + person_B + '\t sent \t' + str(gif_B)      + '\t GIFs')
	print('Person A: ' + person_A + '\t sent \t' + str(link_A)     + '\t links')
	print('Person B: ' + person_B + '\t sent \t' + str(link_B)     + '\t links')
	print('Person A: ' + person_A + '\t sent \t' + str(voice_A)    + '\t voice messages')
	print('Person B: ' + person_B + '\t sent \t' + str(voice_B)    + '\t voice messages')
	print('Person A: ' + person_A + '\t sent \t' + str(photo_A)    + '\t photos')
	print('Person B: ' + person_B + '\t sent \t' + str(photo_B)    + '\t photos')
	print('Person A: ' + person_A + '\t used formating in ' + str(markdown_A) + '\t of their messages')
	print('Person B: ' + person_B + '\t used formating in ' + str(markdown_B) + '\t of their messages')
	print('Total Messages: ' + str(number))
	print('Total Texts: ' + str(number_A + number_B))
	
	all_text_A = all_text_A.lower()
	for char in '-.,\n':
		all_text_A = all_text_A.replace(char,' ')
	all_text_B = all_text_B.lower()
	for char in '-.,\n':
		all_text_B = all_text_B.replace(char,' ')
#	print(all_text_A)
#	a = Counter(all_text_A).most_common()
#	print(a)
	d_a = {}
	d_b = {}
	for word in all_text_A.split(' '):
		if (word.isalpha() and len(word) > 4): 			# TODO, this is ugly because it ignores éöäèèà etc.
			d_a[word] = d_a.get(word, 0) + 1
	for word in all_text_B.split(' '):
		if (word.isalpha() and len(word) > 4): 			# TODO, this is ugly because it ignores éöäèèà etc.
			d_b[word] = d_b.get(word, 0) + 1
	word_freq_A = []
	word_freq_B = []
	for key, value in d_a.items():
		word_freq_A.append((value, key))
	word_freq_A.sort(reverse=True)
	for key, value in d_b.items():
		word_freq_B.append((value, key))
	word_freq_B.sort(reverse=True)

	print('top words of person A:')
	i = 0
	max = len(word_freq_A)
	if max > 50:
		max = 50
	for i in range(max):
		print(word_freq_A[i])
	print('top words of person B:')
	i = 0
	max = len(word_freq_B)
	if max > 50:
		max = 50
	for i in range(max):
		print(word_freq_B[i])

# ===== MAIN =====
def main():
	if ( opts.indir is None or opts.name is None):
		parser.print_help() 
		exit(0)
	raw_data = load_file_to_raw(opts.indir)
	chat_data = from_data_select_chat(raw_data, opts.name)
	number_of_messages(chat_data)


# ================

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt, e:
		print('Aborted by KeyboardInterrupt')
		exit(0)





# old shit
'''
def numberMetrics(listed):
	num_msg_simon = 0
	num_msg_kelly = 0
	num_txt_simon = 0
	num_txt_kelly = 0
	total_char_count_simon = 0
	total_char_count_kelly = 0

	for i in range(len(listed)):
		message = listed[i]
		try:
			if('[@continentalskylight]' in message and '' in message):
				num_msg_kelly += 1
				text = message.split('[@]: ')[1]
				if shouldCountMessage(text):
					total_char_count_kelly += len(text)
					num_txt_kelly += 1
			if('[@mnemocron]' in message and 'Simon' in message):
				num_msg_simon += 1
				text = message.split('[@](you): ')[1]
				if(shouldCountMessage(text)):
					total_char_count_simon += len(text)
					num_txt_simon += 1
		except IndexError, e:
			pass

	avg_char_count_simon = total_char_count_simon / num_txt_simon
	avg_char_count_kelly = total_char_count_kelly / num_txt_kelly
	print('Total messages:')
	print('Simon: ' + str(num_msg_simon))
	print('Kelly: ' + str(num_msg_kelly))
	print('Total text messages:')
	print('Simon: ' + str(num_txt_simon))
	print('Kelly: ' + str(num_txt_kelly))
	print('Total characters:')
	print('Simon: ' + str(total_char_count_simon))
	print('Kelly: ' + str(total_char_count_kelly))
	print('Average message length:')
	print('Simon: ' + str(avg_char_count_simon))
	print('Kelly: ' + str(avg_char_count_kelly))
'''


