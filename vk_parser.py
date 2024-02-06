import requests
import json
from datetime import datetime
import pandas as pd
import time


# read authorization data from private file
with open("creds.txt") as creds:
	lines = [line.rstrip() for line in creds]

APP_ID = lines[0].split('=')[1]
TOKEN = lines[1].split('=')[1]
VERSION = lines[2].split('=')[1]
DOMAIN = "ostin"


def returns_comments(post, owner):
	# returns comments with key details
	# use post_id="417012" and owner_id="-20367999" for test purposes

	comm_request = requests.get('https://api.vk.com/method/wall.getComments', 
		params={
		'access_token': TOKEN,
		'v': VERSION,
		'owner_id': owner,
		'post_id': post,
		'need_likes': "1",
		'extended': "1"
		})

	# try:
	comm_response = comm_request.json()['response']
	comm_items = comm_response['items']
	comm_profiles = comm_response['profiles']

	# make usefull dict with user name
	comm_profiles_dict = {'-20367999':["O'Stin", "owner"]}
	for user in comm_profiles:
		comm_profiles_dict[user['id']] = [user['first_name'], user['last_name']]

	# prepare the comments for future representation and manipulation
	comments_list = list()
	for comment in comm_items:
		comment_dict = dict() 
		comment_dict["id"] = comment['id']
		comment_dict["from"] = comment['from_id']
		comment_dict["first_name"] = comm_profiles_dict[comment['from_id']][0]
		comment_dict["last_name"] = comm_profiles_dict[comment['from_id']][1]
		comment_dict["datetime"] = datetime.fromtimestamp(comment['date'])
		comment_dict["text"] = comment['text']
		comment_dict["likes"] = comment['likes']['count']
		comment_dict["replies_num"] = comment['thread']['count']

		print("COMMENT ID: ", comment['id'])
		print("FROM ID: ", comment['from_id'])
		print("FIRST NAME: ", comm_profiles_dict[comment['from_id']][0])
		print("LAST NAME: ", comm_profiles_dict[comment['from_id']][1])
		print("DATE: ", datetime.fromtimestamp(comment['date']))
		print("TEXT: ", comment['text'])
		print("LIKES: ", comment['likes']['count'])
		print("REPLIES: ", comment['thread']['count'])


		if comment['thread']['count'] > 0:
		# Add replies_num validation here
			returns_replies(post, owner, comment['id'])
			# replies_content = returns_replies(post, owner, comment['id'])
			# comment_dict["replies_cont"] = [i for i in replies_content]

		else:
			# comment_dict["replies_cont"] = []
			print("\n>>> NO REPLIES <<<\n")
		comments_list.append(comment_dict)

	# [print("\n", i['first_name'], i['last_name'], "\n", i['datetime'], '\n', i['text'], '\n', i['replies_cont']) for i in comments_list]

		# comments_df = pd.DataFrame(comments_list)
		# print(comments_df)
	# except KeyError:
	# 	print(comm_request.json())


def returns_replies(post, owner, comment_id):
	# returns replies on previous comments
	# use returns_replies("417012", "-20367999", "417014" / "0") for test purposes

	comm_request = requests.get('https://api.vk.com/method/wall.getComments', 
		params={
		'access_token': TOKEN,
		'v': VERSION,
		'owner_id': owner,
		'post_id': post,
		'need_likes': "1",
		'extended': "1",
		'comment_id': comment_id
		})

	comm_response = comm_request.json()['response']
	comm_items = comm_response['items']
	comm_profiles = comm_response['profiles']

	# Make another dictionary for users
	comm_profiles_dict = {20367999:["O'Stin", "owner"], -20367999:["O'Stin", "owner"]}
	for user in comm_profiles:
		comm_profiles_dict[user['id']] = [user['first_name'], user['last_name']]

	print("\n>>> HERE IS REPLIES SECTION <<<\n")

	# prepare the comments for future representation and manipulation
	comments_list = list()
	for num, comment in enumerate(comm_items):
		comment_dict = dict() 
		comment_dict["id"] = comment['id']
		comment_dict["from"] = comment['from_id']
		comment_dict["datetime"] = datetime.fromtimestamp(comment['date'])
		comment_dict["text"] = comment['text']
		comment_dict["likes"] = comment['likes']['count']
		comment_dict["first_name"] = comm_profiles_dict[comment['from_id']][0]
		comment_dict["last_name"] = comm_profiles_dict[comment['from_id']][1]
		comments_list.append(comment_dict)
		time.sleep(0.1)

		
		print("\n--- {} REPLY ---".format(num))
		print("comment ID: ", comment['id'])
		print("from ID: ", comment['from_id'])
		print("date: ", datetime.fromtimestamp(comment['date']))
		try:
			print("text: ", comment['text'].split("],")[1])
		except IndexError:
			print("text: ", comment['text'])
		print("likes: ", comment['likes']['count'])
		print("first name: ", comm_profiles_dict[comment['from_id']][0])
		print("last name: ", comm_profiles_dict[comment['from_id']][1])
		print("\nxxx END OF REPLY {} xxx\n".format(num))

	# return comments_list


if __name__ == "__main__":
	# MAIN STREAM
	response = requests.get('https://api.vk.com/method/wall.get', 
		params={
		'access_token': TOKEN,
		'v': VERSION,
		'domain': str("ostin"),
		'count': 100,
		'filter': str("owner")
		})

	data = response.json()['response']['items']


	for num,post in enumerate(data):
		post_id = post['id']
		post_owner_id = post['owner_id']
		post_datetime = datetime.fromtimestamp(post['date'])
		post_comments_count = post['comments']['count']
		post_view_count = post['views']['count']
		post_like_count = post['likes']['count']
		post_repost_count = post['reposts']['count']
		post_text = post['text']

		if post_comments_count > 0:
			print("\n\n\n", "POST {}".format(num))
			print("POST ID: ", post_id)
			print("POST DATE: ", datetime.fromtimestamp(post['date']))
			print(post_text, "\n")
			returns_comments(post_id, post_owner_id)
			print("\n", "*"*12, 'NEXT POST', "*"*12)
		time.sleep(0.1)



