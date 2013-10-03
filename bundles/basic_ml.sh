#!/bin/bash

# Demonstrates using command-line tools to run a basic ML pipeline.

# Get program and data.
weka=$(./codalab.py upload pliang/weka)
vote=$(./codalab.py upload pliang/uci_arff/vote)

# Split data
split=$(./codalab.py run $weka $vote '$program/split $input $output 4')/output
strippedTest=$(./codalab.py run $weka $split '$program/stripLabels $input/test $output')/output

# Learn
model=$(./codalab.py run $weka $split/train '$program/learn $input $output weka.classifiers.trees.J48')/output

# Predict
modelAndData=$(./codalab.py make model:$model data:$strippedTest)
predictions=$(./codalab.py run $weka $modelAndData '$program/predict $input $output')/output

# Evaluate
predictionsAndData=$(./codalab.py make predictions:$predictions data:$split/test)
evaluation=$(./codalab.py run $weka $predictionsAndData '$program/evaluate $input $output')

./codalab.py wait $evaluation
./codalab.py info $evaluation
