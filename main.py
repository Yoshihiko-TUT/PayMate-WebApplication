from flask import Flask, render_template, request, session, redirect, url_for
from flask_bcrypt import Bcrypt
import mysql.connector
from pay_mate import PayMate

app = Flask(__name__)
bcrypt = Bcrypt()
app.secret_key = 'g09'

# MySQLデータベース接続の設定
db = mysql.connector.connect(
    host='localhost',
    user='g09',  # MySQLユーザー名
    password='1234',  # パスワード
    database='userdb',  # データベース名
    charset="utf8mb4"  # 文字エンコーディングを指定
)

# 最初はlogin.htmlから始まる
@app.route('/')
def login():
    return render_template('login.html')

# ログインの認証とページ移動
@app.route('/login', methods=['POST'])
def authenticate_user():
    email = request.form['email']
    password = request.form['password']

    cursor = db.cursor()
    cursor.execute("SELECT email, password FROM users WHERE email = %s", (email,))

    user = cursor.fetchone()  # メールアドレスに対応するユーザーを取得

    if user and bcrypt.check_password_hash(user[1], password):  # パスワードのハッシュ値を用いて認証
        session['user_id'] = email  # セッションを使用してユーザーを識別

        return calculate(email)
    else:   # ログインが失敗した場合の処理
        return render_template('login.html', error='ログインが失敗しました')
    
def calculate(email):
    pm = PayMate(email)

    cursor = db.cursor(dictionary=True)  # 結果を辞書形式で取得

    query = "SELECT job_name, hourly_wage FROM jobs"
    cursor.execute(query)

    result = cursor.fetchall()

    salary = {row['job_name']: row['hourly_wage'] for row in result}

    result = pm.calculate(salary)
    return render_template('result.html', result=result)  

# 新規登録ボタンを押したときにregister.htmlに移動
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

# 登録ボタンが押されたときにユーザー情報をDBに追加
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    hashed_password = bcrypt.generate_password_hash(request.form['password'])   # パスワードはハッシュで暗号化

    cursor = db.cursor()

    # ユーザーをデータベースに挿入
    cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
    db.commit()

    cursor.close()

    return render_template('first_setting.html')  # 説明ページに移動

# 新規登録ボタンを押したときにadd_job.htmlに移動
@app.route('/add_job', methods=['GET'])
def job_page():
    return render_template('add_job.html')

# 登録ボタンが押されたときにユーザー情報をDBに追加
@app.route('/add_job', methods=['POST'])
def add_job():
    job_name = request.form['job_name']
    hourly_wage = request.form['hourly_wage']
    
    cursor = db.cursor()

    # ユーザーをデータベースに挿入
    cursor.execute("INSERT INTO jobs (job_name, hourly_wage) VALUES (%s, %s)", (job_name, hourly_wage))
    db.commit()

    cursor.close()

    return calculate(session['user_id'])

if __name__ == '__main__':
    app.debug = True
    app.run()

# 下記URLをブラウザに打ち込むとページが開く
# http://127.0.0.1:5000/
