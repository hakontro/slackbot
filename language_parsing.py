import json
import uuid
import os
import requests
import logging

VERSION = 20161120


class ApiAi:
    URL = "https://api.api.ai/v1/query?v={}&lang=en&sessionId=123".format(VERSION)
    HEADER = {'Authorization': 'Bearer {}'}

    def __init__(self):
        self.URL += "&sessionId={}".format(uuid.uuid1())
        self.HEADER['Authorization'] = self.HEADER['Authorization'].format(os.environ.get("API_AI_TOKEN"))
        pass

    def process(self, command):
        get_url = self.URL + "&query={}".format(command)
        response = self.fetch(get_url)

        success = response['status']['errorType'] == 'success'

        if success:
            return self.build_string(response), success
        return "", False

    def fetch(self, url):
        response = requests.get(url, headers=self.HEADER)
        return json.loads(response.text)

    def build_string(self, response):
        logging.debug(response)
        return response["result"]["fulfillment"]["speech"]

class GoogleTranslateApi:
    URL = "https://translation.googleapis.com/language/translate/v2?"

    def __init__(self):
        self.URL += "key={}".format(os.environ.get("GOOGLE_TRANSLATE_TOKEN"))
        self.URL += "&target=en"

    def translate(self,input_string):
        get_url = self.URL + "&q={}".format(input_string)
        response = requests.get(get_url)
        return response
