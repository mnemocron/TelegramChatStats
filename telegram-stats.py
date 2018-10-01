#!/usr/bin/python
#_*_ coding: utf-8 _*_

'''
@file 		telegram-stats.py
@author 	Simon Burkhardt - github.com/mnemocron
@date 		2018.10.01
'''

try:
	import sys
	import os
	import optparse
	import re
	import json
	from pprint import pprint
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
	for message in chat['messages']:
		if(message['type'] == 'message'):
			if person_A in message['from']:
				number_A += 1
			else:
				person_B = message['from']
				number_B += 1
	print('Person A: ' + person_A + ' sent ' + str(number_A) + ' messages')
	print('Person B: ' + person_B + ' sent ' + str(number_B) + ' messages')
	print('Total: ' + str(number) + ' = ' + str(number_A + number_B))

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
			if('[@continentalskylight]' in message and 'Kelly Speakman' in message):
				num_msg_kelly += 1
				text = message.split('[@continentalskylight]: ')[1]
				if shouldCountMessage(text):
					total_char_count_kelly += len(text)
					num_txt_kelly += 1
			if('[@mnemocron]' in message and 'Simon Burkhardt' in message):
				num_msg_simon += 1
				text = message.split('[@mnemocron](you): ')[1]
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


