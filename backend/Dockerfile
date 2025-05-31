FROM python:3.9-slim-bullseye

RUN apt-get update
RUN apt-get install sqlite3
RUN pip install --upgrade pip
COPY requirements.txt /tmp
RUN pip install --requirement /tmp/requirements.txt
# Weird interaction in deps
RUN pip install -U scikit-learn
RUN pip install	pandas

COPY . .

# Run the schema and insert script
RUN sqlite3 database.sqlite3 < projectSchema.sql
# RUN python3 insertScript.py
EXPOSE 5000
# CMD ["python3", "databaseManipulator.py"]
CMD python3 insertScript.py && python3 databaseManipulator.py
