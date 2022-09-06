import sqlite3
import hashlib

def add_user(user, pwd, type):
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    cursor.execute(f'Insert into USER(user,pass,type) values({user},{pwd},{type});')
    conn.commit()
    conn.close()  

with open('users.csv','r') as file:
    lines = file.read().splitlines()

for users in lines:
    (user, type) = users.split(',')
    print(user)
    print(type)
    add_user(user, hashlib.md5(user.encode()).hexdigest(), type)
