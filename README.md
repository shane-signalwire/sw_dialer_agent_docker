# SignalWire AI Dailer Agent

This standalone docker container allows configuration and customization of a SignalWire AI Agent to be used with your pre-existing SignalWire Space.  The AI Agent is configured to act as a polling agent.

## Prerequisites
 - An NGROK account and auth token (ngrok.com)
 - Docker desktop (docker.com)
 - A SignalWire API Token, Project ID and at least one phone number

## RUN VIA DOCKER
```console
# Build the Docker image:
docker build -t ai_dialer_agent  --build-arg "NGROK_AUTHTOKEN_ARG=<NGROK AUTH TOKEN>" --build-arg "TOKEN_ARG=<API TOKEN>" --build-arg "PROJECT_ARG=<SIGNALWIRE PROJECT ID>" --build-arg "AGENT_DEST_ARG=<AI AGENT DESTINATION NUMBER>" .

# Run the container
docker run -p 8000:5000 ai_dialer_agent
```

## Configuration and Set Up
To Set up a SWML webhook to your new docker instance:
1.  Copy the NGROK tunnel address from the command line output
2.  In a web browser, navigate to <your-signalwire-space>.signalwire.com
4.  Navigate to the desired 'Phone Number' and edit
5.  Set the number to:
    - Handle Calls Using:  A SWML Script
    - When A Call Comes In:  https://<ngrok_tunnel_address>/ai

To Generate Calls:
1.  Naviate to http://127.0.0.1:8000 in a browser window.
2.  In the 'Caller ID' field, enter the desired Caller ID Number (In E164 format) in the text box.  This MUST be a number associated with your SignalWire Account.
3.  In the 'Lust of Number to Dial' field, Enter one number per line to have them dialed sequentially by the dialer application.  Each call will separately connect to the AI Agent for the poll.
4.  Click 'Dial' to begin calling.

