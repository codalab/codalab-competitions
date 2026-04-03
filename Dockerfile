FROM --platform=linux/amd64 python:3.8-bookworm


# For nodejs
#RUN curl -sL https://deb.nodesource.com/setup_4.x | bash -
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
ENV NVM_DIR="/root/.nvm"
RUN [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" \
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion" && \
    nvm install 4 && nvm use 4 && nvm alias default 4
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN apt-get update && apt-get install -y npm netcat-traditional libmemcached-dev

#RUN pip install --upgrade pip  # make things faster, hopefully
COPY codalab/requirements/requirements.txt requirements.txt
#RUN /root/.local/bin/uv venv && /root/.local/bin/uv pip install -r requirements.txt
RUN pip install -r requirements.txt
WORKDIR /app/codalab
