
START_TIME=`date +%s`

docker-compose build alice-amd

END_TIME=`date +%s`

TOTAL_RUN_TIME="Built at "$(((END_TIME-START_TIME)/60))" minutes."
echo '--------------------------'
echo "$TOTAL_RUN_TIME"
echo '--------------------------'
