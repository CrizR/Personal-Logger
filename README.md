# PersonalLogger

For fun, I created a personal command line tool that allows me to log data to a local mongodb database about how I'm currently feeling cognitively, emotional, and physically (in addition to a regular message). In addition to this information, I get the current weather data at the time that the log took place (using my comp's IP to determine what city i'm in). I also use a basic sentiment analysis plugin to log whether or not the messages I input are positive. Using all of this data, I can tell what specific indicators impact my health and make adjustments accordingly.

## How I use it


To post information relevant to my current state I can do the following:

    python3 main.py -c 10 -cd "I feel smart" -p 5 -pd "I'm tired" -e 7 -ed "I'm happy"

    Input: {'2018-02-25 09': '{"data": {"cognitive": {"rating": "10", "description": "I feel smart", "sentiment": "positive"}, "emotional": {"rating": "7", "description": "I\'m happy", "sentiment": "positive"}, "physical": {"rating": "5", "description": "I\'m tired", "sentiment": "negative"}}, "weather": {"weather_type": ["Rain", "Mist"], "temperature": 276.33, "pressure": 1023, "humidity": 93, "visibility": 9656, "wind_speed": 5.7}}'}

To then graph this information:

    python3 main.py -graph all

To log a basic message:

    python3 main.py -log "weather test"
    
    Input: {'2018-02-25 09': '{"log": "weather test", "sentiment": "neutral", "weather": {"weather_type": ["Rain", "Mist"], "temperature": 276.07, "pressure": 1025, "humidity": 80, "visibility": 14484, "wind_speed": 7.61}}'}

To print both the logs and the personal data:

    python3 main.py -lprint console # For Logs
    
    python3 main.py -dprint console # For Data
    
Optionally this can be dumped to a file as well:

    python3 main.py -lprint file # For Logs
    
    python3 main.py -dprint file # For Data
    
    
To reset all data (Will also dump to file):

    python3 main.py -reset logs # For Logs
    
    python3 main.py -reset data  # For Data

To just delete everything:

     python3 main.py -fdel


On my computer I've created an alias that simplifies many of these commands, you can too by altering your ~/.bash_profile
