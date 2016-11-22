import logging
import os
import time
from slackclient import SlackClient
from language_parsing import ApiAi
from language_parsing import GoogleTranslateApi
from google.cloud import translate
from oauth2client.client import GoogleCredentials

credentials = GoogleCredentials.get_application_default()


# bot ID is an environment variable
BOT_ID = os.environ.get("BOT_ID")
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
GOOGLE_TRANSLATE_TOKEN = os.environ.get("GOOGLE_TRANSLATE_TOKEN")


#Set debugging level
logging.basicConfig(level=logging.DEBUG)
logging.debug(GOOGLE_TRANSLATE_TOKEN)

# constants
AT_BOT = "<@" + BOT_ID + ">"
READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose

# instantiate Slack, google translate api & api.ai
slack_client = SlackClient(SLACK_BOT_TOKEN)
apiai = ApiAi()
translator = translate.Client(GOOGLE_TRANSLATE_TOKEN)
credentials = GoogleCredentials.get_application_default()


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Default"
    logging.debug("Processing command through API.AI: '{}'".format(command))
    lang_response, ok = apiai.process(command)
    if ok:
        response = lang_response

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":

    trans_string = translator.translate("Jeg")
    logging.debug(trans_string)
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
