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
#!/usr/bin/env python
import sys
import os
import json
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
matplotlib.use('SVG')
import numpy as np


def convert(obj, enc):
	if isinstance(obj, str):
		return obj.encode('latin1').decode(enc)
	if isinstance(obj, (list, tuple)):
		return [convert(item, enc) for item in obj]
	if isinstance(obj, dict):
		return {convert(key, enc) : convert(val, enc)
			for key, val in obj.items()}
	else: return obj
"""
def moving_avg(arr, N):
	N = N // 2
	out = [0]*len(arr)
	for i, x in enumerate(arr):
		j = i
		while j >= 0 and abs(arr[j] - arr[i]) < N:
			out[i] += 1
			j -= 1
		j = i + 1
		while j < len(arr) and abs(arr[j] - arr[i]) < N:
			out[i] += 1
			j += 1
	return out
"""
workdir = os.path.join(os.environ['PWD'], sys.argv[1])

json_files = [ file for file in os.listdir(workdir) if file.endswith(".json") ]

json_list = []
for file in json_files:
	with open(os.path.join(workdir,file), "r") as f:
		json_list.append(json.loads(f.read()))

if len(json_list) > 1:
	for i in range(0, len(json_list)):
		json_list[0]['messages'] += json_list[i]['messages']


messages = convert(json_list[0], 'utf-8')
print(len(messages['messages']))
del json_list

timestamps = [ x['timestamp_ms'] for x in messages['messages'] ]
timestamps.sort()
day_timestamps = [ math.floor(mdates.epoch2num(t/1000)) for t in timestamps ]
#print(day_timestamps)
#values = moving_avg(timestamps, 86400000)
#xval = [mdates.num2date(mdates.epoch2num(t/1000)) for t in timestamps]
xval = [ x for x in range(day_timestamps[0], day_timestamps[-1] + 1) ]
values = [0]*len(xval)

for t in day_timestamps:
	values[t - day_timestamps[0]] += 1

fig, ax = plt.subplots()
#locator = mdates.WeekdayLocator()
locator = mdates.MonthLocator(interval=3)
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
plt.xticks(rotation=45, ha="right")
fig.tight_layout()
ax.plot(xval, values)
fig.savefig("xd.svg")
