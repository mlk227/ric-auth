FROM python:3.8

ARG requirements=requirements/development.txt
ENV DJANGO_SETTINGS_MODULE=ric_auth.settings.development

WORKDIR /app
COPY . /app/

RUN apt-get update
RUN apt -y install netcat binutils libproj-dev gdal-bin

RUN pip install --upgrade pip
RUN pip install -r ${requirements}

EXPOSE 8001

CMD ["/app/runserver.sh"]
