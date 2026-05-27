FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install uv && make install && pip install psycopg[binary]

CMD ["make", "test-coverage"]