tmux new -d -s codalab_workers

tmux send-keys -t codalab_workers "source ~/.virtualenvs/codalab/bin/activate" ENTER
tmux send-keys -t codalab_workers "python $PWD/codalab/worker.py" ENTER

tmux split-window -t codalab_workers

tmux send-keys -t codalab_workers.1 "source ~/.virtualenvs/codalab/bin/activate" ENTER
tmux send-keys -t codalab_workers.1 "python $PWD/codalabtools/compute/worker.py" ENTER
