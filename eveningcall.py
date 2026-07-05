import smtplib
import sqlite3
import time
import urllib.parse
from email.mime.text import MIMEText
from email.utils import formataddr
from http import cookiejar

from bs4 import BeautifulSoup

login_url = 'https://dashboard.stedwardsoxford.org/login/login.aspx?prelogin=https%3a%2f%2fdashboard.stedwardsoxford.org%2fpupil-dashboard&kr=ActiveDirectoryKeyRing'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
head = {'User-Agent': user_agent}
login_data = {}
login_data['username'] = ''
login_data['password'] = ''
loginpostdata = urllib.parse.urlencode(login_data).encode('utf-8')
cookie = cookiejar.CookieJar()
cookie_support = urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(cookie_support)
req_1 = urllib.request.Request(url=login_url, data=loginpostdata, headers=head)

data_url = 'https://dashboard.stedwardsoxford.org/pupil-dashboard'
req_2 = urllib.request.Request(url=data_url, headers=head)
response_1 = opener.open(req_1)
response_2 = opener.open(req_2)
html = response_1.read().decode('utf-8')

class_date = time.gmtime(time.time())
GMT_date = time.strftime("%Y-%m-%d %a %H:%M:%S", time.gmtime(time.time())) + ' GMT'

#log = open('evening.log', 'w')
log = open('/home/ubuntu/SESMorningCallScript/evening.log', "w")

log.write(GMT_date + '\n')

#conn = sqlite3.connect('db.sqlite3')
conn = sqlite3.connect('/home/ubuntu/django/SESMorningCallServer/db.sqlite3')

c = conn.cursor()
for row in c.execute('SELECT name,guid,email,eveningmailing FROM userdata_user'):
    mailing = row[3]
    if mailing == '1':
        user_name = row[0].capitalize()
        user_url = 'https://dashboard.stedwardsoxford.org/profile?guid=' + row[1]
        user_email = row[2]
        log.write(user_name + ',' + user_email + '\n')
        req = urllib.request.Request(url=user_url, headers=head)
        response = opener.open(req)
        html_1 = response.read()
        class_date = time.gmtime(time.time())
        if class_date.tm_wday != 5:
            target = BeautifulSoup(html_1, 'lxml')
            lesson_all = target.find(class_='ff-timetable-day ff-timetable-today')
            lesson_all = lesson_all.next_sibling.next_sibling
            lesson_list = []
            lesson_information = []
            lesson = lesson_all.find_all(class_='ff-timetable-lesson-subject')
            for i in range(0, len(lesson)):
                lesson[i] = str(lesson[i])
                lesson_list.append(lesson[i].split('>')[1].split('<')[0])

            l_time = []
            lesson_time = lesson_all.find_all(class_='ff-timetable-lesson-info')
            for i in range(0, len(lesson_time)):
                lesson_time[i] = str(lesson_time[i]).split('"')[3].split(' in')[0]
                l_time.append(lesson_time[i])

            for i in range(0, len(l_time) - 1):
                if l_time[i] == l_time[i + 1]:
                    if lesson_list[i] == lesson_list[i + 1]:
                        lesson_list.pop(i + 1)
                    else:
                        lesson_list[i] = lesson_list[i] + ' / ' + lesson_list[i + 1]
                        lesson_list.pop(i + 1)

            if lesson_all.find_all('strong'):
                lesson_list = lesson_all.find_all('strong')
                for each in lesson_list:
                    each = str(each).split('>')[1].split('<')[0]
                    lesson_information.append(each)
            else:
                lesson_teacher = lesson_all.find_all(class_='ff-timetavble-lesson-teacher')
                # lesson_teacher = lesson_all.find_all('strong')
                if len(lesson_teacher) >= len(lesson_list):
                    for i in range(0, len(lesson_list)):
                        match = lesson_teacher[0].previous_sibling.previous_sibling
                        match = str(match)
                        match = match.split('>')[1].split('<')[0]
                        name = lesson_teacher[0]
                        name = str(name).split('>')[1].split('<')[0]
                        if lesson_list[i] == 'IB meeting':
                            lesson_info = 'IB Meeting'
                            lesson_information.append(lesson_info)
                            lesson_teacher.remove(lesson_teacher[0])
                            lesson_teacher.remove(lesson_teacher[0])
                        else:
                            if lesson_list[i] == match:
                                lesson_info = lesson_list[i] + '       ' + name
                                lesson_information.append(lesson_info)
                                lesson_teacher.remove(lesson_teacher[0])
                            else:
                                lesson_info = lesson_list[i]
                                lesson_information.append(lesson_info)
                                pass
                else:
                    lesson_teacher.insert(len(lesson_teacher), 'a><')
                    for i in range(0, len(lesson_list)):
                        try:
                            match = lesson_teacher[0].previous_sibling.previous_sibling
                            match = str(match)
                            match = match.split('>')[1].split('<')[0]
                        except AttributeError:
                            match = ''
                        name = lesson_teacher[0]
                        name = str(name).split('>')[1].split('<')[0]
                        if lesson_list[i] == 'IB meeting':
                            lesson_info = 'IB Meeting'
                            lesson_information.append(lesson_info)
                            lesson_teacher.remove(lesson_teacher[0])
                            lesson_teacher.remove(lesson_teacher[0])
                        else:
                            if lesson_list[i] == match:
                                lesson_info = lesson_list[i] + '       ' + name
                                lesson_information.append(lesson_info)
                                lesson_teacher.remove(lesson_teacher[0])
                            else:
                                lesson_info = lesson_list[i]
                                lesson_information.append(lesson_info)
                                pass

            free = []
            l_time = set(l_time)
            if class_date.tm_wday % 2 == 0:
                time_l = ['08:30 - 09:25', '09:30 - 10:25', '11:00 - 11:55', '12:00 - 12:55']
                if len(time_l) == len(l_time):
                    pass
                else:
                    for t in range(0, len(time_l)):
                        if time_l[t] not in l_time:
                            lesson_information.insert(t, 'STUDY PERIOD!!!!!')
                lesson_text = '\n'.join(str(x) for x in lesson_information)

            else:
                time_l = ['08:30 - 09:25', '09:30 - 10:25', '11:00 - 11:55', '12:00 - 12:55', '14:30 - 15:25',
                          '15:30 - 16:25']
                if len(time_l) == len(l_time):
                    pass
                else:
                    for t in range(0, len(time_l)):
                        if time_l[t] not in l_time:
                            lesson_information.insert(t, 'STUDY PERIOD!!!!!')
                lesson_text = '\n'.join(str(x) for x in lesson_information)

        else:
            lesson_text = 'No lessons tommorow.'

        GMT_date = time.strftime("%Y-%m-%d %a %H:%M:%S", time.gmtime(time.time())) + ' GMT'

        try:
            text = GMT_date + '\n' + '' + '\n' + "Tomorrow's lessons: " + '\n' + lesson_text + '\n' + '' + '\n' + '' + '\n' + 'Click the link below to unsubscribe or resubscribe' + '\n' + 'http://sesmorningcall.co.uk/subscription/?email=' + user_email + '&guid=' + \
                   row[1] + '&type=2' + '\n' + 'Made by Gandy'
        except NameError:
            text = GMT_date + '\n' + '' + '\n' + 'Invalid username/password for Dashbaord.'

        log.write(text + '\n')

        my_sender = 'sesmorningcall@outlook.com'
        my_pass = 'WorldtradeGandy!'

        my_user = user_email

        # ret = True
        def mail():
            ret = True
            try:
                msg = MIMEText(text, 'plain')
                msg['From'] = formataddr(['SES-Evening Call', my_sender])
                msg['To'] = formataddr([user_name, my_user])
                msg['Subject'] = 'Good evening, ' + user_name

                server = smtplib.SMTP('smtp.office365.com', 587)
                server.ehlo()
                server.starttls()
                server.login(my_sender, my_pass)
                server.sendmail(my_sender, my_user, msg.as_string())
                server.quit()
            except Exception:
                ret = False
            return ret

        ret = mail()
        if ret:
            log.write('Successfully sent' + '\n' + '')
            time.sleep(60)
            print('s')
        else:
            log.write('Error' + '\n' + '')
            print('x')
    else:
        pass
log.close()
