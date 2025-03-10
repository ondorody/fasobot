import os
import sys
import json
import predict_reply

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["EAAGCbeaSIQwBALZB3GZCo4CpTHrg6NIBkPQLZB6jZAnaHvMVeZAbx8U4uwHenMayiYHyjcpwXdxCCzY5htD6wvp96fI4jAZBpHjACDZAhoQwsz6t0xWg3Dp7DZBOtWuonkKDmgp9Dbv7Tr2oMPw0fVmy7ZCTdqZB22ZCZC5ZB0ULAYbRJN1JTGTdD2wiT"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events
  try:
    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    try: 
                        message_text = messaging_event["message"]["text"]  # the message's text
            
                        reply=predict(message_text)
                        send_message(sender_id, str(reply))
                    except:
                        send_message(sender_id,str("Sorry! I didn't get that."))    
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200
  except:
    pass  


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()

def predict(incoming_msg):
    return predict_reply.classify(incoming_msg);

if __name__ == '__main__':
    app.run(debug=True)
    #print(predict(raw_input("Enter something")))
