FROM python:3.7

COPY ./src /usr/src/app

WORKDIR /usr/src/app
RUN pip install -r requirements.txt

ENV FLASK_APP=alma.py
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0"]
