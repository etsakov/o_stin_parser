import pandas as pd 
import numpy as np
import sqlite3 as SQL
from datetime import datetime, time

# This script is devoted to the datasets preparing process. We need to prepare a number of tabels for future interactions with dashboard logics

def create_pd_tables():
	# Here we connect to the database and make three correspondant dataframes: comments, posts, users

	conn = SQL.connect('main_db.sqlite')
	comments_df = pd.read_sql_query("SELECT * FROM Comments", conn)
	posts_df = pd.read_sql_query("SELECT * FROM Posts", conn)
	users_df = pd.read_sql_query("SELECT * FROM Users", conn)
	locations_df = pd.read_sql_query("SELECT * FROM Locations", conn)

	return comments_df, posts_df, users_df, locations_df


def build_metadataframe():
	# Now we need to build a metadataframe for the future manipulations

	raw_tables = create_pd_tables()

	raw_comments_df = raw_tables[0]
	raw_posts_df = raw_tables[1]
	raw_users_df = raw_tables[2]
	raw_locs_df = raw_tables[3]

	raw_posts_df.drop(columns=["owner_id"], inplace=True)
	raw_comments_df.rename(columns={
		"comment_datetime" : "comm_datetime",
		"content" : "comm_content", 
		"like_count" : "comm_like_count",
		"replies_count" : "comm_replies_count",
		"reply_at" : "comm_reply_at",
		"sentiment" : "comm_sentiment",
		"confidence" : "comm_confidence"}, inplace=True)
	raw_posts_df.rename(columns={
		"comments_count" : "post_comments_count",
		"views_count" : "post_views_count",
		"like_count" : "post_like_count"}, inplace=True)


	# Now we merge all dataframes in a bigger one
	meta_df = raw_comments_df.merge(raw_posts_df, on = 'post_id', how = 'left')
	meta_df = meta_df.merge(raw_users_df, on = 'user_id', how = 'left')
	meta_df = meta_df.merge(raw_locs_df, how='left', left_on=['city', 'country'], right_on=['city', 'country'])

	# Let's make some data clearance
	meta_df['comm_datetime'] = pd.to_datetime(meta_df['comm_datetime'], format='%Y-%m-%d %H:%M:%S')
	meta_df['post_datetime'] = pd.to_datetime(meta_df['post_datetime'], format='%Y-%m-%d %H:%M:%S')
	meta_df['comm_replies_count'] = meta_df['comm_replies_count'].fillna(0)
	meta_df['comm_replies_count'] = meta_df['comm_replies_count'].astype(int)

	return meta_df
