FROM python:3.8-slim-buster
FROM joyzoursky/python-chromedriver:3.8

WORKDIR /app

RUN pip3 install flask
RUN pip3 install pymysql
RUN pip3 install cryptography
RUN pip3 install selenium

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=127.0.0.1"]
CMD ["python", "test/auth_test.py"]
