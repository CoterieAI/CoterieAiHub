FROM python:3.9

ENV pythonunbufferd 1

RUN mkdir /app

COPY ./coterie-app /app

COPY ./requirements.txt /app

COPY cloud_sql_proxy.exe ./app

WORKDIR /app

RUN pip install -r requirements.txt

#CMD python manage.py runserver 0.0.0.0:8000

ENTRYPOINT ["sh", "./run.sh"]