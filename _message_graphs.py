#! /usr/bin/python3

from collections import Counter
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import bokeh
import bokeh.plotting as bkh
from bokeh.core.properties import value
import codecs
import csv

def _parse_chat(chat):
	metrics = {}
	metrics['A'] = {}
	metrics['B'] = {}
	metrics['A']['days'] = {}
	metrics['B']['days'] = {}
	metrics['A']['months'] = {}
	metrics['B']['months'] = {}
	metrics['A']['weekdays'] = {}
	metrics['B']['weekdays'] = {}
	metrics['A']['hourofday'] = {}
	metrics['B']['hourofday'] = {}
	metrics['A']['name'] = chat['messages'][0]['from']
	for message in chat['messages']:
		if(message['type'] == 'message'):
			person = 'B'
			if metrics['A']['name'] in message['from']:
				person = 'A'
			metrics[person]['name'] = message['from']
			date_obj = datetime.strptime(message['date'], '%Y-%m-%dT%H:%M:%S')
			month_str = str(date_obj.year) + '-' + str(date_obj.month) + '-1'
			month_obj = datetime.strptime(month_str, '%Y-%m-%d')
			metrics[person]['months'][month_obj] = metrics[person]['months'].get(month_obj, 0) + 1
			metrics[person]['days'][date_obj.date()] = metrics[person]['days'].get(date_obj.date(), 0) + 1
			metrics[person]['weekdays'][date_obj.weekday()] = metrics[person]['weekdays'].get(date_obj.weekday(), 0) + 1
			metrics[person]['hourofday'][date_obj.hour] = metrics[person]['hourofday'].get(date_obj.hour, 0) + 1
	metrics['A']['day_series'] = pd.Series(metrics['A']['days'])
	metrics['B']['day_series'] = pd.Series(metrics['B']['days'])

	metrics['A']['series_days'] = pd.Series(metrics['A']['days'])
	metrics['B']['series_days'] = pd.Series(metrics['B']['days'])
	metrics['A']['series_month'] = pd.Series(metrics['A']['months'])
	metrics['B']['series_month'] = pd.Series(metrics['B']['months'])
	metrics['A']['frame_days'] = metrics['A']['series_days'].to_frame(name='frequency')
	metrics['B']['frame_days'] = metrics['B']['series_days'].to_frame(name='frequency')
	metrics['A']['frame_months'] = metrics['A']['series_month'].to_frame(name='frequency')
	metrics['B']['frame_months'] = metrics['B']['series_month'].to_frame(name='frequency')
	return metrics

def _message_graphs(chat):
	metrics = _parse_chat(chat)

	data_months = {'index' : metrics['A']['frame_months'].index, metrics['A']['name'] : metrics['A']['frame_months'].frequency,
	 metrics['B']['name'] : metrics['B']['frame_months'].frequency}

	histogram_days('plot_days_' + metrics['A']['name'] + '.html', metrics['A']['frame_days'], metrics['A']['name'])
	histogram_days('plot_days_' + metrics['B']['name'] + '.html', metrics['B']['frame_days'], metrics['B']['name'])
	histogram_month_stacked('plot_month.html', data_months, metrics['A']['name'], metrics['B']['name'])
	histogram_weekdays('plot_weekdays.html', )
	return metrics

# https://bokeh.pydata.org/en/latest/docs/user_guide/categorical.html
def histogram_month_stacked(filename, data, namea, nameb):
	bkh.reset_output()
	bkh.output_file(filename)
	##### STACKED BAR GRAPH for monthly data
	colors = ["#f62459", "#f4b350"]
	# dict containing all the monthly data
	# 'index' : [2018-01, 2018-02, 2018-03]
	# 'name A' : [300, 234, 67]
	# 'name B' : [290, 210, 89]
	fig = bkh.figure(x_axis_type="datetime",
					title="Messages per Month",
					width=1280, height=720)
	fig.vbar_stack([namea, nameb], x='index', width=timedelta(days=20), color=colors, source=data, legend=[value(x) for x in [namea, nameb]])
	fig.xaxis.axis_label = "Date"
	fig.yaxis.axis_label = "Number of Messages"
	bkh.show(fig)

def histogram_month(filename, data, namea, nameb):
	bkh.reset_output()
	bkh.output_file(filename)
	colors = ["#f62459", "#f4b350"]

def histogram_days(filename, frame, name):
	bkh.reset_output()
	bkh.output_file(filename)
	##### LINE GRAPH for daily data
	fig = bkh.figure(x_axis_type="datetime",
					title="Message count per day of " + name,
					width=1280, height=720)
	fig.line(frame.index, frame.frequency)
	fig.xaxis.axis_label = "Date"
	fig.yaxis.axis_label = "Frequency"
	bkh.show(fig)

def histogram_weekdays(filename, metrics):
	bkh.reset_output()
	bkh.output_file(filename)
	metrics['A']['weekdays']

	weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']



	return

