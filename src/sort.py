import json, numpy as np # Imports json, and numpy modules.

# os relative path to test.json
#json_path = os.path.join(os.path.dirname(__file__), 'timelines', 'sort.json') # Constructs the file path to the 'sort.json' file.

# load test json
def sort_json(json_path):
    with open(json_path) as json_file: # Opens the 'sort.json' file.
        json_data = json.load(json_file) # Loads the JSON data from the file into a dictionary.
    # Initialize the indexed list of events
    ref = {}; idx = -1 # Initializes an empty dictionary 'ref' and an index variable 'idx'.
    for event in json_data['events']: # Iterates over the 'events' list in the loaded JSON data.
        idx += 1
        ref[idx] = event # Stores each event in the 'ref' dictionary with its index as the key.
    # Sort the list of events based on the year
    for _i in range(len(ref)): # Iterates over the length of the 'ref' dictionary.
        for i in range(len(ref)-1): # Iterates over the length of the 'ref' dictionary minus one.
            if (ref[i]['date'][2] > ref[i+1]['date'][2]) | (ref[i]['date'][2] == ref[i+1]['date'][2] & ref[i]['date'][0] > ref[i+1]['date'][0]): # Checks if the current event's year is greater than the next event's year, or if the years are equal and the current event's month is greater than the next event's month.
                _temp = ref[i] # Stores the current event in a temporary variable.
                ref[i] = ref[i+1]; ref[i+1] = _temp # Swaps the current event with the next event in the 'ref' dictionary.
    # Break it up into {yy:{mm:{dd:[]}}}
    years = {} # Initializes an empty dictionary 'years'.
    for idx in range(len(ref)): # Iterates over the length of the 'ref' dictionary.
        year = ref[idx]['date'][2] # Extracts the year from the current event's date.
        month = ref[idx]['date'][0] # Extracts the month from the current event's date.
        day = ref[idx]['date'][1] # Extracts the day from the current event's date.
        if year in years: # Checks if the year is already a key in the 'years' dictionary.
            if month in years[year]: # Checks if the month is already a key in the year's dictionary.
                if day in years[year][month]: # Checks if the day is already a key in the month's dictionary.
                    years[year][month][day].append(ref[idx]) # Appends the current event to the list of events for that day.
                else:
                    years[year][month][day] = [ref[idx]] # Creates a new list with the current event for that day.
            else:
                years[year][month] = {day: [ref[idx]]} # Creates a new dictionary for the month with a list for the day containing the current event.
        else:
            years[year] = {month: {day: [ref[idx]]}} # Creates a new nested dictionary for the year, month, and day with a list containing the current event.
    # Sort based on month
    for year in years: # Iterates over the years in the 'years' dictionary.
        keys = list(years[year].keys()) # Gets a list of the month keys for the current year.
        keys.sort() # Sorts the list of month keys.
        sorted = {i: years[year][i] for i in keys} # Creates a new dictionary with the sorted month keys and their corresponding values.
        years[year] = sorted # Updates the year's dictionary with the sorted month dictionary.
    # Sort based on day
    for year in years: # Iterates over the years in the 'years' dictionary.
        for month in years[year]: # Iterates over the months in the current year's dictionary.
            keys = list(years[year][month].keys()) # Gets a list of the day keys for the current month.
            keys.sort() # Sorts the list of day keys.
            sorted = {i: years[year][month][i] for i in keys} # Creates a new dictionary with the sorted day keys and their corresponding values.
            years[year][month] = sorted # Updates the month's dictionary with the sorted day dictionary.
    sorted_events = [] # Initializes an empty list 'sorted_events'.
    for year in years: # Iterates over the years in the 'years' dictionary.
        for month in years[year]: # Iterates over the months in the current year's dictionary.
            for day in years[year][month]: # Iterates over the days in the current month's dictionary.
                for event in years[year][month][day]: # Iterates over the events in the current day's list.
                    sorted_events.append(event) # Appends the current event to the 'sorted_events' list.
    json_data['events'] = sorted_events # Updates the original 'events' list in the loaded JSON data with the sorted events.

    with open(json_path, 'w') as json_file: # Opens the 'sort.json' file for writing.
        json.dump(json_data, json_file, indent=4) # Dumps the updated JSON data to the file with indentation.

    json_file.close() # Closes the JSON file.