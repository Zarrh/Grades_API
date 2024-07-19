FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    firefox-esr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN GECKODRIVER_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep "tag_name" | cut -d '"' -f 4) && \
    wget -O /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz" && \
    tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin && \
    rm /tmp/geckodriver.tar.gz

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["gunicorn", "main:app"]