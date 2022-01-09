FROM python:3.7.11-buster as base

# build and load all requirements
FROM base as builder
WORKDIR /airbyte/integration_code

# upgrade pip to the latest version
RUN apt upgrade \
    && pip install --upgrade pip \
    && apt install tzdata

RUN pip install --upgrade setuptools


COPY setup.py ./
# install necessary packages to a temporary folder
RUN pip install --no-cache-dir  --force-reinstall -Iv --prefix=/install .

# build a clean environment
FROM python:3.7.11-slim-buster
WORKDIR /airbyte/integration_code

# copy all loaded and built libraries to a pure basic image
COPY --from=builder /install /usr/local
# add default timezone settings
COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN echo "Etc/UTC" > /etc/timezone

# bash is installed for more convenient debugging.
RUN apt install bash

# copy payload code only
COPY main.py ./
COPY source_google_analytics_data_api ./source_google_analytics_data_api

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.1
LABEL io.airbyte.name=airbyte/source-google-analytics-data-api
