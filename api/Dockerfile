FROM python:3.11-slim

WORKDIR /app

# install git and system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY main.py .

# create directories
RUN mkdir -p /app/workdir /app/output

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]