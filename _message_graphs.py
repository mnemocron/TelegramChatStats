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
colors = ["#34ace0", "#ffb142"]
colors = ["#686de0", "#ffbe76"]


def count_occurrences(message, wordlist):
    count = 0
    for substring in wordlist:
        count += message.lower().count(substring)
    return count


def _parse_chat(chat, date_filter, wordlist):
    metrics = {}
    metrics["A"] = {}
    metrics["B"] = {}
    metrics["A"]["days"] = {}
    metrics["B"]["days"] = {}
    metrics["A"]["months"] = {}
    metrics["B"]["months"] = {}
    metrics["A"]["months_chars"] = {}
    metrics["B"]["months_chars"] = {}
    metrics["A"]["weekdays"] = {}
    metrics["B"]["weekdays"] = {}
    metrics["A"]["hourofday"] = {}
    metrics["B"]["hourofday"] = {}
    metrics["A"]["monthly_n_replied"] = {}
    metrics["B"]["monthly_n_replied"] = {}
    metrics["A"]["monthly_time_to_reply"] = {}
    metrics["B"]["monthly_time_to_reply"] = {}
    metrics["A"]["monthly_avg_reply_time"] = {}
    metrics["B"]["monthly_avg_reply_time"] = {}
    metrics["A"]["monthly_pictures"] = {}
    metrics["B"]["monthly_pictures"] = {}
    metrics["A"]["monthly_calls"] = {}
    metrics["B"]["monthly_calls"] = {}
    metrics["A"]["monthly_word_occurrence"] = {}
    metrics["B"]["monthly_word_occurrence"] = {}
    metrics["A"]["monthly_call_duration"] = {}
    metrics["B"]["monthly_call_duration"] = {}
    # person A is the 2nd message (1st can be "joined telegram" which has no "from" key)
    metrics["A"]["name"] = chat["messages"][1]["from"]
    metrics["A"]["call_hourofday"] = {}
    metrics["B"]["call_hourofday"] = {}
    previous_message = {}
    oldest_date = datetime.strptime(date_filter, "%Y-%m-%d")

    for message in chat["messages"]:
        if message["type"] == "unsupported":
            continue
        person = "B"
        if "from" in message:
            if metrics["A"]["name"] in message["from"]:
                person = "A"
        elif "actor" in message:
            if metrics["A"]["name"] in message["actor"]:
                person = "A"
        date_obj = datetime.strptime(message["date"], "%Y-%m-%dT%H:%M:%S")
        # check if message needs to be reviewed based on date
        if date_obj >= oldest_date:
            month_str = str(date_obj.year) + "-" + str(date_obj.month) + "-1"
            month_obj = datetime.strptime(month_str, "%Y-%m-%d")
            # text and media
            if message["type"] == "message":
                metrics[person]["name"] = message["from"]
                metrics[person]["months"][month_obj] = (
                    metrics[person]["months"].get(month_obj, 0) + 1
                )
                metrics[person]["days"][date_obj.date()] = (
                    metrics[person]["days"].get(date_obj.date(), 0) + 1
                )
                metrics[person]["weekdays"][date_obj.weekday()] = (
                    metrics[person]["weekdays"].get(date_obj.weekday(), 0) + 1
                )
                metrics[person]["hourofday"][date_obj.hour] = (
                    metrics[person]["hourofday"].get(date_obj.hour, 0) + 1
                )
                if type(message["text"]) is list:  # multiple elements in one message
                    for line in message["text"]:
                        if type(line) is str:
                            # count characters
                            metrics[person]["months_chars"][month_obj] = metrics[
                                person
                            ]["months_chars"].get(month_obj, 0) + len(line)
                            # check if words occurr in message
                            metrics[person]["monthly_word_occurrence"][
                                month_obj
                            ] = metrics[person]["monthly_word_occurrence"].get(
                                month_obj, 0
                            ) + count_occurrences(
                                line, wordlist
                            )
                elif type(message["text"]) is str:
                    # count characters
                    metrics[person]["months_chars"][month_obj] = metrics[person][
                        "months_chars"
                    ].get(month_obj, 0) + len(message["text"])
                    # check if words occurr in message
                    metrics[person]["monthly_word_occurrence"][month_obj] = metrics[
                        person
                    ]["monthly_word_occurrence"].get(month_obj, 0) + count_occurrences(
                        message["text"], wordlist
                    )
                if "from" in previous_message:
                    if not (previous_message["from"] == message["from"]):
                        replytime = (
                            datetime.strptime(message["date"], "%Y-%m-%dT%H:%M:%S")
                            - datetime.strptime(
                                previous_message["date"], "%Y-%m-%dT%H:%M:%S"
                            )
                        ).total_seconds()
                        metrics[person]["monthly_n_replied"][month_obj] = (
                            metrics[person]["monthly_n_replied"].get(month_obj, 0) + 1
                        )
                        metrics[person]["monthly_time_to_reply"][month_obj] = (
                            metrics[person]["monthly_time_to_reply"].get(month_obj, 0)
                            + replytime
                        )
                        avg_time = metrics[person]["monthly_time_to_reply"].get(
                            month_obj, 0
                        ) / metrics[person]["monthly_n_replied"].get(month_obj, 0)
                        metrics[person]["monthly_avg_reply_time"][month_obj] = avg_time
                if "photo" in message:
                    metrics[person]["monthly_pictures"][month_obj] = (
                        metrics[person]["monthly_pictures"].get(month_obj, 0) + 1
                    )
            # calls
            elif message["type"] == "service":
                if message["action"] == "phone_call":
                    if (
                        "duration_seconds" in message
                    ):  # only count if the call was answered
                        metrics["A"]["monthly_call_duration"][month_obj] = metrics["A"][
                            "monthly_call_duration"
                        ].get(month_obj, 0) + int(message["duration_seconds"])
                        metrics["A"]["monthly_calls"][month_obj] = (
                            metrics["A"]["monthly_calls"].get(month_obj, 0) + 1
                        )
                        metrics["A"]["call_hourofday"][date_obj.hour] = (
                            metrics["A"]["call_hourofday"].get(date_obj.hour, 0) + 1
                        )
            previous_message = message

    metrics["B"]["monthly_call_duration"] = metrics["A"]["monthly_call_duration"]
    metrics["B"]["monthly_calls"] = metrics["A"]["monthly_calls"]
    metrics["B"]["call_hourofday"] = metrics["A"]["call_hourofday"]

    metrics["A"]["day_series"] = pd.Series(metrics["A"]["days"])
    metrics["B"]["day_series"] = pd.Series(metrics["B"]["days"])
    metrics["A"]["series_days"] = pd.Series(metrics["A"]["days"])
    metrics["B"]["series_days"] = pd.Series(metrics["B"]["days"])
    metrics["A"]["frame_days"] = metrics["A"]["series_days"].to_frame(name="frequency")
    metrics["B"]["frame_days"] = metrics["B"]["series_days"].to_frame(name="frequency")
    # 	metrics['A']['series_month'] = pd.Series(metrics['A']['months'])
    # 	metrics['B']['series_month'] = pd.Series(metrics['B']['months'])
    # 	metrics['A']['frame_months'] = metrics['A']['series_month'].to_frame(name='frequency')
    # 	metrics['B']['frame_months'] = metrics['B']['series_month'].to_frame(name='frequency')
    metrics["A"]["frame_months"] = hacky_solution_to_fix_timedelta_dodge(
        metrics["A"]["months"], -5
    )
    metrics["B"]["frame_months"] = hacky_solution_to_fix_timedelta_dodge(
        metrics["B"]["months"], 5
    )
    metrics["A"]["frame_months_chars"] = hacky_solution_to_fix_timedelta_dodge(
        metrics["A"]["months_chars"], -5
    )
    metrics["B"]["frame_months_chars"] = hacky_solution_to_fix_timedelta_dodge(
        metrics["B"]["months_chars"], 5
    )
    metrics["A"]["frame_months_reply_time"] = hacky_solution_to_fix_timedelta_dodge(
        metrics["A"]["monthly_avg_reply_time"], -5
    )
    metrics["B"]["frame_months_reply_time"] = hacky_solution_to_fix_timedelta_dodge(
        metrics["B"]["monthly_avg_reply_time"], 5
    )
    metrics["A"]["frame_months_pictures"] = hacky_solution_to_fix_timedelta_dodge(
        metrics["A"]["monthly_pictures"], -5
    )
    metrics["B"]["frame_months_pictures"] = hacky_solution_to_fix_timedelta_dodge(
        metrics["B"]["monthly_pictures"], 5
    )
    metrics["A"]["frame_months_calls"] = hacky_solution_to_fix_timedelta_dodge(
        metrics["A"]["monthly_calls"], -5
    )
    metrics["B"]["frame_months_calls"] = hacky_solution_to_fix_timedelta_dodge(
        metrics["B"]["monthly_calls"], 5
    )
    metrics["A"]["frame_months_call_duration"] = hacky_solution_to_fix_timedelta_dodge(
        metrics["A"]["monthly_call_duration"], -5
    )
    metrics["B"]["frame_months_call_duration"] = hacky_solution_to_fix_timedelta_dodge(
        metrics["B"]["monthly_call_duration"], 5
    )
    metrics["A"][
        "frame_months_word_occurrence"
    ] = hacky_solution_to_fix_timedelta_dodge(
        metrics["A"]["monthly_word_occurrence"], -5
    )
    metrics["B"][
        "frame_months_word_occurrence"
    ] = hacky_solution_to_fix_timedelta_dodge(
        metrics["B"]["monthly_word_occurrence"], 5
    )
    metrics["A"]["series_weekdays"] = pd.Series(metrics["A"]["weekdays"])
    metrics["B"]["series_weekdays"] = pd.Series(metrics["B"]["weekdays"])
    metrics["A"]["frame_weekdays"] = metrics["A"]["series_weekdays"].to_frame(
        name="frequency"
    )
    metrics["B"]["frame_weekdays"] = metrics["B"]["series_weekdays"].to_frame(
        name="frequency"
    )
    metrics["A"]["series_hoursofday"] = pd.Series(metrics["A"]["hourofday"])
    metrics["B"]["series_hoursofday"] = pd.Series(metrics["B"]["hourofday"])
    metrics["A"]["frame_hoursofday"] = metrics["A"]["series_hoursofday"].to_frame(
        name="frequency"
    )
    metrics["B"]["frame_hoursofday"] = metrics["B"]["series_hoursofday"].to_frame(
        name="frequency"
    )
    metrics["A"]["series_call_hoursofday"] = pd.Series(metrics["A"]["call_hourofday"])
    metrics["B"]["series_call_hoursofday"] = pd.Series(metrics["B"]["call_hourofday"])
    metrics["A"]["frame_call_hoursofday"] = metrics["A"][
        "series_call_hoursofday"
    ].to_frame(name="frequency")
    metrics["B"]["frame_call_hoursofday"] = metrics["B"][
        "series_call_hoursofday"
    ].to_frame(name="frequency")
    return metrics


"""
@input  months
@input  delta (int)    the x-offset in days
@output frame (frame)

This is used to shift monthly data on the time axis by a couple of days.
Used to display multiple vbars next to each other.
The bokeh.transforms.dodge method does not support offsets of type (datetime)
"""


def hacky_solution_to_fix_timedelta_dodge(months, delta):
    altered = {}
    for month in months:
        altered[month + timedelta(days=delta)] = altered.get(
            month + timedelta(days=delta), 0
        ) + months.get(month, 0)
    series = pd.Series(altered)
    return series.to_frame(name="frequency")


# called by the main script
def _message_graphs(chat, date_filter, wordlist):
    metrics = _parse_chat(chat, date_filter, wordlist)

    # commented out because this graph is visually unpleasing and not very

    # filename = 'plot_days_' + metrics['A']['name'] + '.html'
    # filename = ''.join([x for x in filename if ord(x) < 128]) # strip non-ascii characters
    # histogram_days(filename, metrics['A']['frame_days'], metrics['A']['name'], colors[0])
    # filename = 'plot_days_' + metrics['B']['name'] + '.html'
    # filename = ''.join([x for x in filename if ord(x) < 128]) # strip non-ascii characters
    # histogram_days(filename, metrics['B']['frame_days'], metrics['B']['name'], colors[1])
    # histogram_month_stacked('plot_month.html', data_months, metrics['A']['name'], metrics['B']['name'])
    histogram_month(
        "plot_month.html",
        metrics,
        "frame_months",
        "Monthly message count over time per person",
        "Message count",
    )
    histogram_month(
        "plot_month_replytime.html",
        metrics,
        "frame_months_reply_time",
        "Average monthly reply delay time over time per person",
        "average delay in seconds",
    )
    histogram_month(
        "plot_month_calls.html",
        metrics,
        "frame_months_calls",
        "Number of calls per month (both persons)",
        "Amount",
    )
    histogram_month(
        "plot_month_call_time.html",
        metrics,
        "frame_months_call_duration",
        "Total time on call per month (both persons)",
        "total time in seconds",
    )
    histogram_month(
        "plot_month_photos.html",
        metrics,
        "frame_months_pictures",
        "Monthly photo count over time per person",
        "number of photos sent",
    )
    histogram_month(
        "plot_month_word_occurrence.html",
        metrics,
        "frame_months_word_occurrence",
        "Occurrences of the strings: [" + ";\n".join(wordlist) + "]",
        "number of occurrences",
    )
    histogram_weekdays("plot_weekdays.html", metrics)

    histogram_hourofday(
        "plot_hoursofday_messages.html",
        metrics,
        "frame_hoursofday",
        "Message count distribution throughout the day",
        "message count",
    )
    histogram_hourofday(
        "plot_hoursofday_calls.html",
        metrics,
        "frame_call_hoursofday",
        "Call distribution throughout the day",
        "number of calls",
    )

    histogram_month_chars("plot_month_characters.html", metrics)
    return metrics


"""
@input filename
@input data
@input namea
@input nameb

This method is currently not used. 
However it provides a different approach to display the data stacked instead of 
both person's bars next to each other.
Though I found this visualization to be more confusing and the data
between the two persons cannot easily be compared.
"""
# https://bokeh.pydata.org/en/latest/docs/user_guide/categorical.html
def histogram_month_stacked(filename, data, namea, nameb):
    bkh.reset_output()
    bkh.output_file(filename, title=filename)
    ##### STACKED BAR GRAPH for monthly data
    fig = bkh.figure(
        x_axis_type="datetime", title="Messages per Month", width=720, height=480
    )
    fig.vbar_stack(
        [namea, nameb],
        x="index",
        width=timedelta(days=20),
        color=colors,
        source=data,
        legend=[value(x) for x in [namea, nameb]],
    )
    fig.xaxis.axis_label = "Date"
    fig.yaxis.axis_label = "Message count"
    bkh.show(fig)
    return


"""
@input filename
@input metrics (dict)
"""


def histogram_month_chars(filename, metrics):
    bkh.reset_output()
    bkh.output_file(filename, title=filename)
    data_months = {
        "index": metrics["A"]["frame_months_chars"].index,
        metrics["A"]["name"]: metrics["A"]["frame_months_chars"].frequency,
        metrics["B"]["name"]: metrics["B"]["frame_months_chars"].frequency,
    }
    fig = bkh.figure(
        x_axis_type="datetime",
        title="Monthly character count over time per person",
        width=720,
        height=480,
    )
    fig.vbar(
        x="index",
        top="frequency",
        width=timedelta(days=10),
        source=metrics["A"]["frame_months_chars"],
        color=colors[0],
        legend=metrics["A"]["name"],
    )
    fig.vbar(
        x="index",
        top="frequency",
        width=timedelta(days=10),
        source=metrics["B"]["frame_months_chars"],
        color=colors[1],
        legend=metrics["B"]["name"],
    )
    fig.xaxis.axis_label = "Date"
    fig.yaxis.axis_label = "Number of characters"
    bkh.show(fig)
    return


"""
@input filename
@input metrics (dict)
@input key
@input title_str
@input ylabel
"""


def histogram_month(filename, metrics, key, title_str, ylabel):
    bkh.reset_output()
    bkh.output_file(filename, title=filename)
    data_months = {
        "index": metrics["A"][key].index,
        metrics["A"]["name"]: metrics["A"]["frame_months"].frequency,
        metrics["B"]["name"]: metrics["B"][key].frequency,
    }
    fig = bkh.figure(x_axis_type="datetime", title=title_str, width=720, height=480)
    fig.vbar(
        x="index",
        top="frequency",
        width=timedelta(days=10),
        source=metrics["A"][key],
        color=colors[0],
        legend=metrics["A"]["name"],
    )
    fig.vbar(
        x="index",
        top="frequency",
        width=timedelta(days=10),
        source=metrics["B"][key],
        color=colors[1],
        legend=metrics["B"]["name"],
    )
    fig.xaxis.axis_label = "Date"
    fig.yaxis.axis_label = ylabel
    bkh.show(fig)
    return


"""
@input filename
@input frame
@imput name of the person
@input color for this person
"""


def histogram_days(filename, frame, name, color):
    bkh.reset_output()
    bkh.output_file(filename, title=filename)
    fig = bkh.figure(
        x_axis_type="datetime",
        title="Message count per day of " + name,
        width=720,
        height=480,
    )
    fig.line(frame.index, frame.frequency, color=color, line_width=3)
    fig.xaxis.axis_label = "Date"
    fig.yaxis.axis_label = "Frequency"
    bkh.show(fig)
    return


"""
@input filename
@input metrics (dict)
"""


def histogram_weekdays(filename, metrics):
    bkh.reset_output()
    bkh.output_file(filename, title=filename)
    weekdays = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    fig = bkh.figure(
        x_range=weekdays,
        title="Message distribution over weekdays",
        width=720,
        height=480,
    )
    fig.vbar(
        x=dodge("index", 0.35, range=fig.x_range),
        top="frequency",
        width=0.3,
        source=metrics["A"]["frame_weekdays"],
        color=colors[0],
        legend=metrics["A"]["name"],
    )
    fig.vbar(
        x=dodge("index", 0.65, range=fig.x_range),
        top="frequency",
        width=0.3,
        source=metrics["B"]["frame_weekdays"],
        color=colors[1],
        legend=metrics["B"]["name"],
    )
    fig.xaxis.axis_label = "Weekday"
    fig.yaxis.axis_label = "Message count"
    bkh.show(fig)
    return


"""
@input filename
@input metrics (dict)
@input key
@input title_str
@input ylabel
"""


def histogram_hourofday(filename, metrics, key, title_str, ylabel):
    bkh.reset_output()
    bkh.output_file(filename, title=filename)
    hours = [
        "00:00",
        "01:00",
        "02:00",
        "03:00",
        "04:00",
        "05:00",
        "06:00",
        "07:00",
        "08:00",
        "09:00",
        "10:00",
        "11:00",
        "12:00",
        "13:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00",
        "19:00",
        "20:00",
        "21:00",
        "22:00",
        "23:00",
    ]
    fig = bkh.figure(x_range=hours, title=title_str, width=1280, height=480)
    fig.vbar(
        x=dodge("index", 0.35, range=fig.x_range),
        top="frequency",
        width=0.3,
        source=metrics["A"][key],
        color=colors[0],
        legend=metrics["A"]["name"],
    )
    fig.vbar(
        x=dodge("index", 0.65, range=fig.x_range),
        top="frequency",
        width=0.3,
        source=metrics["B"][key],
        color=colors[1],
        legend=metrics["B"]["name"],
    )
    fig.xaxis.axis_label = "Time"
    fig.yaxis.axis_label = ylabel
    bkh.show(fig)
    return
