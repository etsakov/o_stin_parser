class Post:
	# Each VK post on O'Stin page is an object of class Post
	def __init__(self, 
		post_id, 
		owner_id, 
		datetime, 
		comments_count, 
		view_count, 
		like_count, 
		repost_count):
		self.post_id = post_id 
		self.owner_id = owner_id
		self.datetime = datetime 
		self.comments_count = comments_count
		self.view_count = view_count
		self.like_count = like_count
		self.repost_count = repost_count

	def get_post_id(self):
		return self.post_id 

	def get_owner_id(self):
		return self.owner_id

	def get_datetime(self):
		return self.datetime

	def get_comments_count(self):
		return self.comments_count

	def get_view_count(self):
		return self.view_count 

	def get_like_count(self):
		return self.like_count 

	def get_repost_count(self):
		return self.repost_count 


class Comment:
	# Each review is an object of class Comment
	def __init__(self, 
		post_id, 
		comment_id, 
		from_id, 
		datetime, 
		text, 
		likes, 
		replies_num=None, 
		reply_to_comm=None):
		self.post_id = post_id
		self.comment_id = comment_id
		self.from_id = from_id
		self.datetime = datetime
		self.text = text
		self.likes = likes
		self.replies_num = replies_num
		self.reply_to_comm = reply_to_comm

	def get_post_id(self):
		return self.post_id

	def get_comment_id(self):
		return self.comment_id

	def get_from_id(self):
		return self.from_id 

	def get_datetime(self):
		return self.datetime 

	def get_text(self):
		return self.text 

	def get_likes(self):
		return self.likes 

	def get_replies_num(self):
		return self.replies_num 

	def get_reply_to_comm(self):
		return self.reply_to_comm 


class User:
	# Each VK user that appear in comments on O'Stin page is an object of class User
	def __init__(self, 
		user_id, 
		first_name, 
		last_name, 
		sex=None, 
		age=None, 
		city=None, 
		country=None):
		self.user_id = user_id
		self.first_name = first_name
		self.last_name = last_name
		self.sex = sex
		self.age = age
		self.city = city
		self.country = country

	def get_user_id(self):
		return self.user_id 

	def get_first_name(self):
		return self.first_name 

	def get_last_name(self):
		return self.last_name 

	def get_sex(self):
		return self.sex 

	def get_age(self):
		return self.age 

	def get_city(self):
		return self.city 

	def get_country(self):
		return self.country









