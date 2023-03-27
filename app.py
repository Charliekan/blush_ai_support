# Import necessary modules
import requests
from bs4 import BeautifulSoup
import spacy
from flask import Flask, request, abort
import os
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

# Load Spacy language model
nlp = spacy.load('en_core_web_sm')

# Set LINE Messaging API credentials
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]


line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Define function to search web pages for given keywords
def web_search(keywords, urls):
    lines = []

    # Search each URL for keywords
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for p in soup.find_all('p'):
            if any(keyword in p.text.lower() for keyword in keywords):
                lines.append(p.text.strip())

    return lines

# Handle POST requests to callback URL
app = Flask(__name__)
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# Handle MessageEvent
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    # Analyze text to extract verbs, nouns, and adjectives
    doc = nlp(text)
    verbs = [token.lemma_ for token in doc if token.pos_ == 'VERB']
    nouns = [token.lemma_ for token in doc if token.pos_ == 'NOUN']
    adjectives = [token.lemma_ for token in doc if token.pos_ == 'ADJ']

    # Combine extracted keywords
    keywords = verbs + nouns + adjectives

    # Search web pages for keywords
    urls = ['https://blush-platform.com/terms-of-use', 'https://blush-platform.com/faq', 'https://blush-platform.com/law-on-e-commerce']
    lines = web_search(keywords, urls)

    # Generate response
    if lines:
        response = "\n".join(lines)
    else:
        response = "I'm sorry, I couldn't find any information on that."

    # Send response back to user using LINE Messaging API
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response))

if __name__ == "__main__":
    app.run()
