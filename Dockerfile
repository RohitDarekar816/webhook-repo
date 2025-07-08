FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN pip install gunicorn

COPY . .

EXPOSE 5004

CMD [ "gunicorn", "-w", "4", "-b", "0.0.0.0:5004", "app:app" ]