import os, json, numpy as np

# os relative path to test.json
json_path = os.path.join(os.path.dirname(__file__), '..', 'timelines', 'sort.json')

# load test json
json = json.load(open(json_path))

# Initialize the indexed list of events
ref = {};idx = -1
for event in json['events']:
    idx += 1
    ref[idx] = event

# Sort the list of events based on the date
# *Tau's Event Sort
for _i in range(len(ref)):
    for i in range(len(ref)-1):
        if (ref[i]['date'][2] > ref[i+1]['date'][2]):
            _temp = ref[i]
            ref[i] = ref[i+1];ref[i+1] = _temp

years = {};idx = -1
for event in ref:
    idx += 1
    if event['date'][2] in years:
        years[event['date'][2]].append(event['date'][2])
    else:
        years[event['date'][2]] = []

#print(lowest_year,latest_year)