#!/bin/bash
###################
#Run.sh - Sets up the web app!
####################

# Read command line parameters

WIPE_AND_GENERATE_DATA=false

while getopts "wh" opt; do
    case $opt in
        w)
            WIPE_AND_GENERATE_DATA=true
            echo "WIPE"
            ;;
        h)  echo ""
            echo "Usage: run.sh [-w to wipe local MySQL DB]"
            echo ""
            exit 1
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
    esac
done
shift $((OPTIND - 1))

echo "WIPE_AND_GENERATE_DATA = $WIPE_AND_GENERATE_DATA"

#Activate the virutal envronment
echo "Activating virtual environment"
. venv/bin/activate

#If redis is not running, start redis
#http://www.anyexample.com/linux_bsd/bash/check_if_program_is_running_with_bash_shell_script.xml
SERVICE='redis'

#if ps ax | grep -v grep | grep $SERVICE 
#then
#    echo "$SERVICE service is already running, so skipping"
#else
#    echo "$SERVICE is not running"
#    echo "Starting $SERVICE"
#	
#	#Start Redis
#	awesome/redis-2.6.4/src/redis-server &
#
#	echo "Started Redis!"
#fi


#Wipe & Generate Data
if $WIPE_AND_GENERATE_DATA
then
	echo "------Wiping Data and Generating Test Data------"
	#python awesome/api/data/testData/generateTestData.py 
    python wipeLocalDB.py
    python generateTestData.py
	echo "------Done Generating Test Data------"
else
	echo "------As set by the script variable, NOT Wiping and Generating test Data------"
fi


#Run the server in the background
python runserver.py

