import os

import pymysql
from flask import Flask

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "esempio")


@app.route("/")
def home():
    return f"Ciao! DB_HOST={DB_HOST}, DB_NAME={DB_NAME}"


@app.route("/db")
def db_check():
    connection = pymysql.connect(
        host=DB_HOST,
        user="root",
        password=DB_PASSWORD,
        database=DB_NAME,
    )
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
    connection.close()
    return f"Connessione al database riuscita: {result}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)