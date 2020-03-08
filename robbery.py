import requests
import os
import re
import prettytable as pt
from bs4 import BeautifulSoup

#搶課機器人(博雅通識) : 網頁架構變動的情況下,程序可能失效。

#登錄
userid = 'xxxxx'
userpwd = 'xxxxx'

def login():    
  url = 'https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/bookmark.php'  
  params = {'id': userid,'password' : userpwd}
  res = requests.post(url , params)
  res.encoding = res.apparent_encoding
  session_id = re.findall('Add_Course00.cgi?.*' , res.text)[0][28:-3]
  return session_id
  

#選擇課程
def selectCourse(session_id , dept , grade , cge_cate , cge_subcate , course_id , course_cate , done):
  
  if course_id in done:
    return None
  data = {
    'session_id': session_id,
    'dept': dept, 
    'grade': grade, 
    'cge_cate': cge_cate,
    'cge_subcate': cge_subcate, 
    'course': course_id,
    '7304030_01': course_cate,
    'SelectTag': '1', 
  }
  text = requests.post(f'https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Add_Course01.cgi',data)
  text.encoding = text.apparent_encoding 
  return text

#課程搜尋
def searchCourse(session_id , dept , grade , cge_cate , cge_subcate , clist , others):
    page = 0  
    data = {
        'session_id' : session_id,
        'dept': dept,
        'grade': grade,
        'cge_cate': cge_cate,
        'cge_subcate': cge_subcate,
        'page':str(page)
    }
    text = requests.post(f'https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Add_Course01.cgi',data)
    text.encoding = text.apparent_encoding
    soup = BeautifulSoup(text.text , 'html.parser')
    try:
      totalPages = int(soup.find('form' , {'name':'NextForm'}).findAll('a')[-1].text.split(' ')[1])
    except:
      totalPages = 1

    for page in range(totalPages):
      text = requests.get(f'https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Add_Course01.cgi?session_id={session_id}&use_cge_new_cate=1&m=0&dept={dept}&grade={grade}&page={page+1}&cge_cate={cge_cate}&cge_subcate={cge_subcate}')
      text.encoding = text.apparent_encoding
      soup = BeautifulSoup(text.text , 'html.parser')
      textList = soup.find('form' , {'action':'Add_Course01.cgi'}).find('table').find('tr').findAll('tr')[1:]
      for text in textList:
        try:
          courseinfo = text.findAll('th')
          courseid = courseinfo[0].input.attrs['value']
          current = courseinfo[1].text
          remaining = courseinfo[2].text
          course = courseinfo[3].text
          teacher = courseinfo[4].text
          credit = courseinfo[5].text
          time = courseinfo[6].text
          classroom = courseinfo[7]
        except:
            continue
        if int(remaining) != 0:
          clist.append((course , courseid , current , remaining , credit , cge_subcate))
        else:
          others.append((course , courseid , current , remaining , credit , cge_subcate))

import time

if __name__ == '__main__':
  
  done = []  
  
  while(1):
    #session_id
    session_id = login()

    #通事課程參數
    grade = '1'
    dept = 'I001'
    cge_cate = '2'
    cge_subcate = ['0' , '1' , '2' , '3' , '4' , '5' , '6']
    course_cate = '3'

    #爬取所有博雅通識課程訊息
    clist = []
    others = []
    for subcate in cge_subcate:
      searchCourse(session_id  , dept , grade , cge_cate , subcate , clist , others)
      clist.sort(key = lambda x : int(x[3]))

    #建表整理
    tb = pt.PrettyTable()
    tb.field_names = ['剩餘名額' , '課程名稱' , '課程編號' , '目前選修人數' , '學分數' , '通識類別']
    for i in range(len(clist)):
      tb.add_row([clist[i][3] , clist[i][0] , clist[i][1] , clist[i][2] , clist[i][4] , clist[i][5]])
    print(tb)

    #鎖定課程
    tb2 = pt.PrettyTable()
    tb2.field_names = ['剩餘名額' , '課程名稱' , '課程編號' , '目前選修人數' , '學分數' , '通識類別']
    focus = ['7405006_02' , '7403003_01']
    for i in range(len(clist)):
      if clist[i][1] in focus:
        tb2.add_row([clist[i][3] , clist[i][0] , clist[i][1] , clist[i][2] , clist[i][4] , clist[i][5]])
        text = selectCourse(session_id , dept , grade , cge_cate , clist[i][5] , clist[i][1] , course_cate , done)
        if text != None:
          #鎖定課程有缺額,程序提交表單選取
          done.append(clist[i][1])
          print('+---------------------+')
          print(f'提交表單選擇通識{clist[i][0]} , 系統回覆如下:')
          print(text.text)
          print('+---------------------+')
      
    for i in range(len(others)):
      if others[i][1] in focus:
        tb2.add_row([others[i][3] , others[i][0] , others[i][1] , others[i][2] , others[i][4] , others[i][5]])
    
    #關注列表
    print('關注列表')
    print(tb2)

    #以提交表單選課
    print('已提交表單選課 , 請至選課系統確認')
    for i in range(len(done)):
      print(done[i])

  
