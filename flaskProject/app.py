import os
from io import StringIO

import MySQLdb
from flask import Flask, flash, send_file, render_template, session, redirect, request, url_for
from flask_mysqldb import MySQL
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads/"
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = ['txt', 'pdf']
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ALLOWED_EXTENSIONS"] = ["TXT", "PDF"]
app.secret_key = "123456789"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "gwynedd123"
app.config["MYSQL_DB"] = "PDFApp"

db = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def default():  # put application's code here
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM user WHERE username=%s AND password=%s", (username, password))
            info = cursor.fetchone()
            if info is not None:
                if info['username'] == username and info['password'] == password:
                    flash("Login Successful", info)
                    session['loginsuccess'] = True
                    return redirect(url_for('upload'))
            else:
                flash("Incorrect username or password")
                return redirect(url_for('default'))

    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if "one" in request.form and "two" in request.form:
            username = request.form['one']
            password = request.form['two']
            cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("INSERT INTO user (username,password) VALUES (%s,%s)", (username, password))
            db.connection.commit()
            flash("User created successfully")
            return redirect(url_for('default'))
    return render_template("register.html")


def allowed_file(filename):
    return filename.split('.')[-1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if session['loginsuccess'] == True:
        if request.method == 'POST':
            if request.files:

                file = request.files["file"]
                file.filename = "input.pdf"
                if file.filename == "":
                    print("Image must have a filename")
                    return redirect(request.url)

                if not allowed_file(file.filename):
                    print("Image extension not allowed")
                    return redirect(request.url)

                else:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                    print("File saved!")

                    return redirect(url_for('download'))
        return render_template("upload.html")


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if 'ad' in request.form:
            username = request.form['ad']
            crsr = db.connection.cursor(MySQLdb.cursors.DictCursor)
            crsr.execute("DELETE FROM user WHERE username=%s", (username,))
            db.connection.commit()
            flash("User deleted successfully")
            return redirect(url_for('default'))
    return render_template("admin.html")


def listToString(s):
    str1 = ""

    for ele in s:
        str1 += ele

    return str1


@app.route('/download', methods=['GET', 'POST'])
def download():
    output_string = StringIO()
    with open('uploads\input.pdf', 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
        with open(r"C:\Users\Berk\PycharmProjects\flaskProject\uploads\output.txt", "w", encoding="utf-8") as f:
            f.write(output_string.getvalue())

        mylines = []
        summary = []
        ozet = "ÖZET"
        giris = "GİRİŞ"
        dr="Dr"
        end = 0
        count = 0


        with open("uploads\output.txt", encoding="utf-8") as myfile:
            for line in myfile:
                if ozet in line:
                    count += 1
                elif giris in line:
                    end += 1
                if end == 2: break
                if count == 2:
                    mylines.append(line.replace("\n", " "))
                if dr in line:
                    mylines.append(line.replace("\n", " "))
        with open("ozet.txt", "w", encoding="utf-8") as file:
            for element in mylines:
                file.write(element + "\n")

    return render_template("download.html")


@app.route('/download_file')
def download_file():
    p = "ozet.txt"
    return send_file(p, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
