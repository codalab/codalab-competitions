# !/bin/bash

# Demonstrates Vowpal-Wabbit integration to the Codalab commandline tool

# Get program
vw=$(./codalab.py upload pliang/vw)

# Get example data sets
murl=$(./codalab.py upload pliang/maliciousurl/url_svmlight)

# Execute online training simulation
online_training_sim=$(./codalab.py run $vw $murl '$program/online_training_sim $input $output')/output
