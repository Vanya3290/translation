from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from deep_translator import GoogleTranslator
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') 

app.config['MYSQL_HOST'] = os.getenv('db_host') 
app.config['MYSQL_USER'] = os.getenv('db_user') 
app.config['MYSQL_PASSWORD'] = os.getenv('db_password') 
app.config['MYSQL_DB'] = os.getenv('db_database') 

mysql = MySQL(app)


login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM site_users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    if user is None:
        return None

    user_obj = User()
    user_obj.id = user_id
    return user_obj

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM site_users WHERE user_login = %s AND user_pass = %s", (username, password,))
        user = cur.fetchone()
        if user:
            user_obj = User()
            user_obj.id = user[0]  # Припустимо, що id користувача знаходиться в першому стовпці
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/translate', methods=['GET', 'POST'])
@login_required
def translate():
    translated_text = ""
    original_text = ""
    selected_language = "en"  # За замовчуванням англійська
    supported_languages  = GoogleTranslator().get_supported_languages(as_dict=True)

    # Отримання історії перекладів з бази даних
    cur = mysql.connection.cursor()
    cur.execute("SELECT original_text, translated_text, target_language, translation_time FROM translation_history WHERE user_id = %s ORDER BY translation_time DESC", (current_user.get_id(),))
    history = cur.fetchall()

    if request.method == 'POST':
        original_text = request.form.get('text')
        selected_language = request.form.get('language')
        translator = GoogleTranslator(source='auto', target=selected_language)
        translated_text = translator.translate(text=original_text)

        # Запис нового перекладу в історію
        cur.execute("INSERT INTO translation_history(user_id, original_text, translated_text, target_language) VALUES(%s, %s, %s, %s)", 
                    (current_user.get_id(), original_text, translated_text, selected_language))
        mysql.connection.commit()

        # Оновлення історії після додавання нового перекладу
        cur.execute("SELECT original_text, translated_text, target_language, translation_time FROM translation_history WHERE user_id = %s ORDER BY translation_time DESC", (current_user.get_id(),))
        history = cur.fetchall()
        
    cur.close()

    return render_template('translate.html', 
                           original_text=original_text, 
                           translated_text=translated_text, 
                           selected_language=selected_language, 
                           supported_languages=supported_languages,
                           history=history)




if __name__ == '__main__':
    app.run(debug=True,  host='0.0.0.0', port=5000)

