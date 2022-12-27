from flask import Flask, render_template, request
import sqlite3
import json
import pymysql
 
app = Flask(__name__)
 
 
@app.route("/data.json")

def data():
    connection = pymysql.connect(host='115.22.125.154',
                        user='root',
                        password='142536nM@@',
                        db='smart_factory',
                        charset='utf8',
                        port=3307)
    cursor = connection.cursor()
    cursor.execute("SELECT 1000*`real_time`, `score_sum` from news_api")
    results = cursor.fetchall()
    print("-----------1",results)
    return json.dumps(results)

@app.route("/graph")

def graph():
    return render_template('graph.html')
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7900)