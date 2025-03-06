FROM python:3.8
LABEL maintainer="Klaus"

COPY ./techtrends /app
WORKDIR /app
RUN pip install -r requirements.txt

# Expose port 3111
EXPOSE 3111

# command to run on container start
CMD [ "python", "app.py" ]
