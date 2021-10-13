FROM  python:3.8

WORKDIR /scrolls


RUN apt-get update && apt-get upgrade -y
RUN apt-get install git -y
RUN mkdir /evennia && git clone --depth=1 https://github.com/evennia/evennia.git ../evennia
RUN pip install -e /evennia 

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN evennia makemigrations && evennia migrate
CMD ["evennia", "test", "--settings", "settings.py", "."]