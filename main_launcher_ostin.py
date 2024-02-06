from vk_parser_v2 import main_routine as posts_parser_short
from vk_parser_hist import main_routine as post_parser_long
from user_info_upd import update_db_with_user_data
from review_analysis import update_db_with_sentiment
from city_update import get_cities, get_lat_lon


if __name__=="__main__":
	posts_parser_short()
	# post_parser_long()
	update_db_with_user_data()
	update_db_with_sentiment()
	get_cities()
	get_lat_lon()

