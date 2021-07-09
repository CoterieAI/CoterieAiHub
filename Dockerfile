FROM gcr.io/google_appengine/python

RUN virtualenv -p python3 /env
ENV PATH /env/bin:$PATH

COPY ./coterie-app /app

COPY ./requirements.txt /app

COPY cloud_sql_proxy /app

WORKDIR /app


RUN /env/bin/pip install --upgrade pip && /env/bin/pip install -r /app/requirements.txt
ADD . /app

ENTRYPOINT ["sh", "./run.sh"]