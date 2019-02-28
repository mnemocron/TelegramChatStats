#! /usr/bin/python3

#_*_ coding: utf-8 _*_

'''
@file 		telegram-statistics.py
@author 	Simon Burkhardt - github.com/mnemocron
@date 		2018.10.01

Post about this code:
https://www.reddit.com/r/LongDistance/comments/9mgcol/oc_chat_statistics_from_telegram_using_python/

Inspiration:
https://www.reddit.com/r/LongDistance/comments/9jud8j/analysis_of_texts_from_a_long_distance/
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
parser.add_option('-d', '--date-max', 		dest='date', 	type='string', 	help='only count messages after date [YYYY-MM-DD]')
(opts, args) = parser.parse_args()

# Writes a dict in json format to a file
def dump_to_json_file(filename, data):
	with open(filename, 'w', encoding='utf-8') as fh:
		json.dump(data, fh, indent=4, sort_keys=True)

# writes data utf-8 encoded to a file
# important for emojis
def dump_to_unicode_file(filename, data):
	fh = codecs.open(filename, 'w', 'utf-8')
	fh.write(data)
	fh.close()

# writes a dict to a csv format

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

def calculate_metrics(chat_data, date_filter):
	metrics = _message_numerics(chat_data, date_filter)
	dump_to_json_file('raw_metrics.json', metrics)
	ustr = u'' + metrics['A']['name'] + '\n'
	for e in metrics['A']['emojilist']:
		ustr += str(e[0]) + u' : ' + str(e[1]) + u'\n'
	ustr += metrics['B']['name'] + '\n'
	for e in metrics['B']['emojilist']:
		ustr += str(e[0]) + u' : ' + str(e[1]) + u'\n'
	dump_to_unicode_file('emojis.txt', ustr)

def calculate_graphs(chat_data, date_filter):
	return _message_graphs(chat_data, date_filter)

# https://stackoverflow.com/questions/16870663/how-do-i-validate-a-date-string-format-in-python
def validate(date_text):
	try:
		datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		print('Incorrect date format, should be YYYY-MM-DD')
		exit(-1)

### MAIN
def main():
	if ( opts.indir is None or opts.name is None):
		parser.print_help() 
		exit(0)
	date_filter = '1970-01-01'
	if ( opts.date is not None):
		validate(opts.date)
		date_filter = opts.date
	print('importing raw data...')
	raw_data = load_file_to_raw(opts.indir)
	chat_data = from_data_select_chat(raw_data, opts.name)
	print('calculating metrics...')
	calculate_metrics(chat_data, date_filter)
	print('generating graphs...')
	raw = calculate_graphs(chat_data, date_filter)
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
