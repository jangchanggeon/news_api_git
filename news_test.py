import schedule
import time
import requests
import app

def news_call():
    url = "http://192.168.219.100:35502/db_write"
    response = requests.get(url= url)
    response.content
    print(response)
    
schedule.every(24).hours.do(news_call)#시간 당 호출로 바꿔야함 
    
while True:
    schedule.run_pending()
    time.sleep(1)