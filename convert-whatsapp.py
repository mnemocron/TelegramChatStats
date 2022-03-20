#! /usr/bin/python3

# _*_ coding: utf-8 _*_

"""
@file 		print-results.py
@author 	Simon Burkhardt - github.com/mnemocron
@date 		2018.10.10

This file prints the resulting numbers to the command line

Post about this code:
https://www.reddit.com/r/LongDistance/comments/9mgcol/oc_chat_statistics_from_telegram_using_python/

Inspiration:
https://www.reddit.com/r/LongDistance/comments/9jud8j/analysis_of_texts_from_a_long_distance/
"""

from __future__ import print_function

import sys
import os
import optparse
import json
import re
from pprint import pprint

parser = optparse.OptionParser("convert-whatsapp.py")
parser.add_option(
    "-i", "--input-file", dest="indir", type="string", help="chat history file"
)
(opts, args) = parser.parse_args()

dateformat = "EU"
dateseprarator = "."

# Writes a dict in json format to a file
def dump_to_json_file(filename, data):
    with open(filename, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, sort_keys=True)


def load_file_to_srting(filename):
    with open(filename, "r") as fh:
        data = fh.read()
    return data


def split_string_to_messages(string):
    global dateseprarator
    regex_matcher = "^\\d{2}.\\d{2}.\\d{2}, \\d{2}:\\d{2} - "
    if "/" in string[:8]:
        dateformat = "US"
        dateseprarator = "/"
        regex_matcher = "^\\d{2}/\\d{2}/\\d{4}, \\d{2}:\\d{2} - "
        print(
            "detected mm.dd.yy dateformat (using dateseprarator: "
            + dateseprarator
            + ")"
        )
    else:
        print("using dd.mm.yy dateformat")
    messages = []
    for line in string.split("\n"):
        if re.match(regex_matcher, line):
            messages.append(line)
        else:
            messages[-1] += "\n" + line
    return messages


def to_telegram_format(messages):
    data = {}
    data["chats"] = {}
    data["chats"]["about"] = "This page lists all chats from this export."
    data["chats"]["list"] = []
    data["chats"]["list"].append({})
    data["chats"]["list"][0]["name"] = (
        messages[0].split("- ")[1].split(":")[0]
    )  # name of the first message
    data["chats"]["list"][0]["type"] = "personal_chat"
    data["chats"]["list"][0]["messages"] = []

    id = 0
    for message in messages:
        media = False
        try:
            date_time = message.split("-")[0].replace(" ", "")
            date_ = date_time.split(",")[0]
            if dateseprarator == ".":
                date_y = 2000 + int(date_.split(".")[-1])
                date_m = int(date_.split(".")[1])
                date_d = int(date_.split(".")[0])
            else:
                date_y = int(date_.split("/")[-1])
                date_m = int(date_.split("/")[1])
                date_d = int(date_.split("/")[0])
            time_ = date_time.split(",")[1]
            time_h = time_.split(":")[0]
            time_m = time_.split(":")[1]
            name = message.split("- ")[1].split(":")[0]
            text = message.split("- ", 1)[1].split(": ", 1)[1]
        except Exception as e:
            name = "automatic"
            text = ""
        if "<medi" in text.lower():
            media = True
        data["chats"]["list"][0]["messages"].append({})
        data["chats"]["list"][0]["messages"][-1]["id"] = id
        data["chats"]["list"][0]["messages"][-1]["type"] = "message"
        data["chats"]["list"][0]["messages"][-1]["date"] = (
            str(date_y).zfill(2)
            + "-"
            + str(date_m).zfill(2)
            + "-"
            + str(date_d).zfill(2)
            + "T"
            + str(time_h).zfill(2)
            + ":"
            + str(time_m).zfill(2)
            + ":00"
        )  # 2017-06-12T21:30:09
        data["chats"]["list"][0]["messages"][-1]["edited"] = "1970-01-01T01:00:00"
        data["chats"]["list"][0]["messages"][-1]["from"] = name
        data["chats"]["list"][0]["messages"][-1]["text"] = text
        data["chats"]["list"][0]["messages"][-1][
            "photo"
        ] = "placeholder/path/to/photo.jpg"
        id += 1
    return data


### MAIN
def main():
    if opts.indir is None:
        parser.print_help()
        exit(0)
    raw = load_file_to_srting(opts.indir)
    messages = split_string_to_messages(raw)
    formated = to_telegram_format(messages)
    dump_to_json_file("whatsapp-result.json", formated)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print("Aborted by KeyboardInterrupt")
        exit(0)
