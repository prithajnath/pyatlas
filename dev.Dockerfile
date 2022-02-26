FROM python:3.9-slim-buster

RUN apt update

# GCC and other essentials
RUN apt install -y libpq-dev \
	build-essential \
	gnupg2 \
	procps \
	poppler-utils

# Networking tools
RUN apt install -y \
	lsb-release \
	traceroute \
	wget \
	curl \
	iputils-ping \
	bridge-utils \
	dnsutils \
	netcat-openbsd \
	jq \
	nmap \
	net-tools \
	&& rm -rf /var/lib/apt/lists/*

# PSQL
RUN echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list | sh
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt update && apt install -y postgresql-client

WORKDIR /usr/bin/pyatlas

COPY . .

RUN pip install -r requirements.txt


STOPSIGNAL SIGINT
ENTRYPOINT ["python", "app.py"]