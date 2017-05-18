import datetime
import csv
import operator
import collections

## Same as csv_parse except takes a list of strings and iterates through each as a .csv file.

def csv_parse_list(context, list_of_strings):
	return_dict = {}

	for csv_file in list_of_strings:


		with open(str(csv_file), 'rb') as f_csv_file:
			reader = csv.DictReader(f_csv_file)
		
			for row in reader:
				date = row['Date'].split()[0]
				if date not in return_dict.keys():
					return_dict[date] = {
						'count': int(0),
						'high_score': None
					}

				return_dict[date]['count'] += 1

				if not return_dict[date]['high_score'] or row['<Rank>'].split()[0] > return_dict[date]['high_score']:

					return_dict[date]['high_score'] = float(row['<Rank>'].split()[0])

		##Sort CSV

		sorted_return = collections.OrderedDict(sorted(return_dict.items(), reverse=False))

		##High score

		best_score = None
		previous_best_score = None

		for date, data in sorted_return.items():
			if not best_score or data['high_score'] > best_score:
				best_score = data['high_score']
			else:
				data['high_score'] = best_score

		print(sorted_return)

		context['csv_data'] = sorted_return




def csv_parse(context, csv_file):
	
	return_dict = {}

	## Read from CSV 

	## CSV's had some difference in formatting, so I formatted
	## them all the same as 9, since thats what I was first working with.

	with open(str(csv_file), 'rb') as f_csv_file:
		reader = csv.DictReader(f_csv_file)
		
		for row in reader:
			date = row['Date'].split()[0]
			if date not in return_dict.keys():
				return_dict[date] = {
					'count': int(0),
					'high_score': None
				}

			return_dict[date]['count'] += 1

			if not return_dict[date]['high_score'] or row['<Rank>'].split()[0] > return_dict[date]['high_score']:

				return_dict[date]['high_score'] = float(row['<Rank>'].split()[0])

	##Sort CSV

	sorted_return = collections.OrderedDict(sorted(return_dict.items(), reverse=False))

	##High score

	best_score = None
	previous_best_score = None

	for date, data in sorted_return.items():
		if not best_score or data['high_score'] > best_score:
			best_score = data['high_score']
		else:
			data['high_score'] = best_score

	print(sorted_return)

	context['csv_data'] = sorted_return




