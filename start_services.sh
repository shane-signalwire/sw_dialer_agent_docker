#!/bin/sh

# Start the Py scripts in the background
# TODO:  This is sketchy... Daemonize?

python3 /root/app.py &
sleep 5

#######################
## THIS IS TEMPORARY ##
#######################
# Add questions to the database
# This will go away when frontend exists to add your own questions to the db
#sqlite3 /root/database.db "INSERT into survey_questions (question) VALUES ('How would you rank Candidate A on a scale of 1 to 10?');"
#sqlite3 /root/database.db "INSERT into survey_questions (question) VALUES ('How would you rank Candidate B on a scale of 1 to 10?');"
#sqlite3 /root/database.db "INSERT into survey_questions (question) VALUES ('How would you rank Candidate C on a scale of 1 to 10?');"
#######################


python3 /root/amd.py 