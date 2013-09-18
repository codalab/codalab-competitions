#!/usr/bin/env python
import sys, os, os.path

input_dir = sys.argv[1]
output_dir = sys.argv[2]

submit_dir = os.path.join(input_dir, 'res') 
truth_dir = os.path.join(input_dir, 'ref')

if not os.path.isdir(submit_dir):
	print "%s doesn't exist" % submit_dir

if os.path.isdir(submit_dir) and os.path.isdir(truth_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = os.path.join(output_dir, 'scores.txt')              
    output_file = open(output_filename, 'wb')

    gold_list = os.listdir(truth_dir)
    for gold in gold_list:
    	gold_file = os.path.join(truth_dir, gold)
    	corresponding_submission_file = os.path.join(submit_dir, gold)
    	if os.path.exists(corresponding_submission_file):
    		pi = float(open(gold_file, 'rb').read())
    		guess = float(open(corresponding_submission_file, 'rb').read())
    		diff = abs(pi - guess)
    		output_file.write("%f" % diff)
    output_file.close()