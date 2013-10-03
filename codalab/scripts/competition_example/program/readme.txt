Building an evaluation program that works with CodaLab

This example uses python.

evaluate.py - is an example that loads a single value from each of the gold files, looks for a corresponding submission, and finds the difference.
setup.py - this is a file that enables py2exe to build a windows executable of the evaluate.py script.
metadata - this is a file that lists the contents of the program.zip bundle for the CodaLab system.

Once these pieces are assembled they are packages as program.zip which CodaLab can then use to evaluate the submissions for a competition.