# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 09:00:39 2017

@author: rauli
"""

import numbers
from datetime import datetime
import sqlite3
import hashlib
import flask_httpauth 
from flask import Flask, request, render_template

DBNAME = './quiz.db'

def lambda_handler(event, context):
    try:
        def not_equals(first, second):
            if isinstance(first, numbers.Number) and isinstance(second, numbers.Number):
                return abs(first - second) > 1e-3
            return first != second

        # TODO implement
        ndes = int(event['ndes'])
        code = event['code']
        args = event['args']
        resp = event['resp']
        diag = event['diag']
        exec(code, locals())

        test = []
        for index, arg in enumerate(args):
            if not f'desafio{ndes}' in locals():
                return f"Nome da função inválido. Usar 'def desafio{ndes}(...)'"

            if not_equals(eval(f'desafio{ndes}(*arg)'), resp[index]):
                test.append(diag[index])

        return " ".join(test)
    except:
        return "Função inválida."


def converte_data(orig):
    """ ada """
    return orig[8:10]+'/'+orig[5:7]+'/'+orig[0:4]+' '+orig[11:13]+':'+orig[14:16]+':'+orig[17:]


def get_quizes(user):
    """ pega os quizes que podem ser feitos"""
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if user == 'admin' or user == 'fabioja':
        cursor.execute("SELECT id, numb from QUIZ".format(date))
    else:
        cursor.execute(f"SELECT id, numb from QUIZ where release < '{date}'")

    info = [reg for reg in cursor.fetchall()]
    conn.close()
    return info


def get_user_quiz(userid, quizid):
    """ pega um quiz para um aluno """
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT sent,answer,result from USERQUIZ where userid = '{userid}' and quizid = {quizid} order by sent desc")
    info = [reg for reg in cursor.fetchall()]
    conn.close()
    return info


def set_user_quiz(userid, quizid, sent, answer, result):
    """ envia a resposta dada pelo aluno """
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute(
        f"insert into USERQUIZ({userid},{quizid},{sent},{answer},{result}) values (?,?,?,?,?);")
    conn.commit()
    conn.close()


def get_quiz(id, user):
    """ pega um quiz que pode ser feito """
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if user == 'admin' or user == 'fabioja':
        cursor.execute(
            f"SELECT id, release, expire, problem, tests, results, diagnosis, numb from QUIZ where id = {id}")
    else:
        cursor.execute(
            f"SELECT id, release, expire, problem, tests, results, diagnosis, numb from QUIZ where id = {id} and release < '{date}'")
    info = [reg for reg in cursor.fetchall()]
    conn.close()
    return info


def set_info(pwd, user):
    """ atualiza o nome de usuario """
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE USER set pass = ? where user = ?", (pwd, user))
    conn.commit()
    conn.close()


def get_info(user):
    """ pusha as informacoes de usuario """
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT pass, type from USER where user = '{user}'")
    print("SELECT pass, type from USER where user = '{0}'".format(user))
    info = [reg[0] for reg in cursor.fetchall()]
    conn.close()
    if len(info) == 0:
        return None
    else:
        return info[0]


auth = flask_httpauth.HTTPBasicAuth() 

app = Flask(__name__, static_url_path='')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?TX'


@app.route('/', methods=['GET', 'POST'])
@auth.login_required
def main():
    msg = ''
    p = 1
    challenges = get_quizes(auth.username())
    sent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if request.method == 'POST' and 'ID' in request.args:
        id = request.args.get('ID')
        quiz = get_quiz(id, auth.username())
        if len(quiz) == 0:
            msg = "Boa tentativa, mas não vai dar certo!"
            p = 2
            return render_template('index.html', username=auth.username(), challenges=challenges, p=p, msg=msg)

        quiz = quiz[0]
        if sent > quiz[2]:
            msg = "Sorry... Prazo expirado!"

        f = request.files['code']
        filename = f'./upload/{auth.username()}-{sent}.py'
        f.save(filename)
        with open(filename, 'r') as fp:
            answer = fp.read()

        #lamb = boto3.client('lambda')
        args = {"ndes": id, "code": answer, "args": eval(
            quiz[4]), "resp": eval(quiz[5]), "diag": eval(quiz[6])}

        #response = lamb.invoke(FunctionName="Teste", InvocationType='RequestResponse', Payload=json.dumps(args))
        #feedback = response['Payload'].read()
        #feedback = json.loads(feedback).replace('"','')
        feedback = lambda_handler(args, '')

        result = 'Erro'
        if len(feedback) == 0:
            feedback = 'Sem erros.'
            result = 'OK!'

        set_user_quiz(auth.username(), id, sent, feedback, result)

    if request.method == 'GET':
        if 'ID' in request.args:
            id = request.args.get('ID')
        else:
            id = 1

    if len(challenges) == 0:
        msg = "Ainda não há desafios! Volte mais tarde."
        p = 2
        return render_template('index.html', username=auth.username(), challenges=challenges, p=p, msg=msg)

    quiz = get_quiz(id, auth.username())

    if len(quiz) == 0:
        msg = "Oops... Desafio invalido!"
        p = 2
        return render_template('index.html', username=auth.username(), challenges=challenges, p=p, msg=msg)

    answers = get_user_quiz(auth.username(), id)

    return render_template('index.html', username=auth.username(), challenges=challenges, quiz=quiz[0], e=(sent > quiz[0][2]), answers=answers, p=p, msg=msg, expi=converte_data(quiz[0][2]))


@app.route('/pass', methods=['GET', 'POST'])
@auth.login_required
def change():
    if request.method == 'POST':
        velha = request.form['old']
        nova = request.form['new']
        repet = request.form['again']

        p = 1
        msg = ''
        if nova != repet:
            msg = 'As novas senhas nao batem'
            p = 3
        elif get_info(auth.username()) != hashlib.md5(velha.encode()).hexdigest():
            msg = 'A senha antiga nao confere'
            p = 3
        else:
            set_info(hashlib.md5(nova.encode()).hexdigest(), auth.username())
            msg = 'Senha alterada com sucesso'
            p = 3
    else:
        msg = ''
        p = 3

    return render_template('index.html', username=auth.username(), challenges=get_quizes(auth.username()), p=p, msg=msg)


@app.route('/logout')
def logout():
    return render_template('index.html', p=2, msg="Logout com sucesso"), 401


@auth.get_password
def get_password(username):
    return get_info(username)


@auth.hash_password
def hash_pw(password):
    return hashlib.md5(password.encode()).hexdigest()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
