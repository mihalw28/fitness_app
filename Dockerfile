FROM python:3.7

RUN adduser --disabled-login fitness_app


#USER fitness_app
WORKDIR /home/fitness_app

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn psycopg2-binary

COPY app app
COPY migrations migrations
COPY bin bin

COPY fit_app.py config.py boot.sh ./
RUN chmod +x boot.sh
RUN chmod +x /home/fitness_app/bin
RUN chmod +x -R /bin

ENV FLASK_APP fit_app.py
ENV PATH=$PATH:/fitness_app/bin/

RUN chown -R fitness_app:fitness_app ./
USER fitness_app

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
