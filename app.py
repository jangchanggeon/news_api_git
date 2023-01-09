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
    cursor.execute("SELECT 1*`index_auto`,`score` from news_api")
    # float(cursor.execute("SELECT `score_sum` FROM `news_api`"))
    results = cursor.fetchall()
    results_fix = []
    for i in range(0,len(results)):
        results_fix.append(tuple([results[i][0],float(results[i][1])]))
        
    print("-----------1",tuple(results_fix))
    return json.dumps(tuple(results_fix))

@app.route("/graph")

def graph():
    return render_template('graph.html')
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7900)