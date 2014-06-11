#coding:utf-8

import MySQLdb
from flask import Flask, g, request,make_response
import urllib
import requests
import datetime
import json
import hashlib
import xml.etree.ElementTree as ET
import time
from bs4 import BeautifulSoup
import re
import random
import pickle

app = Flask(__name__)
app.config.from_pyfile('config.py')
apikey = app.config['APIKEY']
text_tpl = app.config['TEXT_TEMPLATE'] 
pictext_tpl = app.config['PICTEXT_TEMPLATE']
item_tpl = app.config['ARTICLE_ITEM']
music_tpl = app.config['MUSIC_TEMPLATE']

from sae.const import (MYSQL_HOST, MYSQL_HOST_S,
    MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DB
)

@app.before_request
def before_request():
    g.db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS,
                           MYSQL_DB, port=int(MYSQL_PORT))

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'): g.db.close()

@app.route('/')
def hello():
    return "Hello, world! - Flask"


@app.route('/wechat',methods = ['GET','POST'])
def wechat():
    if request.method == 'GET':
        token = '112233'
        query = request.args
        signature = query.get('signature','')
        timestamp = query.get('timestamp','')
        nonce = query.get('nonce','')
        echostr = query.get('echostr','')

        s = [timestamp,nonce,token]
        s.sort()
        s = ''.join(s)
        return make_response(echostr)
    else:
        xml_recv = ET.fromstring(request.data)
        ToUserName = xml_recv.find('ToUserName').text
        FromUserName = xml_recv.find('FromUserName').text
        Content = xml_recv.find('Content').text

        if Content == 'hot':
            articles = get_nowplaying_movies()
            result = pictext_tpl % (FromUserName, ToUserName, str(int(time.time())), 7, articles) 
        elif Content.startswith('music'):
            song = get_random_song()
            params = (FromUserName, ToUserName, str(int(time.time()))) + song
            result = music_tpl % params
        elif Content.startswith('m'):
            articles = get_movie_info(Content[1:])
            result = pictext_tpl % (FromUserName, ToUserName, str(int(time.time())), 1, articles) 
        elif Content.startswith('b'):
            articles = get_book_info(Content[1:])
            result = pictext_tpl % (FromUserName, ToUserName, str(int(time.time())), 1, articles) 
        elif Content.startswith('w'):
            pass
        else:
            talk_url = 'http://rmbz.net/Api/AiTalk.aspx?key=rmbznet&word=' + Content
            r = requests.get(talk_url)
            word = json.loads(r.content).get('content')
            result = text_tpl % (FromUserName, ToUserName, str(int(time.time())), word)

        response = make_response(result)
        response.content_type = 'application/xml'
        return response


@app.route('/weather')
def get_weather_info():
    url = 'http://m.weather.com.cn/atad/101190401.html'
    weeks = [u'一',u'二',u'三',u'四',u'五',u'六',u'日']
    today = datetime.date.today().weekday()

    r = requests.get(url)
    content = r.content

    weather_data = json.loads(content)
    weather_info = weather_data.get('weatherinfo')

    weather_list = []
    for i in range(6):
        temperature = weather_info.get('temp'+str(i+1))
        if i==0:
            weekday = u'今天'
        else:
            if today+i > 6:
                weekday = u'星期' + weeks[(today+i)%6]
            else:
                weekday = u'星期' + weeks[today+i]
        weather_list.append(weekday+' '+temperature+'</br>')

    return ''.join(weather_list)

@app.route('/hosts')
def hosts():
    lines = []
    with open('static/hosts') as f:
        for line in f:
            line = line + '<br>'
            lines.append(line)
    return ''.join(lines)

@app.route('/test')
def test():
    return 'test'

def get_random_song():
    with open('static/songs.pickle') as f:
        songs = pickle.load(f)
        random.seed(time.time())
        ran_num = random.randrange(len(songs))
        song = songs[ran_num]

    song_name = song.get('name')
    singer = song.get('artists')[0].get('name')
    mp3_url = song.get('mp3Url')

    return (song_name,singer,mp3_url,mp3_url)

def get_book_info(bookname,count=1):
    params = (bookname,count,apikey)    
    url = 'https://api.douban.com/v2/book/search?q=%s&count=%s&apikey=%s' % params
    content = requests.get(url).content
    json_data = json.loads(content)
    books = json_data.get('books')

    items = []
    for book in books:
        book_title = book.get('title')
        author = ','.join(book.get('author'))
        img_url = book.get('images').get('large')
        average = book.get('rating').get('average')
        summary = book.get('summary')
        book_url = book.get('alt')
        
        title = u'%s\t%s分\n%s' % (book_title,average,author)
        item = item_tpl % (title,summary,img_url,book_url)
        items.append(item)
    return ''.join(items)

def get_movie_info(moviename,count=1):
    params = (moviename,count,apikey)
    url = 'https://api.douban.com/v2/movie/search?q=%s&count=%s&apikey=%s' % params
    content = requests.get(url).content
    json_data = json.loads(content)
    movies = json_data.get('subjects')

    items = []
    for movie in movies:
        movie_title = movie.get('title')
        img_url = movie.get('images').get('large')
        average = movie.get('rating').get('average')
        movie_id = movie.get('id')
        alt = movie.get('alt')
        r = requests.get('http://api.douban.com/v2/movie/'+movie_id)
        spec = json.loads(r.content)
        summary = spec.get('summary')
        director = ','.join(spec.get('attrs').get('director'))
        director = re.sub('[a-zA-Z\s]*','',director)
        cast = ','.join(spec.get('attrs').get('cast')[:2])
        cast = re.sub('[a-zA-Z\s]*','',cast)
        title = u'%s\t%s分\n导演\t%s\n主演\t%s' % (movie_title, average,director,cast)
        item = item_tpl % (title,summary,img_url,alt)
        items.append(item)
    return ''.join(items)

def get_nowplaying_movies():
    url = 'http://movie.douban.com/nowplaying/suzhou/'
    content = requests.get(url).content

    soup = BeautifulSoup(content)
    ul = soup.find('div',id='nowplaying').find('ul',class_='lists')
    lis = ul.find_all('li',class_=re.compile('.*item.*'))

    movies = []
    for li in lis:
        movie = {}
        movie['id'] = li.get('id')
        movie['average'] = li.get('data-score')
        movie['title'] = li.get('data-title')
        movies.append(movie) 
    movies.sort(cmp=cmp)

    items = []
    for movie in movies[:7]:
        url = 'http://api.douban.com/v2/movie/%s?apikey=%s' % (movie['id'],apikey)
        content = requests.get(url).content
        movie_data = json.loads(content)
        director = ','.join(movie_data.get('attrs').get('director'))
        director = re.sub('[a-zA-Z\s]*','',director)
        cast = ','.join(movie_data.get('attrs').get('cast')[0:5])
        cast = re.sub('[a-zA-z\s]*','',cast)
        title = u'%s\t%s分\n导演\t%s\n主演\t%s' % (movie['title'],movie['average'],director,cast)
        summary = movie_data.get('summary')
        img_url = movie_data.get('image').replace('ipst','lpst')
        alt = 'http://movie.douban.com/subject/%s/' % movie['id']
        item = item_tpl % (title,summary,img_url,alt)
        items.append(item)
    return ''.join(items)

def cmp(a,b):
    if float(a['average']) < float(b['average']):
        return 1
    else:
        return -1
