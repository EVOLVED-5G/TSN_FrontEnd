# syntax=docker/dockerfile:1

FROM python:3.10-slim
EXPOSE 5000

RUN mkdir -p /srv/tsn_af
WORKDIR /srv/tsn_af

COPY . .

RUN apt-get update && apt-get install -y gcc
RUN pip install --no-cache-dir -r requirements.txt waitress

ENTRYPOINT ["waitress-serve"]
CMD [ "--listen=*:5000", "app:app" ]

