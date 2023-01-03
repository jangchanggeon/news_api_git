#파이썬 기본제공 모듈
from datetime import datetime, timedelta
import os
import requests
import time
from turtle import color
import six
from bs4 import BeautifulSoup as bs
from flask import Flask, render_template, request
import schedule
from unittest import result
import pymysql
# 그 외 모듈
from bs4 import BeautifulSoup as bs
from newsapi import NewsApiClient
from google.cloud import language_v1


app = Flask(__name__)
# Init news api, news api key import 

API_KEY = '13787d35607c4241bb7e28d822a5d01a'
NEWS_LIST = "bloomberg.com,bbcnews.com,investing.com/news/,Finance.google.com,marketwatch.com,eia.doe.gov"

newsapi = NewsApiClient(api_key=API_KEY)

# def 
def convert_datetime_gmt9(gmt0_str):
    gmt0_datetime = datetime.strptime(gmt0_str, '%Y-%m-%dT%H:%M:%SZ')
    gmt9_datetime = gmt0_datetime + timedelta(hours=9)
    gmt9_str = gmt9_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    return gmt9_str
    
#sql insert 함수
def sql_insert(keyword,score_sum,middle_article):
    conn = pymysql.connect(host='115.22.125.154',
                        user='root',
                        password='142536nM@@',
                        db='smart_factory',
                        charset='utf8',
                        port=3307)
    
    # if keyword!="":    
    if keyword != "":
        sql = "INSERT INTO news_api (title,score_sum,searchin,source,newsdate) VALUES (%s, %s,%s,%s,%s)"
        #중복값 제거
        DELETE_TITLE = "DELETE a FROM news_api a, news_api b where a.index_auto < b.index_auto AND a.title = b.title;"

        # mid_newsdate = middle_article['fetch_datetime'].replace("T"," ")
        # mid_newsdate = mid_newsdate.replace("Z","")
        #SET COUNT를 0부터 시작해서 1씩 증가한뒤 업데이트
        with conn:
                    with conn.cursor() as cur:
                        
                        cur.execute(sql, (middle_article['title'],middle_article['url'],keyword,middle_article['score'],middle_article['fetch_datetime']))
                        cur.execute(DELETE_TITLE)
                        print("\nSQL = "+sql % (middle_article['title'],score_sum,keyword,middle_article['score'],middle_article['fetch_datetime']))
                        conn.commit()
                        return True

            
    return False

#google nlp analyze 함수
def analyze_sentiment(title):
    #google api 인증키 json 파일 path잡는 곳
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:/Users/ghkdw/Desktop/develope/Flask_news/googleapikey.json"
    # language_v1.LanguageServiceClient()을 원래는 할때마다 호출해줘야하는데 변수에 담아서 필요할때만 호출하기위함
    client = language_v1.LanguageServiceClient()
    #.decode는 인코딩과정에서 라틴어를 사용하는 것에 방지하기 위함
    if isinstance(title, six.binary_type):
        title = title.encode('utf-8').decode('iso-8859-1')
    type_ = language_v1.Document.Type.PLAIN_TEXT
    language ="en"
    # content부분에  newsapi에서 title부분을 넣어줘서 list형 dict방식으로 변수에 담아준다.
    document = {"type_": type_, "content": title}
    #분석의 결과값을 저장하는 response
    response = client.analyze_sentiment(request={"document": document})
    sentiment = response.document_sentiment
    return sentiment.score, sentiment.magnitude 

def get_emotion(score):
    if score > 0:
            sentiment =  "긍정"
            
    elif score == 0:
            sentiment = "중립"
    else:
            sentiment ="부정"
    return sentiment



def autocall_write(keyword, middle_article,score_sum,avg_score_title,avg_magnitude_title,sentiment_avg):
        now = datetime.now()
        f_autocall = open("C:/새 폴더/autocall_{0}.txt".format(now.strftime("%y%m%d")),'a',encoding='utf-8')
        f_autocall.write(now.strftime('%Y-%m-%d %H:%M:%S')+"키워드 :"+keyword+"\n"+"기사 개수 :"+str(len(middle_article))+"\n"+"Score :"+str(score_sum)+"\n"+"점수 평균:"+str(avg_score_title)+"\n"+"magnitude :"+str(avg_magnitude_title)+"\n"+"감정 :"+ str(sentiment_avg)+"\n\n\n")
        f_autocall.close()

# keyword에 관한 article 기본 형 
def get_result(keyword):
    d_today = datetime.today()

    articles = newsapi.get_everything(qintitle=keyword,
                                      domains=NEWS_LIST,
                                      from_param = d_today - timedelta(days=5),
                                      to = d_today,
                                      language='en',
                                      sort_by="publishedAt",
                                      page_size = 100)['articles']
    final_articles = []
    score_sum = 0
    magnitude_sum = 0
    
    for article in articles:
        title_score = ''
        title_magnitude = ''
        title = article['title']
        title_score, title_magnitude =analyze_sentiment(title)
        middle_article = article
        middle_article['score'] = round(title_score,4)  #article_copy를 result값에 넣기위해 만든 것
        middle_article['magnitude'] = round(title_magnitude,4) #4째 자리 반올림
        score_sum += title_score
        score_sum = round(score_sum,4)
        magnitude_sum += title_magnitude
        middle_article['sentiment'] = get_emotion(title_score)
        middle_article['publishedAt_gmt9'] = convert_datetime_gmt9(article['publishedAt'])
        middle_article['fetch_datetime'] = datetime.now()
        final_articles.append(middle_article)
        
        if len(final_articles) >= 10:
            break
        
        if sql_insert(keyword,score_sum,middle_article):
            print("\nSQL-insert-OKAY---------------------------------------------------\n") 
        
        else:
            keyword ==""
            keyword==""
            print("\nFAIL-------------------------------------\n")
    return final_articles, score_sum, magnitude_sum

def summarize_news_score(score_sum,magnitude_sum,middle_article):
    avg_score_title = round(score_sum/len(middle_article),4)
    avg_magnitude_title = round(magnitude_sum/len(middle_article),4)
    sentiment_avg = get_emotion(avg_score_title)#score, magnitude를 한꺼번에 넣을려면 append를 써야하나?
    return score_sum,avg_score_title,sentiment_avg,avg_magnitude_title
    
@app.route("/", methods=['GET', 'POST'])

def home():           
    keyword = ""
    
    if "keyword" in request.form:
        keyword =request.form["keyword"]    
    middle_article,score_sum,magnitude_sum = get_result(keyword) 
    
    if len((middle_article)) > 0:
        score_sum,avg_score_title,avg_magnitude_title,sentiment_avg =summarize_news_score(score_sum,magnitude_sum,middle_article)
        return render_template("home.html", all_articles = middle_article, result = keyword, \
         score_sum = avg_score_title,magnitude_sum =avg_magnitude_title, sentiment = sentiment_avg)
    else:
        avg_score_title = 0
        avg_magnitude_title = 0
        return render_template("fail.html")
    
    
    
@app.route("/db_write", methods=['GET', 'POST'])

def home_db():          
    keyword_list = ['gold','oil']
    for keyword in keyword_list:
            
        middle_article,score_sum,magnitude_sum = get_result(keyword)
        a="OKAY"
        if len((middle_article)) > 0:
            score_sum,avg_score_title,avg_magnitude_title,sentiment_avg =summarize_news_score(score_sum,magnitude_sum,middle_article)
        #   print(keyword, len(middle_article), score_sum, avg_score_title, avg_magnitude_title, sentiment_avg)
            
            autocall_write(keyword, middle_article,score_sum,avg_score_title,avg_magnitude_title,sentiment_avg)
            
            

        else:
            avg_score_title = 0
            avg_magnitude_title = 0
            a="NO"

    return a
if __name__ == "__main__":
    app.run(debug = True, port=35502, host='0.0.0.0')