from o_stin_tables import build_metadataframe
import plotly.express as px
import streamlit as st 
import numpy as np
import datetime

# https://docs.streamlit.io/library/api-reference/charts
# https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/

st.title("Добро пожаловать в анализатор отзывов O'Stin :sparkles:")
st.markdown("##### Здесь мы собираем и анализируем статистику по отзывам о постах компании в социальной сети 'ВКонтакте'")

# Settings menu introduction
st.sidebar.title("Меню настроек 🪄")
st.sidebar.markdown("Для удобства использования меню, некоторые пункты скрыты по умолчанию")

@st.cache(persist=True)
def load_data():
	# Connects to DB, makes all necessary pre-processing and uploads the data
	metadataframe = build_metadataframe()

	# print(metadataframe.columns)

	return metadataframe


def apply_filters(meta_df):
	# Creates a set of filters for the user

	# Datetime filters
	st.sidebar.subheader("Временные диапазоны")

	today = datetime.datetime.now()
	start_date = today - datetime.timedelta(days=30)
	beginning_date = np.min(meta_df.post_datetime)

	# Posts timeframe filter
	p_left_frame = beginning_date.date()
	p_right_frame = today.date()
	post_dt_filter = st.sidebar.checkbox("Указать период постов", key="disabled")
	if post_dt_filter is True:
		post_dt_frame = st.sidebar.date_input(
			"Укажите период интересующих постов", 
			(start_date, today),
			min_value=beginning_date,
			max_value=today
			)
		p_left_frame = post_dt_frame[0]
		p_right_frame = post_dt_frame[1]
	meta_df = meta_df[(meta_df.post_datetime.dt.date >= p_left_frame) & (meta_df.post_datetime.dt.date <= p_right_frame)]

	# Comments timeframe filter
	c_left_frame = beginning_date.date()
	c_right_frame = today.date()
	comment_dt_filter = st.sidebar.checkbox("Указать период комментариев", key="disabled")
	if comment_dt_filter is True:
		comment_dt_frame = st.sidebar.date_input(
			"Укажите период интересующих комментариев",
			(start_date, today),
			min_value=beginning_date,
			max_value=today
			)
		c_left_frame = comment_dt_frame[0]
		c_right_frame = comment_dt_frame[1]
	meta_df = meta_df[(meta_df.comm_datetime.dt.date >= c_left_frame) & (meta_df.comm_datetime.dt.date <= c_right_frame)]

	# Gender filter
	st.sidebar.subheader("Выберите пол пользователя")
	fem_filter = st.sidebar.checkbox("Женский", key="disabled")
	male_filter = st.sidebar.checkbox("Мужской", key="disabled")

	if fem_filter is True and male_filter is False:
		# Female only case
		meta_df = meta_df[meta_df.gender == "female"]
	elif fem_filter is False and male_filter is True:
		# Male only case
		meta_df = meta_df[meta_df.gender == "male"]
	else:
		pass

	# Age filter
	st.sidebar.subheader("Возраст пользователя")
	check_age = st.sidebar.checkbox("Указать возраст пользователей", key="disabled")

	if check_age is True:
		age_limits = st.sidebar.slider("Выберите диапазон возраста пользователей", 0, 100, (int(np.min(meta_df.age)), 70))
		meta_df = meta_df[(meta_df.age >= np.min(age_limits)) & (meta_df.age <= np.max(age_limits))]


	# Location filter
	st.sidebar.subheader("Место проживания пользователя")
	check_country = st.sidebar.checkbox("Выбрать страны проживания", key="disabled")

	if check_country is True:
		country_list = [x for x in meta_df.country.unique() if isinstance(x, str)]
		default_country = []
		if "Russia" in country_list:
			default_country = "Russia"
		country_options = st.sidebar.multiselect("Выберите страны:", 
			options = sorted(country_list),
			default = default_country,
			help="Не у всех пользователей указано место проживания"
			)
		meta_df = meta_df[meta_df["country"].isin(country_options)]

		# turn on city filter
		check_city = st.sidebar.checkbox("Выбрать города проживания", key="disabled")
		if check_city is True:
			city_list = [x for x in meta_df.city.unique() if x is not None]
			city_options = st.sidebar.multiselect("Выберите города проживания:",
				options = sorted(city_list)
				)
			meta_df = meta_df[meta_df["city"].isin(city_options)]

	return meta_df


def draw_locs_map(clear_df):
	# Draws a map with users locations
	# https://coderzcolumn.com/tutorials/data-science/geoplot-scatter-and-bubble-maps-python

	st.sidebar.subheader("Показать карту")

	meta_map_df = clear_df[["latitude", "longitude"]]
	meta_map_df = meta_map_df.dropna(subset=["latitude", "longitude"])
	if st.sidebar.checkbox("Показать", False, key="0"):
		st.markdown("#### Географическое распределение пользователей")
		st.markdown("Используйте скроллинг для масштабирования")
		st.map(meta_map_df)


def get_smile(pos_val, neg_val):
	# Returns proper smile

	if pos_val > neg_val:
		sent_smile = "😃"
	elif pos_val < neg_val:
		sent_smile = "😠"
	else:
		sent_smile = "😑"

	return sent_smile


def get_inputs_in_age_groups(age_df):
	# Returns number of positive and negative comments together with overall sentiment score

	age_pos_comm_df = age_df[age_df.comm_sentiment == "POS"]
	age_neg_comm_df = age_df[age_df.comm_sentiment == "NEG"]
	age_pos_num = age_pos_comm_df.shape[0]
	age_neg_num = age_neg_comm_df.shape[0]
	try:
		age_overall_score = (age_pos_num-age_neg_num)/(age_pos_num+age_neg_num)*100
	except ZeroDivisionError:
		age_overall_score = 0

	return age_pos_num, age_neg_num, age_overall_score


def get_smilie_diagrams(clear_df):
	# Builds the gender diagrams over the filtered data

	# st.text(clear_df.columns)

	# Split the data in accordance with the sentiment evaluation results
	positive_comms = clear_df[clear_df.comm_sentiment == "POS"]
	negative_comms = clear_df[clear_df.comm_sentiment == "NEG"]

	# 1) Overall sentiment smile;  Female sentiment smile;  Male sentiment smile;  Female vs. Male
	# General sentiment
	pos_num = positive_comms.shape[0]
	neg_num = negative_comms.shape[0]
	try:
		overall_score = (pos_num-neg_num)/(pos_num+neg_num)*100
	except ZeroDivisionError:
		overall_score = 0

	# Female sentiment
	fem_positive_comms = positive_comms[positive_comms.gender == "female"]
	fem_negative_comms = negative_comms[negative_comms.gender == "female"]
	fem_pos_num = fem_positive_comms.shape[0]
	fem_neg_num = fem_negative_comms.shape[0]
	try:
		fem_overall = (fem_pos_num-fem_neg_num)/(fem_pos_num+fem_neg_num)*100
	except ZeroDivisionError:
		fem_overall = 0

	# Male sentiment
	male_positive_comms = positive_comms[positive_comms.gender == "male"]
	male_negative_comms = negative_comms[negative_comms.gender == "male"]
	male_pos_num = male_positive_comms.shape[0]
	male_neg_num = male_negative_comms.shape[0]
	try:
		male_overall = (male_pos_num-male_neg_num)/(male_pos_num+fem_neg_num)*100
	except ZeroDivisionError:
		male_overall = 0

	# Gender balance
	fem_comms = clear_df[clear_df.gender == "female"]
	male_comms = clear_df[clear_df.gender == "male"]
	fem_num = fem_comms.shape[0]
	male_num = male_comms.shape[0]

	if fem_num-male_num < 0:
		gender_img = "♂️"
		try:
			gender_balance_score = (male_num-fem_num)/(male_num+fem_num)*100
		except ZeroDivisionError:
			gender_balance_score = 0
	else:
		gender_img = "♀️"
		try:
			gender_balance_score = (fem_num-male_num)/(fem_num+male_num)*100
		except ZeroDivisionError:
			gender_balance_score = 0

	st.markdown("#### Тональность комменатриев в зависимости от пола:")
	col1, col2, col3, col4 = st.columns(4)
	col1.metric("Общее настроение", get_smile(pos_num, neg_num), str(int(overall_score))+"%")
	col2.metric("Настроение женщин", get_smile(fem_pos_num, fem_neg_num), str(int(fem_overall))+"%")
	col3.metric("Настроение мужчин", get_smile(male_pos_num, male_neg_num), str(int(male_overall))+"%")
	col4.metric("Соотношение полов", gender_img, str(int(gender_balance_score))+"%")


	# 2) 19- sentiment smile;   20-39 sentiment smile;  40-59 sentiment smile;   60+ sentiment smile
	# Split by the age group

	null_age_df = clear_df[clear_df.age <= 19]
	twenty_age_df = clear_df[(clear_df.age >= 20) & (clear_df.age <= 39)]
	forty_age_df = clear_df[(clear_df.age >= 40) & (clear_df.age <= 59)]
	sixty_age_df = clear_df[clear_df.age >= 60]

	null_pos_num, null_neg_num, null_overall_score = get_inputs_in_age_groups(null_age_df)
	twenty_pos_num, twenty_neg_num, twenty_overall_score = get_inputs_in_age_groups(twenty_age_df)
	forty_pos_num, forty_neg_num, forty_overall_score = get_inputs_in_age_groups(forty_age_df)
	sixty_pos_num, sixty_neg_num, sixty_overall_score = get_inputs_in_age_groups(sixty_age_df)
	
	st.markdown("  #### Тональность комменатриев по разным возрастным группам:")
	col1, col2, col3, col4 = st.columns(4)
	col1.metric("Подростки (до 20 лет)", get_smile(null_pos_num, null_neg_num), str(int(null_overall_score))+"%")
	col2.metric("Молодёжь (20-39 лет)", get_smile(twenty_pos_num, twenty_neg_num), str(int(twenty_overall_score))+"%")
	col3.metric("Взрослые (40-59 лет)", get_smile(forty_pos_num, forty_neg_num), str(int(forty_overall_score))+"%")
	col4.metric("Пожилые (60+ лет)", get_smile(sixty_pos_num, sixty_neg_num), str(int(sixty_overall_score))+"%")

	
	# 3) Positive distribution over gender groups + Negative distribution over gender groups
	# pos_gender_fig = px.histogram(positive_comms, x='gender')

	# st.markdown("  #### Распределение тональности комментариев между мужчинами и женщинами:")


	# 4) Positive distribution over age groups + Negative distribution over age groups
	# 5) Top-10 posts with max positive comments + views, comment nums, reposts etc.
	# 6) Top-10 posts with max negative comments + views, comment nums, reposts etc.
	# 7) Word cloud of the most frequent words


if __name__ == "__main__":
	metadata = load_data()
	filtered_df = apply_filters(metadata)
	get_smilie_diagrams(filtered_df)
	draw_locs_map(filtered_df)
