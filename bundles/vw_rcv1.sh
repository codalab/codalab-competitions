# !/bin/bash

# Demonstrates Vowpal-Wabbit integration to the Codalab commandline tool

# Get program
vw=$(./codalab.py upload pliang/vw)
rcv1=$(./codalab.py upload pliang/rcv1/rcv1)

# Train and test set
rcv1_train=$(./codalab.py run $vw $rcv1 '$program/rcv1_train $input $output')/output
