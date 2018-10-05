#! /usr/bin/python3

#_*_ coding: utf-8 _*_

'''
@file 		telegram-statistics.py
@author 	Simon Burkhardt - github.com/mnemocron
@date 		2018.10.01
'''

from __future__ import print_function

import sys
import os
import optparse
import re
import json
import numpy as np   # install with pip3
import pandas as pd  # install with pip3
import bokeh         # install with pip3
from pprint import pprint
from collections import Counter
from datetime import datetime
from datetime import timedelta
import bokeh.plotting as bkh
from bokeh.core.properties import value
import codecs

from _message_numerics import _message_numerics

parser = optparse.OptionParser('telegram-stats')
parser.add_option('-i', '--input-file', 	dest='indir', 	type='string', 	help='chat history file')
parser.add_option('-n', '--name', 			dest='name', 	type='string', 	help='name of the person')
(opts, args) = parser.parse_args()

def dump_to_json_file(filename, data):
	with open(filename, 'w', encoding='utf-8') as fh:
		json.dump(data, fh, indent=4)

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

### MAIN
def main():
	if ( opts.indir is None or opts.name is None):
		parser.print_help() 
		exit(0)
	raw_data = load_file_to_raw(opts.indir)
	chat_data = from_data_select_chat(raw_data, opts.name)
	metrics = _message_numerics(chat_data)
	dump_to_json_file('metrics.json', metrics)

	print('success')

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt as e:
		print('Aborted by KeyboardInterrupt')
		exit(0)
