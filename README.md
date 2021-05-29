# strava
fun tool to get strava activities
Step to run

`cd to the root`

`pipenv install`

`cp _config.py config.py`

Fill missing configs then run the web server

`flask run`

Enter the host to get strava authentication
http:\\localhost:5000\

Login to Strava and accept to generate the token. It will redirect to http:\\localhost\authorization

Final step set up the cron to run the pull command

`* * * * * cd root && flask pull`

Thanks for Huan and Vu for supporting this project



