FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    firefox-esr \
    bzip2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN GECKODRIVER_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep "tag_name" | cut -d '"' -f 4) && \
    wget -O /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz" && \
    tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin && \
    rm /tmp/geckodriver.tar.gz

RUN apt-get update && apt-get install -y \
    libx11-xcb1 \
    libdbus-glib-1-2 \
    libgtk-3-0 \
    libxt6 \
    libxrender1 \
    libx11-xcb1 \
    libxcb1 \
    libdbus-glib-1-2 \
    libasound2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Firefox
RUN install -d -m 0755 /etc/apt/keyrings
RUN wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | tee /etc/apt/keyrings/packages.mozilla.org.asc > /dev/null
RUN echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | tee -a /etc/apt/sources.list.d/mozilla.list > /dev/null
RUN echo 'Package: * Pin: origin packages.mozilla.org Pin-Priority: 1000' | tee /etc/apt/preferences.d/mozilla
RUN apt-get update && apt-get install -y firefox

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# EXPOSE 10000

CMD ["gunicorn", "main:app", "-b", "0.0.0.0:10000"]
# CMD ["flask", "--app", "main.py", "run", "--port", "10000"]