FROM python:3.11

ADD ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY . /app/

WORKDIR /app

CMD ["uvicorn", "routes:app", "--host", "0.0.0.0"]
