tmux kill-session -t codalab_workers
tmux new -d -s codalab_workers

tmux send-keys -t codalab_workers "source ~/.virtualenvs/codalab-competitions/bin/activate" ENTER
#tmux send-keys -t codalab_workers "python $PWD/codalab/worker.py" ENTER
tmux send-keys -t codalab_workers "celery -A codalab worker -l info -Q site-worker --without-gossip --without-mingle --without-heartbeat" ENTER

tmux split-window -t codalab_workers

tmux send-keys -t codalab_workers.1 "source ~/.virtualenvs/codalab-competitions/bin/activate" ENTER
#tmux send-keys -t codalab_workers.1 "python $PWD/codalabtools/compute/worker.py" ENTER

# Note we only want 1 compute worker running at once
tmux send-keys -t codalab_workers "celery -A codalab worker -l info -Q compute-worker --concurrency=1 --without-gossip --without-mingle --without-heartbeat" ENTER

tmux set-option -g set-titles on
tmux set-option -g set-titles-string 'Codalab Workers Ctrl + b then d to detach'
tmux set-window-option -g automatic-rename on

