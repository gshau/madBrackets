FROM ubuntu

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get -y upgrade
RUN apt-get -y install postgresql postgresql-contrib git
RUN apt-get -y install nginx vim less net-tools
RUN apt-get install -y python3 python3-pip

# RUN git clone https://github.com/gshau/madBrackets.git


RUN pip3 install --upgrade pip
RUN pip3 install pandas flask gunicorn numpy psycopg2 sklearn scipy sqlalchemy sqlalchemy_utils

VOLUME /data
VOLUME /app

EXPOSE 80

RUN rm -f /etc/nginx/sites-enabled/*
COPY sites_enabled_app /etc/nginx/sites-available/application
RUN ln -s /etc/nginx/sites-available/application /etc/nginx/sites-enabled/application

RUN cd /app
CMD /app/run.sh
