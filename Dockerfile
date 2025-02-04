FROM python:3.12.3
LABEL authors="nkozhamuratov"

WORKDIR /opt/app

RUN pip3 install --no-cache-dir discord pymongo pytz

COPY src/ .

CMD ["python3", "main.py"]