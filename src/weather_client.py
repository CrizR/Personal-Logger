import requests
import json
import geocoder


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
            response = json.loads(requests.post(url + city_name + "," + country_code.upper() + "&"
                                                + "APPID=" + key).text)
        except ConnectionError or ConnectionAbortedError or ConnectionResetError or TimeoutError:
            return {}
        wtype = []
        for type in response['weather']:
            wtype.append(type['main'])
        wanted_data = {
            "weather_type": wtype,
            'temperature': round(response['main']["temp"] * 9/5 - 459.67, 2),
            'pressure': response['main']['pressure'],
            'humidity': response['main']['humidity'],
            'visibility': response['visibility'],
            'wind_speed': response['wind']['speed']
        }
        return wanted_data
