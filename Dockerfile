FROM alpine

ARG NGROK_AUTHTOKEN_ARG
ENV NGROK_AUTHTOKEN=$NGROK_AUTHTOKEN_ARG

ARG TOKEN_ARG
ENV TOKEN=$TOKEN_ARG

ARG PROJECT_ARG
ENV PROJECT=$PROJECT_ARG

ARG AGENT_DEST_ARG
ENV AGENT_DEST=$AGENT_DEST_ARG

RUN apk add --update --no-cache python3
RUN apk add --update --no-cache py3-pip
RUN apk add --update --no-cache sqlite-dev

# Install the python scripts
RUN mkdir -p /root/templates

# Copy Application files
COPY app.py /root/app.py
COPY amd.py /root/amd.py
COPY requirements.txt /root/requirements.txt
COPY templates /root/templates
COPY start_services.sh /root/start_services.sh

# Make application Executable
RUN chmod +x /root/app.py
RUN chmod +x /root/amd.py
RUN chmod +x /root/start_services.sh


# pip3 install requirements
# breaking system packages shouldn't matter, we're running on a single use container.
RUN pip3 install --break-system-packages -r /root/requirements.txt

ENTRYPOINT /root/start_services.sh
