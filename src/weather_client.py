import requests
import json
import geocoder
import logging
from logging import config

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})


class Weather(object):

    @staticmethod
    def get_weather(city_name=None, country_code=None):
        """
        Return the weather of the given city
        :param city_name: The name of the city whose weather we want
        :param country_code: The country code associated with that city
        :return: The dictionary of weather data
        """
        if city_name is None and country_code is None:
            g = geocoder.ip('me')
            city_name = g.city
            country_code = g.country
        url = "http://api.openweathermap.org/data/2.5/weather?q="
        key = "a5e0c2f9d95a59f6cebcc153be85af60"
        try:
            response = requests.post(url + city_name + "," + country_code.upper() + "&"
                                                + "APPID=" + key)
            if response.status_code == 200:
                data = json.loads(response.text)
                wtype = []
                for type in data['weather']:
                    wtype.append(type['main'])
                wanted_data = {
                    "weather_type": wtype,
                    'temperature': round(data['main']["temp"] * 9 / 5 - 459.67, 2),
                    'pressure': data['main']['pressure'],
                    'humidity': data['main']['humidity'],
                    'visibility': data['visibility'],
                    'wind_speed': data['wind']['speed']
                }
                return wanted_data
            else:
                logging.error("Could not retrieve weather")
                return {}
        except ConnectionError or ConnectionAbortedError or ConnectionResetError or TimeoutError:
            logging.error("Could not retrieve weather")
            return {}
