#! /usr/bin/python3

#_*_ coding: utf-8 _*_

'''
@file 		telegram-statistics.py
@author 	Simon Burkhardt - github.com/mnemocron
@date 		2018.10.01

https://www.reddit.com/r/LongDistance/comments/9jud8j/analysis_of_texts_from_a_long_distance/?utm_content=comments&utm_medium=user&utm_source=reddit&utm_name=frontpage

'''

from __future__ import print_function

import sys
import os
import optparse
import re
import json
import codecs
import numpy as np   # install with pip3
import pandas as pd  # install with pip3
import bokeh         # install with pip3
from pprint import pprint
from collections import Counter
from datetime import datetime
from datetime import timedelta

from _message_numerics import _message_numerics
from _message_graphs import _message_graphs

parser = optparse.OptionParser('telegram-stats')
parser.add_option('-i', '--input-file', 	dest='indir', 	type='string', 	help='chat history file')
parser.add_option('-n', '--name', 			dest='name', 	type='string', 	help='name of the person')
(opts, args) = parser.parse_args()

def dump_to_json_file(filename, data):
	with open(filename, 'w', encoding='utf-8') as fh:
		json.dump(data, fh, indent=4, sort_keys=True)

def dump_to_unicode_file(filename, data):
	fh = codecs.open(filename, 'w', 'utf-8')
	fh.write(data)
	fh.close()

def dump_dict_to_csv_file(filename, dict):
	(pd.DataFrame.from_dict(data=dict, orient='index')
		.to_csv(filename, header=False, sep=';'))

def load_file_to_raw(path):
	try:
		with open(path, encoding='utf-8-sig') as fh:
			data = json.load(fh)
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
		return data
	except KeyError:
		print('Error: wrong file format (keys not found)')

def calculate_metrics(chat_data):
	metrics = _message_numerics(chat_data)
	dump_to_json_file('raw_metrics.json', metrics)
	ustr = u'' + metrics['A']['name'] + '\n'
	for e in metrics['A']['emojilist']:
		ustr += str(e[0]) + u' : ' + str(e[1]) + u'\n'
	ustr += metrics['B']['name'] + '\n'
	for e in metrics['B']['emojilist']:
		ustr += str(e[0]) + u' : ' + str(e[1]) + u'\n'
	dump_to_unicode_file('emojis.txt', ustr)

def calculate_graphs(chat_data):
	return _message_graphs(chat_data)

### MAIN
def main():
	if ( opts.indir is None or opts.name is None):
		parser.print_help() 
		exit(0)
	print('importing raw data...')
	raw_data = load_file_to_raw(opts.indir)
	chat_data = from_data_select_chat(raw_data, opts.name)
	print('calculating metrics...')
	#calculate_metrics(chat_data)
	print('generating graphs...')
	raw = calculate_graphs(chat_data)
	dump_dict_to_csv_file('raw_weekdays_person_' + raw['A']['name'] + '.csv', raw['A']['hourofday'])
	dump_dict_to_csv_file('raw_weekdays_person_' + raw['B']['name'] + '.csv', raw['B']['hourofday'])
	dump_dict_to_csv_file('raw_months_person_' + raw['A']['name'] + '.csv', raw['A']['months'])
	dump_dict_to_csv_file('raw_months_person_' + raw['B']['name'] + '.csv', raw['B']['months'])
	print('done')

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt as e:
		print('Aborted by KeyboardInterrupt')
		exit(0)
