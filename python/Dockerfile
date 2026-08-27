FROM python:3.11-slim

# Install system dependencies + Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    && mkdir -p /etc/apt/keyrings \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY python/ .

CMD ["python", "network_server.py"]