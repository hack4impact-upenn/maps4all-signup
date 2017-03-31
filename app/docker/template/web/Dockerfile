FROM ubuntu:latest
RUN apt-get update -y && apt-get install -y \
  build-essential \
  git \
  postgresql \
  python3-dev \
  python3-pip \
  rubygems
RUN gem install sass

VOLUME /persists

RUN git clone https://github.com/hack4impact/flask-base.git /app
COPY Proc /app/
WORKDIR /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY run.sh /tmp/
COPY wait-for-postgres.sh /tmp/
WORKDIR /tmp

CMD ["sh", "wait-for-postgres.sh"]

