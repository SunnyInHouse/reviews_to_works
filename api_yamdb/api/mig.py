# import csv, sqlite3
#
# con = sqlite3.connect("db.sqlite3") # change to 'sqlite:///your_filename.db'
# cur = con.cursor()
# # cur.execute("CREATE TABLE users_user (id,username,email,role,bio,first_name,last_name);") # use your column names here
#
# with open('static/data/users.csv','r') as fin: # `with` statement available in 2.5+
#     # csv.DictReader uses first line in file for column headings by default
#     dr = csv.DictReader(fin) # comma is default delimiter
#     to_db = [(i['id'], i['username'],i['email'], i['role'],i['bio'], i['first_name'],i['last_name']) for i in dr]
#
# cur.executemany("INSERT INTO users_user (id,username,email,role,bio,first_name,last_name) VALUES (?,?,?,?,?,?,?);", to_db)
# con.commit()
# con.close()
#
#
#
# con = sqlite3.connect("db.sqlite3") # change to 'sqlite:///your_filename.db'
# cur = con.cursor()
# # cur.execute("CREATE TABLE reviews_titles (id,name,year,category_id);") # use your column names here
#
# with open('static/data/titles.csv','r') as fin: # `with` statement available in 2.5+
#     # csv.DictReader uses first line in file for column headings by default
#     dr = csv.DictReader(fin) # comma is default delimiter
#     to_db = [(i['id'], i['name'],i['year'], i['category']) for i in dr]
#
# cur.executemany("INSERT INTO reviews_title (id,name,year,category_id) VALUES (?,?,?,?);", to_db)
# con.commit()
# con.close()
#
#
# con = sqlite3.connect("db.sqlite3") # change to 'sqlite:///your_filename.db'
# cur = con.cursor()
# cur.execute("CREATE TABLE reviews_genre_title (id,title_id,genre_id);") # use your column names here
#
# with open('static/data/genre_title.csv','r') as fin: # `with` statement available in 2.5+
#     # csv.DictReader uses first line in file for column headings by default
#     dr = csv.DictReader(fin) # comma is default delimiter
#     to_db = [(i['id'], i['title_id'],i['genre_id']) for i in dr]
#
# cur.executemany("INSERT INTO reviews_genre_title (id,title_id,genre_id) VALUES (?,?,?);", to_db)
# con.commit()
# con.close()
#
#
# con = sqlite3.connect("db.sqlite3") # change to 'sqlite:///your_filename.db'
# cur = con.cursor()
# # cur.execute("CREATE TABLE reviews_category (id,name,slug);") # use your column names here
#
# with open('static/data/category.csv','r') as fin: # `with` statement available in 2.5+
#     # csv.DictReader uses first line in file for column headings by default
#     dr = csv.DictReader(fin) # comma is default delimiter
#     to_db = [(i['id'], i['name'],i['slug']) for i in dr]
#
# cur.executemany("INSERT INTO reviews_category (id,name,slug) VALUES (?,?,?);", to_db)
# con.commit()
# con.close()
#
#
# con = sqlite3.connect("db.sqlite3") # change to 'sqlite:///your_filename.db'
# cur = con.cursor()
# # cur.execute("CREATE TABLE reviews_reviews (id,title_id,text,author,score,pub_date);") # use your column names here
#
# with open('static/data/review.csv','r') as fin: # `with` statement available in 2.5+
#     # csv.DictReader uses first line in file for column headings by default
#     dr = csv.DictReader(fin) # comma is default delimiter
#     to_db = [(i['id'], i['title_id'],i['text'], i['author'],i['score'], i['pub_date']) for i in dr]
#
# cur.executemany("INSERT INTO reviews_reviews (id,title_id,text,author_id,score,pub_date) VALUES (?,?,?,?,?,?);", to_db)
# con.commit()
# con.close()
#
#
# con = sqlite3.connect("db.sqlite3") # change to 'sqlite:///your_filename.db'
# cur = con.cursor()
# # cur.execute("CREATE TABLE reviews_comments (id,review_id,text,author,pub_date);") # use your column names here
#
# with open('static/data/comments.csv','r') as fin: # `with` statement available in 2.5+
#     # csv.DictReader uses first line in file for column headings by default
#     dr = csv.DictReader(fin) # comma is default delimiter
#     to_db = [(i['id'], i['review_id'],i['text'], i['author'],i['pub_date']) for i in dr]
#
# cur.executemany("INSERT INTO reviews_comments (id,review_id,text,author_id,pub_date) VALUES (?,?,?,?,?);", to_db)
# con.commit()
# con.close()