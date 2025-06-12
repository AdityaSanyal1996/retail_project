FROM quay.io/astronomer/astro-runtime:12.5.0
# install soda into a virtual environment
USER root

RUN sudo apt-get update && sudo apt-get install -y build-essential

RUN python -m venv soda_venv && source soda_venv/bin/activate && \
    pip install setuptools &&\
    pip install --no-cache-dir soda-core-bigquery==3.4.0 &&\
    pip install --no-cache-dir soda-core-scientific==3.4.0 && deactivate

