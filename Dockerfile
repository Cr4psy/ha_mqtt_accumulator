ARG BUILD_FROM
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Copy Python requirements file
COPY requirements.txt /tmp/

# Install requirements for add-on
RUN \
    apk add --no-cache \
        py3-pip \
        python3

RUN pip install -r /tmp/requirements.txt

COPY main.py /tmp/

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]