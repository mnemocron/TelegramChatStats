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


colors = ['#f62459', '#f4b350']

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
	return metrics


def hacky_solution_to_fix_timedelta_dodge(months, delta):
	altered = {}
	for month in months:
		altered[month + timedelta(days=delta)] = altered.get(month + timedelta(days=delta), 0) + months.get(month, 0)
	series = pd.Series(altered)
	return series.to_frame(name='frequency')
		


def _message_graphs(chat):
	metrics = _parse_chat(chat)

	histogram_days('plot_days_' + metrics['A']['name'] + '.html', metrics['A']['frame_days'], metrics['A']['name'], colors[0])
	histogram_days('plot_days_' + metrics['B']['name'] + '.html', metrics['B']['frame_days'], metrics['B']['name'], colors[1])
	# histogram_month_stacked('plot_month.html', data_months, metrics['A']['name'], metrics['B']['name'])
	histogram_month('plot_month.html', metrics)
	histogram_weekdays('plot_weekdays.html', metrics)
	return metrics



# https://bokeh.pydata.org/en/latest/docs/user_guide/categorical.html
def histogram_month_stacked(filename, data, namea, nameb):
	bkh.reset_output()
	bkh.output_file(filename)
	##### STACKED BAR GRAPH for monthly data
	fig = bkh.figure(x_axis_type='datetime',
		title='Messages per Month',
		width=1280, height=720)
	fig.vbar_stack([namea, nameb], x='index', 
		width=timedelta(days=20), 
		color=colors, source=data, 
		legend=[value(x) for x in [namea, nameb]])
	fig.xaxis.axis_label = 'Date'
	fig.yaxis.axis_label = 'Message count'
	bkh.show(fig)
	return



def histogram_month(filename, metrics):
	bkh.reset_output()
	bkh.output_file(filename)
	data_months = {'index' : metrics['A']['frame_months'].index, metrics['A']['name'] : metrics['A']['frame_months'].frequency,
		metrics['B']['name'] : metrics['B']['frame_months'].frequency}
	fig = bkh.figure(x_axis_type='datetime',
		title='Message count over week', 
		width=1280, height=720)
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



def histogram_days(filename, frame, name, color):
	bkh.reset_output()
	bkh.output_file(filename)
	fig = bkh.figure(x_axis_type='datetime',
		title='Message count per day of ' + name,
		width=1280, height=720)
	fig.line(frame.index, frame.frequency, color=color, line_width=3)
	fig.xaxis.axis_label = 'Date'
	fig.yaxis.axis_label = 'Frequency'
	bkh.show(fig)
	return



def histogram_weekdays(filename, metrics):
	bkh.reset_output()
	bkh.output_file(filename)
	weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
	fig = bkh.figure(x_range=weekdays, 
		title='Message count over week', 
		width=1280, height=720)
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

