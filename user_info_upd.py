import time
import requests
import sqlite3 as SQL
from datetime import datetime
from dateutil.relativedelta import relativedelta

# NB: Obviously VK API allows to execute group data parsing in respect to the users. My current algorythm parses each user one by one.
# This is inefficinet. Needs refactoring on a later stage to make it capable of parsing the entire dataset with all users' info.

with open("creds.txt") as creds:
	lines = [line.rstrip() for line in creds]
APP_ID = lines[0].split('=')[1]
TOKEN = lines[1].split('=')[1]
VERSION = lines[2].split('=')[1]
DOMAIN = "ostin"


def parse_user_data(user_id):
	# Gets user data from VK API
	# https://dev.vk.com/ru/method/users.get
	
	response = requests.get('https://api.vk.com/method/users.get', 
		params={
		'access_token': TOKEN,
		'v': VERSION,
		'user_ids': user_id,
		'fields': "city,country,bdate,sex"
		})
	data = response.json()['response'][0]

	return data


def update_db_with_user_data():
	# Updates the database with users' basic info

	conn = SQL.connect("main_db.sqlite")
	cur = conn.cursor()

	# cur.execute('SELECT user_id, city, country, gender, age FROM Users WHERE gender IS NULL')
	cur.execute('SELECT user_id, city, country, gender, age FROM Users')
	comments_without_sentiments = cur.fetchall()

	for num, row in enumerate(comments_without_sentiments):
		user_id = row[0]
		try:
			user_data = parse_user_data(row[0])
			if 'city' in user_data.keys():
				customer_city = user_data['city']['title']
				cur.execute('UPDATE Users SET city = ? WHERE user_id = ?', (customer_city, user_id))

			if 'country' in user_data.keys():
				customer_country = user_data['country']['title']
				cur.execute('UPDATE Users SET country = ? WHERE user_id = ?', (customer_country, user_id))

			if 'sex' in user_data.keys():
				if user_data['sex'] == 1:
					customer_sex = 'female'
				elif user_data['sex'] == 2:
					customer_sex = 'male'
				else:
					customer_sex = None
				cur.execute('UPDATE Users SET gender = ? WHERE user_id = ?', (customer_sex, user_id))

			if 'bdate' in user_data.keys():
				customer_bdate = user_data['bdate']
				if len(customer_bdate.split(".")) == 3:
					customer_age = datetime.strptime(customer_bdate, '%d.%m.%Y')
					customer_age = relativedelta(datetime.now(), customer_age).years
					cur.execute('UPDATE Users SET age = ? WHERE user_id = ?', (customer_age, user_id))

		except (IndexError, KeyError, ConnectionResetError):
			time.sleep(10)
			continue

		print("\n"*30, "\t\t>>> {}% USERS PROCESSED <<<".format(int(num/len(comments_without_sentiments)*100)))
		time.sleep(0.3)

	conn.commit()
	cur.close()

	print("\n"*30, "\t\t>>> YOUR USER DATABASE HAS BEEN UPDATED <<<")

# if __name__ == "__main__":
# 	update_db_with_user_data()







