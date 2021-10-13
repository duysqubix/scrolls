FROM  python:3.7


RUN apt-get update && apt-get upgrade -y
RUN apt-get install git -y
RUN mkdir /evennia
RUN mkdir /usr/src/evennia 
RUN git clone --depth=1 https://github.com/evennia/evennia.git /usr/src/evennia


# install evennia dependencies
RUN pip install --upgrade pip && pip install -e /usr/src/evennia --trusted-host pypi.python.org
RUN pip install cryptography pyasn1 service_identity

# add the game source when rebuilding a new docker image from inside
# a game dir
ONBUILD COPY . /usr/src/game

# make the game source hierarchy persistent with a named volume.
# mount on-disk game location here when using the container
# to just get an evennia environment.
VOLUME /usr/src/game

WORKDIR /usr/src/game

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 4040
ENTRYPOINT [ "./entrypoint.sh" ]