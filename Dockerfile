FROM eagledaddy/evennia-debian:latest
USER root 
RUN pip install -r requirements.txt --no-cache-dir
ENTRYPOINT evennia makemigrations && evennia migrate && evennia start --log