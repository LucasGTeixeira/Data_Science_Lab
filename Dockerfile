FROM jupyter/pyspark-notebook:latest

COPY --chown=1000:100 requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt
