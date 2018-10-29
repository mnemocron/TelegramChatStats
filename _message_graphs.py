#! /usr/bin/python3

from collections import Counter
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import bokeh
import bokeh.plotting as bkh
from bokeh.core.properties import value
from bokeh.transform import dodge
import codecs
import csv

# https://flatuicolors.com/palette/es
colors = ['#34ace0','#ffb142']

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
	metrics['A']['frame_days'] = metrics['A']['series_days'].to_frame(name='frequency')
	metrics['B']['frame_days'] = metrics['B']['series_days'].to_frame(name='frequency')
#	metrics['A']['series_month'] = pd.Series(metrics['A']['months'])
#	metrics['B']['series_month'] = pd.Series(metrics['B']['months'])
#	metrics['A']['frame_months'] = metrics['A']['series_month'].to_frame(name='frequency')
#	metrics['B']['frame_months'] = metrics['B']['series_month'].to_frame(name='frequency')
	metrics['A']['frame_months'] = hacky_solution_to_fix_timedelta_dodge(metrics['A']['months'], -5)
	metrics['B']['frame_months'] = hacky_solution_to_fix_timedelta_dodge(metrics['B']['months'],  5)
	metrics['A']['series_weekdays'] = pd.Series(metrics['A']['weekdays'])
	metrics['B']['series_weekdays'] = pd.Series(metrics['B']['weekdays'])
	metrics['A']['frame_weekdays'] = metrics['A']['series_weekdays'].to_frame(name='frequency')
	metrics['B']['frame_weekdays'] = metrics['B']['series_weekdays'].to_frame(name='frequency')
	metrics['A']['series_hoursofday'] = pd.Series(metrics['A']['hourofday'])
	metrics['B']['series_hoursofday'] = pd.Series(metrics['B']['hourofday'])
	metrics['A']['frame_hoursofday'] = metrics['A']['series_hoursofday'].to_frame(name='frequency')
	metrics['B']['frame_hoursofday'] = metrics['B']['series_hoursofday'].to_frame(name='frequency')
	return metrics

'''
@input  months
@input  delta (int)    the x-offset in days
@output frame (frame)

This is used to shift monthly data on the time axis by a couple of days.
Used to display multiple vbars next to each other.
The bokeh.transforms.dodge method does not support offsets of type (datetime)
'''
def hacky_solution_to_fix_timedelta_dodge(months, delta):
	altered = {}
	for month in months:
		altered[month + timedelta(days=delta)] = altered.get(month + timedelta(days=delta), 0) + months.get(month, 0)
	series = pd.Series(altered)
	return series.to_frame(name='frequency')
		
# called by the main script
def _message_graphs(chat):
	metrics = _parse_chat(chat)

	filename = 'plot_days_' + metrics['A']['name'] + '.html'
	filename = ''.join([x for x in filename if ord(x) < 128]) # strip non-ascii characters
	histogram_days(filename, metrics['A']['frame_days'], metrics['A']['name'], colors[0])
	filename = 'plot_days_' + metrics['B']['name'] + '.html'
	filename = ''.join([x for x in filename if ord(x) < 128]) # strip non-ascii characters
	histogram_days(filename, metrics['B']['frame_days'], metrics['B']['name'], colors[1])
	# histogram_month_stacked('plot_month.html', data_months, metrics['A']['name'], metrics['B']['name'])
	histogram_month('plot_month.html', metrics)
	histogram_weekdays('plot_weekdays.html', metrics)
	histogram_hourofday('plot_hours.html', metrics)
	return metrics

'''
@input filename
@input data
@input namea
@input nameb

This method is old and currently not used. 
However it provides a different approach to display the data stacked instead of 
both person's bars next to each other.
Though I found this visualization to be more confusing and the data
between the two persons cannot easily be compared.
'''
# https://bokeh.pydata.org/en/latest/docs/user_guide/categorical.html
def histogram_month_stacked(filename, data, namea, nameb):
	bkh.reset_output()
	bkh.output_file(filename)
	##### STACKED BAR GRAPH for monthly data
	fig = bkh.figure(x_axis_type='datetime',
		title='Messages per Month',
		width=720, height=480)
	fig.vbar_stack([namea, nameb], x='index', 
		width=timedelta(days=20), 
		color=colors, source=data, 
		legend=[value(x) for x in [namea, nameb]])
	fig.xaxis.axis_label = 'Date'
	fig.yaxis.axis_label = 'Message count'
	bkh.show(fig)
	return

'''
@input filename
@input metrics (dict)
'''
def histogram_month(filename, metrics):
	bkh.reset_output()
	bkh.output_file(filename)
	data_months = {'index' : metrics['A']['frame_months'].index, metrics['A']['name'] : metrics['A']['frame_months'].frequency,
		metrics['B']['name'] : metrics['B']['frame_months'].frequency}
	fig = bkh.figure(x_axis_type='datetime',
		title='Monthly message count over time per person', 
		width=720, height=480)
	fig.vbar(x='index', 
		top='frequency', width=timedelta(days=10), 
		source=metrics['A']['frame_months'], 
		color=colors[0], legend=metrics['A']['name'])
	fig.vbar(x='index', 
		top='frequency', width=timedelta(days=10), 
		source=metrics['B']['frame_months'], 
		color=colors[1], legend=metrics['B']['name'])
	fig.xaxis.axis_label = 'Date'
	fig.yaxis.axis_label = 'Message count'
	bkh.show(fig)
	return

'''
@input filename
@input frame
@imput name of the person
@input color for this person
'''
def histogram_days(filename, frame, name, color):
	bkh.reset_output()
	bkh.output_file(filename)
	fig = bkh.figure(x_axis_type='datetime',
		title='Message count per day of ' + name,
		width=720, height=480)
	fig.line(frame.index, frame.frequency, color=color, line_width=3)
	fig.xaxis.axis_label = 'Date'
	fig.yaxis.axis_label = 'Frequency'
	bkh.show(fig)
	return

'''
@input filename
@input metrics (dict)
'''
def histogram_weekdays(filename, metrics):
	bkh.reset_output()
	bkh.output_file(filename)
	weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
	fig = bkh.figure(x_range=weekdays, 
		title='Message count distribution over weekdays', 
		width=720, height=480)
	fig.vbar(x=dodge('index', 0.35, range=fig.x_range), 
		top='frequency', width=0.3, source=metrics['A']['frame_weekdays'], 
		color=colors[0], legend=metrics['A']['name'])
	fig.vbar(x=dodge('index', 0.65, range=fig.x_range), 
		top='frequency', width=0.3, source=metrics['B']['frame_weekdays'], 
		color=colors[1], legend=metrics['B']['name'])
	fig.xaxis.axis_label = 'Weekday'
	fig.yaxis.axis_label = 'Message count'
	bkh.show(fig)
	return

'''
@input filename
@input metrics (dict)
'''
def histogram_hourofday(filename, metrics):
	bkh.reset_output()
	bkh.output_file(filename)
	hours = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']
	fig = bkh.figure(x_range=hours, 
		title='Message count distribution throughout the day', 
		width=1280, height=480)
	fig.vbar(x=dodge('index', 0.35, range=fig.x_range), 
		top='frequency', width=0.3, source=metrics['A']['frame_hoursofday'], 
		color=colors[0], legend=metrics['A']['name'])
	fig.vbar(x=dodge('index', 0.65, range=fig.x_range), 
		top='frequency', width=0.3, source=metrics['B']['frame_hoursofday'], 
		color=colors[1], legend=metrics['B']['name'])
	fig.xaxis.axis_label = 'Time'
	fig.yaxis.axis_label = 'Message count'
	bkh.show(fig)
	return
