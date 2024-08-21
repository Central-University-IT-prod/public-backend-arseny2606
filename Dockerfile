FROM python:3.12.1

WORKDIR /app

RUN apt update && apt install wait-for-it
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["sh", "entrypoint.sh"]