import discord
import random
import json
import pickle
import numpy as np
import requests
import pytz
import deepl as dp
 
import nltk
from nltk.stem import WordNetLemmatizer
 
"""from tensorflow.keras.models import load_model"""
import tensorflow as tf
 
lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())
 
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = tf.keras.models.load_model('chatbot_model.h5')

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words
 
def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)
 
def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
 
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])[0]})
    return return_list
 
def get_response(intents_list, intents_json):
    if not intents_list:
        return "Sorry, I'm not sure what you mean. Can you please try again?"
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result
 
TOKEN = "MTA0OTU3NTUwOTI2MjA5MDI3MA.GNmbmv.3FtPXFa8266TfIkrzpjLBbNIDoUR2hMMK-1-EM"
 
async def send_message(message, user_message, is_private):
    try:
        usertext = str(user_message)
        if not isinstance(usertext, str):
            raise TypeError("user_message must be a string")
        usertext = usertext.lower()
        ints = predict_class(usertext)
        res = get_response(ints, intents)
        print('result: ' + res)
        await message.author.send(res) if is_private else await message.channel.send(res)
 
    except Exception as e:
        print(e)
 
def run_discord_bot():
    TOKEN = "MTA0OTU3NTUwOTI2MjA5MDI3MA.GNmbmv.3FtPXFa8266TfIkrzpjLBbNIDoUR2hMMK-1-EM"
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
 
    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
 
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
 
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
 
        print(f'{username} said: "{user_message}" ({channel})')
 
        if user_message.startswith('*'):  # Check if the message starts with '*'
            cmdarry = user_message.lower().split()  # Remove the '*' and convert to lowercase
            if cmdarry[0] == '*time':  # Check if the command is 'special_command'
                location = cmdarry[1]
                retrieval = requests.get(f'http://worldtimeapi.org/api/timezone/{location}')
                time_data = retrieval.json()
 
                current_time = time_data['datetime']
 
                await message.channel.send(
                    f'The current time in {location} is {current_time}')  # Send the special response
            elif cmdarry[0] == '*help':
                await message.channel.send(
                    "Here is a list of available commands:\n\n*time timezonehere\ntell the time in a given timezone\n\n*ltmzn\nshows a link to a list of valid time-zones.\n\n*weather yourlocationhere\nshows the current temperature and weather conditions for the city in question\n\n*translate langcodehere translationtexthere\ntranslate text into various languages\n\n*langlist\nsends a list of all valid language codes to translate to\n\n*define wordtodefinehere\ndefines a word\n\n*summarize yourinformationhere\nsummarizes a body of text\n\n*aniquo\nsends a random anime quote\n\n*roll\nrolls a die\n\n*flip\nflips a coin\n\n*rate thingtoratehere\nrates someone or something from 1-10"
                )
            elif cmdarry[0] == '*tmznl':
                time_zones = pytz.all_timezones
 
                for tz in time_zones:
                    await message.channel.send(tz)
 
            elif cmdarry[0] == '*ltmzn':
                await message.channel.send(
                    "For a list of all valid timezones, please visit the following link: http://worldtimeapi.org/api/timezone/"
                )
            elif cmdarry[0] == '*roll':
                dice_score = str(random.randint(1,6))
                await message.channel.send(
                    f"I rolled the dice and got a {dice_score}."
                )
            elif cmdarry[0] == '*flip':
                coin_flip = random.randint(1,2)
                if coin_flip == 1:
                    coin_flip = 'heads'
                else:
                    coin_flip = 'tails'
                await message.channel.send(
                    f'I flipped the coin and it landed on {coin_flip}.'
                )
            elif cmdarry[0] == "*rate":
                rating = str(random.randint(1,10))
                rthing = cmdarry[1:]
                rthing = " ".join(rthing)
                await message.channel.send(
                    f'This time, the rating I give {rthing} is {rating}!'
                )
            elif cmdarry[0] == "*weather":
                wparams = {
                'access_key': '34b763f49249a75b53e9ebdbee745632',
                'query': " ".join(cmdarry[1:])
                }

                wapi_result = requests.get('http://api.weatherstack.com/current', wparams)

                wapi_response = wapi_result.json()
                city = wapi_response["location"]["name"]
                country = wapi_response['location']['country']
                temperature = wapi_response['current']['temperature']
                descriptions = wapi_response['current']['weather_descriptions']
                print(f'The current temperature in {city}, {country} is {temperature}℃ and the weather is {descriptions}')
                await message.channel.send(
                    f'The current temperature in {city}, {country} is {temperature}℃ and the weather is {descriptions}'
                    )
            elif cmdarry[0] == '*translate':
                tslang = cmdarry[1]
                tstext = " ".join(cmdarry[2:])
                auth_key = "bf9a64a1-bc12-84bb-61b9-4df0f3ad418f:fx"  # Replace with your key
                translator = dp.Translator(auth_key)

                result = translator.translate_text(tstext, target_lang=tslang)
                print(result.text)
                await message.channel.send(
                    result.text
                )
            elif cmdarry[0] == '*langlist':
                await message.channel.send(
                    'Here is a list of all of the language codes that may be used for translation targets:\n\nBG - Bulgarian\nCS - Czech\nDA - Danish\nDE - German\nEL - Greek\nEN-GB - English (British)\nEN-US - English (American)\nES - Spanish\nET - Estonian\nFI - Finnish\nFR - French\nHU - Hungarian\nID - Indonesian\nIT - Italian\nJA - Japanese\nKO - Korean\nLT - Lithuanian\nLV - Latvian\nNB - Norwegian (Bokmål)\nNL - Dutch\nPL - Polish\nPT-BR - Portuguese (Brazilian)\nPT-PT - Portuguese (all Portuguese varieties excluding Brazilian Portuguese)\nRO - Romanian\nRU - Russian\nSK - Slovak\nSL - Slovenian\nSV - Swedish\nTR - Turkish\nUK - Ukrainian\nZH - Chinese (simplified)'
                )
            elif cmdarry[0] == '*define':
                dword = cmdarry[1]
                drequest = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{dword}')
                definfo = drequest.json()
                theword = definfo[0]['word']
                meanings = definfo[0]['meanings']
                part_of_speech_list = []
                print(f'Word: {theword}\n\n')
                await message.channel.send(
                    f'**Word: {theword}**'
                )
                for meaning in meanings:
                    part_of_speech = meaning['partOfSpeech']
                    definitions = meaning['definitions']
                    part_of_speech_list.append(part_of_speech)
                    print(f'Part of Speech: {part_of_speech}')
                    await message.channel.send(
                        f'**Part of Speech: {part_of_speech}**'
                    )
                    for definition in definitions:
                        definition_text = definition['definition']
                        example = definition.get('example', 'No example available')
                        print(f'Definition: {definition_text}')
                        await message.channel.send(
                            f'**Definition:** {definition_text}'
                        )
                        print(f'Example: {example}')
                        await message.channel.send(
                            f'Example: {example}'
                        )
            elif cmdarry[0] == '*aniquo':
                aqresponse = requests.get('https://animechan.vercel.app/api/random')
                quote = aqresponse.json()

                anime = quote['anime']
                character = quote['character']
                quote_text = quote['quote']
                print(f'{character} from {anime} said, "{quote_text}"')
                await message.channel.send(
                    f'{character} from {anime} said, "{quote_text}"'
                )
            elif cmdarry[0] == '*anipic':
                if cmdarry[1].lower() != 'nsfw':
                    pic_category = cmdarry[1].lower()
                    picrequest = requests.get(f'https://api.waifu.pics/sfw/{pic_category}')
                    picurl = picrequest.json()
                    print(picurl['url'])
                    await message.channel.send(
                        picurl['url']
                    )
                else:
                    pic_category = cmdarry[2].lower()
                    picrequest = requests.get(f'https://api.waifu.pics/nsfw/{pic_category}')
                    picurl = picrequest.json()
                    print(picurl['url'])
                    await message.channel.send(
                        picurl['url']
                    )
            elif cmdarry[0] == '*nsfwcat':
                await message.channel.send(
                    'Here is a list of all of the NSFW categories:\nwaifu\nneko\ntrap\nblowjob'
                )
            elif cmdarry[0] == '*anicat':
                await message.channel.send(
                    'Here is a list of all of the anime picture categories:\nwaifu\nneko\nshinobu\nmegumin\nbully\ncuddle\ncry\nhug\nawoo\nkiss\nlick\npat\nsmug\nbonk\nyeet\nblush\nsmile\nwave\nhighfive\nhandhold\nnom\nbite\nglomp\nslap\nkill\nkick\nhappy\nwink\npoke\ndance\ncringe'
                )
            elif cmdarry[0] == '*summarize':
                s_text_body = " ".join(cmdarry[1:])
                
                summary_url = "https://text-analysis12.p.rapidapi.com/summarize-text/api/v1.1"

                summary_payload = {
	                "language": "english",
	                "summary_percent": 50,
	                "text": f'{s_text_body}'
                }
                summary_headers = {
	            "content-type": "application/json",
	            "X-RapidAPI-Key": "4078f0f799mshc34f7bcc9992803p1abf2bjsn769e8d338733",
	            "X-RapidAPI-Host": "text-analysis12.p.rapidapi.com"
                }

                summary_response = requests.post(summary_url, json=summary_payload, headers=summary_headers)
                summary_data = summary_response.json()

                summary = summary_data['summary']

                await message.channel.send(
                    f'{summary}'
                )
            else:
                await message.channel.send('Unknown command, try *help')  # Send an error message for an unknown command
        else:
            await send_message(message, user_message, is_private=False)
 
    client.run(TOKEN)
"""
while True:
    message = input("")
    message = message.lower()
    ints = predict_class(message)
    res = get_response(ints, intents)
    print(res)
"""
 
"""
import random
import json
import pickle
import numpy as np
 
import nltk
from nltk.stem import WordNetLemmatizer
 
from tensorflow.keras.models import load_model
 
lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())
 
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_model.model')
 
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words
 
def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)
 
def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
 
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])}[0])
    return return_list
    """
