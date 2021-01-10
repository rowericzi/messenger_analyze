#!/usr/bin/env python
"""
	messenger-analyze: a program for analysis of Facebook Messenger messages
	stored in JSON format.
	Copyright (C) 2021 Ryszard Jezierski

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import sys
import os
import json
import math
import re
from itertools import islice
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
matplotlib.use('SVG')
import numpy as np
import pandas as pd
import pprint

"""
	function converting every string in an object
	from byte-encoded unicode to proper
	unicode characters
"""
def convert(obj, enc):
	if isinstance(obj, str):
		return obj.encode('latin1').decode(enc)
	if isinstance(obj, (list, tuple)):
		return [convert(item, enc) for item in obj]
	if isinstance(obj, dict):
		return {convert(key, enc) : convert(val, enc)
			for key, val in obj.items()}
	else: return obj

def load_json_files(dir):
	json_files = [ file for file in os.listdir(dir) if file.endswith(".json") ]
	json_list = []

	for file in json_files:
		with open(os.path.join(dir,file), "r") as f:
			json_list.append(json.loads(f.read()))

	if len(json_list) > 1:
		for i in range(0, len(json_list)):
			json_list[0]['messages'] += json_list[i]['messages']

	messages = convert(json_list[0], 'utf-8')
	del json_list
	return messages

def plot_messages(messages, N):
	timestamps = [ x['timestamp_ms'] for x in messages['messages'] ]
	timestamps.sort()
	day_timestamps = [ math.floor(mdates.epoch2num(t/1000)) for t in timestamps ]
	xval = [ x for x in range(day_timestamps[0], day_timestamps[-1] + 1) ]
	values = [0]*len(xval)

	for t in day_timestamps:
		values[t - day_timestamps[0]] += 1

	if N > 1:
		values_moving_avg = pd.Series(values).rolling(window=N).mean().iloc[N-1:].values
	else:
		values_moving_avg = values

	fig, ax = plt.subplots()
	#locator = mdates.WeekdayLocator()
	locator = mdates.MonthLocator(interval=3)
	ax.xaxis.set_major_locator(locator)
	ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
	plt.xticks(rotation=45, ha="right")
	fig.tight_layout()
	ax.plot(xval[N-1:], values_moving_avg, lw=0.5)
	fig.savefig("xd.svg")

def most_common_words(messages, N):
	words = {}
	for message in messages['messages']:
		if 'content' not in message:
			continue
		message_str = re.sub(r'[,.?!/()+"*@:]', '', message['content'])
		#message_str = message['content']
		word_list = message_str.lower().split()
		for word in word_list:
			if word in words:
				words[word] += 1
			elif len(word) >= N:
				words[word] = 1
	return words

if __name__ == "__main__":
	workdir = os.path.join(os.environ['PWD'], sys.argv[1])
	messages = load_json_files(workdir)
	pp = pprint.PrettyPrinter(sort_dicts=False)
	words = most_common_words(messages, 5)
	words_sorted = dict(sorted(words.items(), key=lambda item: item[1], reverse=True))
	for key, value in islice(words_sorted.items(), 0, 20):
		print("{0}: {1}".format(key, value))
	print(len(messages['messages']))
	plot_messages(messages, 7)
