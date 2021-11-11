FROM python:3.8.5-slim-buster
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/"
WORKDIR /code


COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .

CMD ["gunicorn", "--workers=3", "-b 0.0.0.0:8000", "-k uvicorn.workers.UvicornWorker", "main:app"]
