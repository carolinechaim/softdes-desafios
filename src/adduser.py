import sqlite3
import hashlib

def add_user(user, pwd, type):
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    cursor.execute(f'INSERT or IGNORE INTO USER(user,pass,type) VALUES("{user}","{pwd}","{type}");')
    conn.commit()
    conn.close()  

with open('users.csv','r') as file:
    lines = file.read().splitlines()

for users in lines:
    (user, type) = users.split(',')
    print(user)
    print(type)
    try:
        add_user(user, hashlib.md5(user.encode()).hexdigest(), type)
    except Exception as err:
        print(Exception, err)
  
