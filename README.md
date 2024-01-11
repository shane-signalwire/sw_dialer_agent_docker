# SignalWire AI Dailer Agent

This standalone docker container allows configuration and customization of a SignalWire AI Agent to be used with your pre-existing SignalWire Space.  The AI Agent is configured to act as a polling agent.

## Prerequisites
 - An NGROK account and auth token (ngrok.com)
 - Docker desktop (docker.com)
 - A SignalWire API Token, Project ID and at least one phone number

## RUN VIA DOCKER
```console
# Build the Docker image:
docker build -t ai_dialer_agent  --build-arg  "NGROK_AUTHTOKEN_ARG=<NGROK AUTH TOKEN>" .

# Run the container
docker run -p 8000:5000 ai_dialer_agent
```

## Configuration and Set Up

To Generate Calls:
In a web broswer:
1.  Navigate to http://localhost:8000
2.  Configure Dialer:
    Under Configure Dialer, enter the information for SignalWire Space, SignalWire Project ID, SignalWire API Token, and Caller ID Number
    Note:  The Caller ID Number **must** be a SignalWire number, and will also be the number that is dialed to reach the AI Agent
3.  Click 'Submit' to save config.  This will configure the dialer, as well as update the Phone Number to point to this application.
4.  Add Poll Partipants
5.  Add questions for the agent to ask.
6.  Start the dialer by clicking 'START POLL'
