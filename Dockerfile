FROM python:3.8

LABEL maintainer="techtrends"

WORKDIR /techtrends

COPY ./requirements.txt .

#RUN pip freeze > requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /techtrends
EXPOSE 3111

RUN python init_db.py

CMD [ "python", "app.py" ]