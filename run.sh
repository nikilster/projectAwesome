#!/bin/bash
###################
#Run.sh - Sets up the web app!
####################

#Regenerate the data?
WIPE_AND_GENERATE_DATA=true
echo "WIPE_AND_GENERATE_DATA = True"
echo "Press control+c NOW if don't want to wipe data!"

#Activate the virutal envronment
. venv/bin/activate



#If redis is not running, start redis
#http://www.anyexample.com/linux_bsd/bash/check_if_program_is_running_with_bash_shell_script.xml
SERVICE='redis'

if ps ax | grep -v grep | grep $SERVICE 
then
    echo "$SERVICE service is already running, so skipping"
else
    echo "$SERVICE is not running"
    echo "Starting $SERVICE"
	
	#Start Redis
	awesome/redis-2.6.4/src/redis-server &

	echo "Started Redis!"
fi


#Wipe & Generate Data
if $WIPE_AND_GENERATE_DATA
then
	echo "------Wiping Data and Generating Test Data------"
	python awesome/api/data/testData/generateTestData.py 
	echo "------Done Generating Test Data------"
else
	echo "------As set by the script variable, NOT Wiping and Generating test Data------"
fi


#Run the server in the background
python runserver.py

