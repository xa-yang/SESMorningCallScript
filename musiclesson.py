import sqlite3
import urllib.request
import smtplib
import urllib.parse
import time
import re
from email.mime.text import MIMEText
from email.utils import formataddr
from http import cookiejar
from bs4 import BeautifulSoup

def _init_():
    global opener
    global GMT_date
    global head
    login_url = 'https://dashboard.stedwardsoxford.org/login/login.aspx?prelogin=https%3a%2f%2fdashboard.stedwardsoxford.org%2fpupil-dashboard&kr=ActiveDirectoryKeyRing'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
    head = {'User-Agent': user_agent}
    login_data = {}
    login_data['username'] = ''
    login_data['password'] = ''
    loginpostdata = urllib.parse.urlencode(login_data).encode('utf-8')
    cookie = cookiejar.CookieJar()
    cookie_support = urllib.request.HTTPCookieProcessor(cookie)
    opener = urllib.request.build_opener(cookie_support)
    req_1 = urllib.request.Request(url=login_url, data=loginpostdata, headers=head)

    class_date = time.gmtime(time.time())
    GMT_date = time.strftime("%Y-%m-%d %a %H:%M:%S", time.gmtime(time.time())) + ' GMT'

    return head

def get_music(head, name):
    music_url = 'https://dashboard.stedwardsoxford.org/music-timetables'
    req_2 = urllib.request.Request(url=music_url, headers=head)
    music_response = opener.open(req_2)
    html = music_response.read().decode('utf-8')

    target_music = BeautifulSoup(html, 'lxml')
    music_info = target_music.tbody
    music_info = music_info.find_all('td')
    for i in range(0, len(music_info)):
        music_info[i] = str(music_info[i]).split('>')[1].split('<')[0]

    all_info = []
    del music_info[0:6]
    while len(music_info) > 5:
        individual_info = music_info[0:6]
        del music_info[0:6]
        individual_info[0] = re.sub(",", "", individual_info[0])
        all_info.append(individual_info)

    for each in all_info:
        each[0] = each[0].split(' ')[0]
        #print(each[0])
        #x[0] = x[0].split(' ')[1] + ' ' + x[0].split(' ')[0]
        #print(lastname)
        #print(each[0])

        if each[0] == name:
            music_lesson = '  '.join(each)
            return music_lesson
        else:
            #music_lesson = 'No music lessons.'
            #return music_lesson
            pass

#get_music(head = _init_(), name='Shukawa')

def db():

    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    for row in c.execute('SELECT name,guid,email,mailing FROM userdata_user'):
        mailing = row[3]

        if mailing == '1':
            print(row[0])
            user_name_lastname = row[0].split(' ')[1].capitalize()

            music_lesson = get_music(_init_(), user_name_lastname)
            print(music_lesson)

        else:
            pass
db()
