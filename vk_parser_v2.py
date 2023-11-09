import json
import time
import requests
import sqlite3 as SQL
from datetime import datetime

# from vk_parser_cls import Post, Comment, User


with open("creds.txt") as creds:
	lines = [line.rstrip() for line in creds]
APP_ID = lines[0].split('=')[1]
TOKEN = lines[1].split('=')[1]
VERSION = lines[2].split('=')[1]
DOMAIN = "ostin"


def parse_vk_api_wall(number_of_posts):
	# Gets 100 reviews dump from VK database

	response = requests.get('https://api.vk.com/method/wall.get', 
		params={
			'access_token': TOKEN,
			'v': VERSION,
			'domain': str("ostin"),
			'count': number_of_posts,
			'offset': 100,
			'filter': str("owner")
			})
	data = response.json()['response']['items']
	return data

	# offset = 0
	# all_data = []
	# while offset <= 1000:
	# 	response = requests.get('https://api.vk.com/method/wall.get', 
	# 		params={
	# 		'access_token': TOKEN,
	# 		'v': VERSION,
	# 		'domain': str("ostin"),
	# 		'count': number_of_posts,
	# 		'offset': offset,
	# 		'filter': str("owner")
	# 		})
	# 	data = response.json()['response']['items']
	# 	all_data.extend(data)
	# 	offset += number_of_posts
	# 	time.sleep(0.5)

	# return all_data


def parse_vk_comments(*args):
	# Gets comments to a post or replies to comment
	post = args[0]
	owner = args[1]
	comment_id = 0
	if len(args) == 3:
		comment_id = args[2]

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

	# We set time.sleep in order not to exceed a request limit restriction
	time.sleep(1)

	return comm_response


def create_db(database_name):
	# Here we prepare our database and create tables Posts, Comments, Users
	conn = SQL.connect(database_name + ".sqlite")
	cur = conn.cursor()

	# Create required tables if they don't exist
	cur.executescript('''
		CREATE TABLE IF NOT EXISTS Posts
		(post_id INTEGER NOT NULL PRIMARY KEY UNIQUE, owner_id INTEGER, post_datetime DATETIME, 
		comments_count INTEGER, views_count INTEGER, like_count INTEGER, repost_count INTEGER);

		CREATE TABLE IF NOT EXISTS Comments
		(comment_id INTEGER NOT NULL PRIMARY KEY UNIQUE, post_id INTEGER, user_id INTEGER, comment_datetime DATETIME, 
		content TEXT, like_count INTEGER, replies_count INTEGER, reply_at INTEGER, sentiment TEXT, confidence REAL);

		CREATE TABLE IF NOT EXISTS Users
		(user_id INTEGER NOT NULL PRIMARY KEY UNIQUE, first_name TEXT, last_name TEXT, 
		gender TEXT, age INTEGER, city TEXT, country TEXT);
		''')

	# Set relations between tables in our database
	cur.execute('SELECT Posts.post_id FROM Posts JOIN Comments ON Posts.post_id = Comments.post_id')
	cur.execute('''SELECT Comments.post_id, Comments.user_id FROM Comments JOIN Posts JOIN Users
		ON Comments.post_id = Posts.post_id AND Comments.user_id = Users.user_id''')
	cur.execute('SELECT Users.user_id FROM Users JOIN Comments ON Users.user_id = Comments.user_id')

	conn.commit()
	cur.close()


def put_comments_data_to_db(post_id, owner_id, database_name):
	# Puts comments data into the database
	conn = SQL.connect(database_name + ".sqlite")
	cur = conn.cursor()

	comment_data = parse_vk_comments(post_id, owner_id)
	comm_items = comment_data['items']
	comm_profiles = comment_data['profiles']

	# Put all users' profiles into the database
	cur.execute('''INSERT OR IGNORE INTO Users (user_id, first_name, last_name)
		VALUES (20367999, "O'Stin", "owner"), (-20367999, "O'Stin", "owner");
		''')

	for user in comm_profiles:
		cur.execute('''INSERT OR IGNORE INTO Users (user_id, first_name, last_name)
			VALUES ( ?, ?, ?)''', (user['id'], user['first_name'], user['last_name']))

	# Put all first-level comments into the database
	for comment in comm_items:
		cur.execute('''INSERT INTO Comments (comment_id, post_id, user_id, comment_datetime, content, like_count, replies_count)
			VALUES ( ?, ?, ?, ?, ?, ?, ?) ON CONFLICT (comment_id) DO UPDATE SET
				like_count=excluded.like_count,
				replies_count=excluded.replies_count;
			''', (comment['id'], post_id, comment['from_id'], datetime.fromtimestamp(comment['date']), comment['text'], 
				comment['likes']['count'], comment['thread']['count']))

		# Put all replies into the database
		if comment['thread']['count'] > 0:
			reply_data = parse_vk_comments(post_id, owner_id, comment['id'])
			reply_items = reply_data['items']
			reply_profiles = reply_data['profiles']

			for user in reply_profiles:
				cur.execute('''INSERT OR IGNORE INTO Users (user_id, first_name, last_name)
					VALUES ( ?, ?, ?)''', (user['id'], user['first_name'], user['last_name']))

			for reply in reply_items:
				# Remove irrelevant part from comment
				try:
					reply_content = reply['text'].split("],")[1]
				except IndexError:
					reply_content = reply['text']

				cur.execute('''INSERT INTO Comments (comment_id, post_id, user_id, comment_datetime, content, like_count, reply_at)
					VALUES ( ?, ?, ?, ?, ?, ?, ?) ON CONFLICT (comment_id) DO UPDATE SET
						like_count=excluded.like_count;
					''', (reply['id'], post_id, reply['from_id'], datetime.fromtimestamp(reply['date']), reply_content, 
						reply['likes']['count'], comment['id']))

	conn.commit()
	cur.close()


def put_post_to_db(post_json, database_name):
	# Puts post data into the database
	conn = SQL.connect(database_name + ".sqlite")
	cur = conn.cursor()

	# Get post data
	post_id = post_json['id']
	post_owner_id = post_json['owner_id']
	post_datetime = datetime.fromtimestamp(post_json['date'])
	post_comments_count = post_json['comments']['count']
	post_view_count = post_json['views']['count']
	post_like_count = post_json['likes']['count']
	post_repost_count = post_json['reposts']['count']

	# Put post data to the database
	cur.execute('''INSERT INTO Posts (post_id, owner_id, post_datetime, comments_count, views_count, like_count, repost_count)
		VALUES ( ?, ?, ?, ?, ?, ?, ?) ON CONFLICT (post_id) DO UPDATE SET
			comments_count=excluded.comments_count,
			views_count=excluded.views_count,
			like_count=excluded.like_count,
			repost_count=excluded.repost_count;
		''', (post_id, post_owner_id, post_datetime, post_comments_count, post_view_count, post_like_count, post_repost_count))

	conn.commit()
	cur.close()

	# Execute comments collection
	put_comments_data_to_db(post_id, post_owner_id, database_name)


def get_comments_and_users(parsed_data, database_name):
	# Extracts comments, replies and users from parsed data

	for num, post_json in enumerate(parsed_data):
		print("\n"*30, "\t\t>>> {}% COMMENTS PROCESSED <<<".format(int(num/len(parsed_data)*100)))
		if post_json['comments']['count'] > 0:
			try:
				put_post_to_db(post_json, database_name)
			except KeyError:
				time.sleep(3)
				continue

	print("\n"*30, "\t\t>>> YOUR MAIN DATABASE HAS BEEN UPDATED <<<")


if __name__=="__main__":
	# MAIN STREAM
	db_name = "main_db"
	create_db(db_name)
	posts_data = parse_vk_api_wall(100)
	get_comments_and_users(posts_data, db_name)













