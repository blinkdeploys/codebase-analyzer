FROM python:3.11-slim

WORKDIR /app

# install git and system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# configure git globally
RUN git config --global user.name "Blink Deploys" && \
    git config --global user.email "blinkdeploys@gmail.com"

# copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy CLI code and worker module
COPY cli.py .
COPY ../worker/worker.py /app/worker/

# create directories
RUN mkdir -p /app/workdir /app/output

# make CLI executable
RUN chmod +x cli.py

ENTRYPOINT ["python", "cli.py"]

