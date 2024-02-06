import sqlite3 as SQL
from geopy.geocoders import Nominatim

def get_cities():
	# Gets a unique list of cities in countries

	conn = SQL.connect("main_db.sqlite")
	cur = conn.cursor()

	# Create Locations table
	cur.executescript('CREATE TABLE IF NOT EXISTS Locations (city TEXT, country TEXT, latitude REAL, longitude REAL);')

	# Get all unique cities in countries table from Users table and past it into Locations table
	cur.execute('SELECT city, country FROM Users GROUP BY city, country')
	all_cities = cur.fetchall()

	cur.execute('SELECT city, country FROM Locations GROUP BY city, country')
	all_locs = cur.fetchall()

	new_locs = [loc for loc in all_cities if loc not in all_locs]

	for city_country in new_locs:
		cur.execute('INSERT OR IGNORE INTO Locations (city, country) VALUES (?, ?)', (city_country[0], city_country[1]))

	cur.execute('DELETE FROM Locations WHERE city IS NULL AND country IS NULL')
	conn.commit()
	cur.close()


def get_lat_lon():
	# Gets latitude and longitude data according to city and country names

	conn = SQL.connect("main_db.sqlite")
	cur = conn.cursor()

	cur.execute('SELECT city, country FROM Locations WHERE latitude IS NULL')
	all_cities = cur.fetchall()

	geolocator = Nominatim(user_agent="o_stin_parser")
	for city_country in all_cities:
		try:
			if city_country[0] is None and city_country[1] is None:
				pass
			elif city_country[0] is None and city_country[1] is not None:
				loc_full = (city_country[1])
			elif city_country[1] is None and city_country[0] is not None:
				loc_full = (city_country[0])
			else:
				loc_full = (city_country[0] + ", " + city_country[1])

			location = geolocator.geocode(loc_full)
			loc_latitude = location.latitude
			loc_longitude = location.longitude
		except AttributeError:
			loc_full = (city_country[1])
			location = geolocator.geocode(loc_full)
			loc_latitude = location.latitude
			loc_longitude = location.longitude

		print(loc_full, loc_latitude, loc_longitude)
		# cur.execute('SELECT * FROM Locations WHERE city=? AND country=?', (city_country[0], city_country[1]))
		if city_country[0] is None and city_country[1] is not None:
			cur.execute('UPDATE Locations SET latitude=?, longitude=? WHERE city IS NULL AND country=?', (loc_latitude, loc_longitude, city_country[1]))
		elif city_country[1] is None and city_country[0] is not None:
			cur.execute('UPDATE Locations SET latitude=?, longitude=? WHERE city=? AND country IS NULL', (loc_latitude, loc_longitude, city_country[0]))
		else:
			cur.execute('UPDATE Locations SET latitude=?, longitude=? WHERE city=? AND country=?', 
				(loc_latitude, loc_longitude, city_country[0], city_country[1]))
		conn.commit()

	cur.close()
	print("\n"*30, "\t\t>>> YOUR LOCATIONS DATABASE HAS BEEN UPDATED <<<")


# if __name__=="__main__":
# 	db_name = "main_db"
# 	get_cities(db_name)
# 	get_lat_lon(db_name)