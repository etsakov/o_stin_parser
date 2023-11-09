import re
import time
import sqlite3 as SQL
import numpy as np
from transformers import pipeline
from googletrans import Translator
import emoji
from emosent import get_emoji_sentiment_rank_multiple



def translate_ru_en(text):
	# This function translates given text from Russian to English for future sentiment analysis
	# pip3 install googletrans==4.0.0-rc1

	translator = Translator(service_urls=['translate.google.com'])
	try:
		translation = translator.translate(text, src='ru', dest='en')
		return translation.text
	except TypeError:
		return text
	


def analyse_sentiments(text):
	# Conducts sentiment analysis for the given text
	'''
	pip3 install -q transformers
	https://huggingface.co/blog/sentiment-analysis-python
	https://huggingface.co/bhadresh-savani/distilbert-base-uncased-emotion
	https://github.com/pysentimiento/pysentimiento
	https://www.digitalocean.com/community/tutorials/how-to-perform-sentiment-analysis-in-python-3-using-the-natural-language-toolkit-nltk
	https://realpython.com/python-nltk-sentiment-analysis/
	'''

	text = translate_ru_en(text)
	# Tensorflow token doesn't take texts longer then 128 characters... So we need to shorten this
	if len(text) > 128:
		text = text[:128]

	# THIS AI MODEL HAS BEEN TRAINED ON TWEETS FROM TWITTER
	sentiment_pipeline = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")
	model_result = sentiment_pipeline(text)
	time.sleep(0.5)
	result_label = model_result[0]['label']
	result_score = round(model_result[0]['score'], 2)

	return(result_label, result_score)


def text_has_emoji(text):
	# Removes all letters and other characters from text and gets emojies only
	pattern = r'[a-zA-Zа-яА-Я0-9-₽"&ё()., :/-?!\n\t]'
	result = re.sub(pattern, '', text)

	emo_detector = False
	for character in result:
		if character in emoji.EMOJI_DATA:
			emo_detector = True

	return result, emo_detector


def discover_emojis(comm_text):
	# Discovers if there're emojis in text and gets their sentiment score

	has_emoji = text_has_emoji(comm_text)
	if has_emoji[1] is True:
		emojies = has_emoji[0]
		emoji_sentiment = get_emoji_sentiment_rank_multiple(emojies)
		sentiment_list = [i['emoji_sentiment_rank']['sentiment_score'] for i in emoji_sentiment]
		sentiment_score = np.mean(sentiment_list)
		if sentiment_score < 0:
			return "NEG"
		elif sentiment_score > 0.2:
			return "POS"
		else:
			return "NEU"
	else:
		return "NEU"



def update_db_with_sentiment(db_name):
	# Connects to the database, gets all the comments and conducts the sentiment analysis
	conn = SQL.connect(db_name)
	cur = conn.cursor()

	cur.execute('SELECT comment_id, content, sentiment FROM Comments WHERE sentiment IS NULL')
	comments_without_sentiments = cur.fetchall()

	res_message = "\t\t>>> NO NEW COMMENTS TO ANALYSE <<<"

	for num, comment in enumerate(comments_without_sentiments):

		print("\n"*30, "\t\t>>> {} COMMENTS, {}% TEXTS AND EMOJIES PROCESSED <<<".format(num, int(num/len(comments_without_sentiments)*100)))

		comm_id = comment[0]
		comm_text = comment[1]

		emoji_sentiment = discover_emojis(comm_text)

		try:
			processed_comment = analyse_sentiments(comm_text)
			comm_sentiment = processed_comment[0]
			comm_confidence = processed_comment[1]

			print("COMMENT: ", comm_text)
			print("TEXT SENTIMENT: ", comm_sentiment)
			print("EMOJI SENTIMENT: ", emoji_sentiment)

			# Here we amend the comment text sentiment evaluation according to the emoji's sentiment evaluation
			if comm_sentiment =="NEU" and emoji_sentiment == "POS":
				comm_sentiment = "POS"
				confidence = 0
			elif comm_sentiment =="NEU" and emoji_sentiment == "NEG":
				comm_sentiment = "NEG"
				confidence = 0
			else:
				pass

			cur.execute('UPDATE Comments SET sentiment = ?, confidence = ? WHERE comment_id = ?', 
				(comm_sentiment, comm_confidence, comm_id))
			conn.commit()
			res_message = "\t>>> YOUR COMMENTS DATABASE HAS BEEN UPDATED WITH SEMANTICS <<<"

		except (KeyError, IndexError):
			conn.commit()
			res_message = "\t\t>>> !!! DATA UPDATE RESULTED AN ERROR !!! <<<"
			print(res_message)
			break 

	conn.commit()
	cur.close()

	print("\n"*30, res_message)


if __name__ == "__main__":
	update_db_with_sentiment("main_db.sqlite")

