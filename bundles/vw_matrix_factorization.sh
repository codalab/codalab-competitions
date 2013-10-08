# !/bin/bash

# Demonstrates Vowpal-Wabbit integration to the Codalab commandline tool

# Get program
vw=$(./codalab.py upload pliang/vw)

# Get example data sets
ml100k=$(./codalab.py upload pliang/ml-100k/ml-100k)

# Run matrix factorization example
matrix_factorization=$(./codalab.py run $vw $ml100k '$program/matrix_factorization $input $output')/output
