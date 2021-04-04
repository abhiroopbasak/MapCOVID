from django.http import HttpResponse
from django.shortcuts import render
import numpy as np
import face_recognition as fr
import cv2
import time
import os
from pymongo import MongoClient
import csv
import datetime
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import date
import calendar
import matplotlib.pyplot as plt
import seaborn as sn
from pymongo import MongoClient
import requests


def index(request):
  
  return render(request,"index.html")



def takepic(name):
    cam = cv2.VideoCapture(0)

    cv2.namedWindow("Make Profile Picture")

    img_counter = 0

    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow("profile", frame)

        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            cam.release()
            cv2.destroyAllWindows()
            return 0
        elif k%256 == 32:
            # SPACE pressed
            img_name = "media/profile_{}.png".format(name)
            cv2.imwrite(img_name, frame)
            cam.release()
            cv2.destroyAllWindows()
            return img_name




def face_auth(pic):
    corr=0
    video_capture = cv2.VideoCapture(0)

    my_image = fr.load_image_file(pic)
    my_face_encoding = fr.face_encodings(my_image)[0]

    known_face_encondings = [my_face_encoding]
    known_face_names = ["Abhiroop Basak"]

    while True: 
        ret, frame = video_capture.read()

        rgb_frame = frame[:, :, ::-1]

        face_locations = fr.face_locations(rgb_frame)
        face_encodings = fr.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):

            matches = fr.compare_faces(known_face_encondings, face_encoding)

            name = "Unknown"

            face_distances = fr.face_distance(known_face_encondings, face_encoding)

            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                for a in range(10):
                    print("Welcome\nRedirecting in {0} seconds...".format(a))
                    corr=1
                return corr
                
            else:
                corr=0
                return corr
            
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            cv2.rectangle(frame, (left, bottom -35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        cv2.imshow('Security_FaceRecognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return corr


def mail(receiver_email):
    port = 587 
    smtp_server = "smtp.gmail.com"
    sender_email = "team.mars.04@gmail.com"
    # receiver_email = "team.mars.04@gmail.com"
    password = "mars@12345"
    message = MIMEMultipart("alternative")
    message["Subject"] = "MAPCovid Alert"
    message["From"] = sender_email
    message["To"] = receiver_email

    html = """\
    <html>
    <body background="bg3.jpg">
        <h1>Hey User,<br></h1>
        <h3>Hope you are doing well. Thank you for joining the MAPCovid Network.<br></h3>
            Let me guide you through the vaccination program in your area.
        Here at MAPCovid, you will receive realtime information regarding all vaccination centers near you! Visit us anytime to know more about the vaccination drives in your community!
        </p>
        <br><br>
       <a href="http://127.0.0.1:8000/">Check out more</a>
    </body>
    </html>
    """
    part2 = MIMEText(html, "html")

    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
    print("Mail sent")



def pic(request):
    client=MongoClient("mongodb+srv://admin_project:project@clusterlarkai1.idztf.mongodb.net/{{dbname}}?retryWrites=true&w=majority")
    db=client.get_database('covid_tracker')
    records=db.covid

    name=request.GET["name"]
    covid=request.GET["covid"]
    vaccine=request.GET["vaccine"]
    email=request.GET["email"]
    password=request.GET["password"]

    dpname=takepic(name)
    now= datetime.datetime.now()
    new_user={
      'name' : name,
      'email' : email,
      'password' : password,
      'covid' : covid,
      'vaccine' : vaccine,
      'picture' : dpname
    }

    records.insert_one(new_user)

    mail(email)
    
    return render(request,"Profile.html",{'name':name,'email':email,'covid':covid,'vaccine':vaccine,'picture':dpname})

def login(request):
    email=request.GET["email"]
    password=request.GET["password"]

    client=MongoClient("mongodb+srv://admin_project:project@clusterlarkai1.idztf.mongodb.net/{{dbname}}?retryWrites=true&w=majority")
    db=client.get_database('covid_tracker')
    records=db.covid

    rg=list(records.find())
    print("List: ",rg)
    flag=0
    for i in range(0,len(rg)):

        if (rg[i]['email']==email and rg[i]['password']==password):
            path=rg[i]['picture']
            name=rg[i]['name']
            covid=rg[i]['covid']
            vaccine=rg[i]['vaccine']
            flag=1
            break
    # directory="C:/Users/admin/Desktop/mapcovid/media"
    # for filename in os.listdir(directory):
    #     if filename.endswith(".png"): 
    #         print(filename)
    p="media/{0}".format(path)
    check=face_auth(path)
    if check==1:
        path=path[6:]
        return render(request,"Profile.html",{'name':name,'email':email,'covid':covid,'vaccine':vaccine,'picture':path})
    else:
        return render(request,"index.html")


def dashboard(request):
    client=MongoClient("mongodb+srv://admin_project:project@clusterlarkai1.idztf.mongodb.net/{{dbname}}?retryWrites=true&w=majority")
    db=client.get_database('covid_tracker')
    records=db.covid
    db=list(records.find())
    csv_columns=['_id','name','email','password','covid','vaccine','picture']
    csv_file='db.csv'
    with open(csv_file,'w') as csvfile:
        writer=csv.DictWriter(csvfile,fieldnames=csv_columns)
        writer.writeheader()
        for data in db:
            writer.writerow(data)

    print("Database created")

    
    data=pd.read_csv('db.csv')
    res=data['vaccine']
    res.value_counts()
    res1=res.replace(to_replace ="Yes",value = 1)
    res2=res1.replace(to_replace ="No",value = 0)
    sn.distplot(res2)
    plt.savefig("media/Figure1.png")
    sn.countplot(x='vaccine', data=data);
    plt.title('Count of people who have been vaccinated')
    plt.savefig("media/Figure2.png")
    ser=data['covid']
    ser.value_counts()
    ser1=ser.replace(to_replace ="Positive",value = +1)
    ser2=ser1.replace(to_replace ="Negative",value = -1)
    ser3=ser2.replace(to_replace ="Not Tested",value = 0)
    sn.countplot(x='covid', data=data)
    plt.title('Count of people who have COVID')
    plt.savefig("media/Figure3.png")
    sn.distplot(ser3)
    plt.savefig("media/Figure4.png")
    # res2.hist(res2, bins=35)
    # plt.title('Distribution of vaccines')
    # plt.xlabel('Vaccines')
    # plt.savefig("media/Figure5.png")
    count=count1=0
    for i in range(0,len(res)):
        if(res2[i]==1):
            count=count+1
        if(res2[i]==0):
            count1=count1+1
    ct=ct1=ct2=0
    for i in range(0,len(ser)):
        if(ser3[i]==1):
            ct=ct+1
        if(ser3[i]==-1):
            ct1=ct1+1
        if(ser3[i]==0):
            ct2=ct2+1
    slice_ = [count,count1]
    label = ['Vaccinated', 'Not Vaccinated']
    colors = ['g', 'r']
    plt.pie(slice_, labels=label, colors=colors, startangle=90, autopct='%.1f%%')
    plt.title("Vaccine Demographics")
    # plt.show()
    plt.savefig("media/Figure6.png")
    slice_ = [ct,ct1,ct2]
    label = ['Covid Positive', 'Covid Negative', 'Not Tested']
    colors = ['r', 'b', 'g']
    plt.pie(slice_, labels=label, colors=colors, startangle=90, autopct='%.1f%%')
    plt.title("COVID Demographics")
    # plt.show()
    plt.savefig("media/Figure7.png")
    a=b=c=d=0
    for i in range(0,len(ser)):
        if(ser2[i]==1) and (res2[i]==0):
            a=a+1
        if(ser2[i]==1) and (res2[i]==1):
            b=b+1
        if(ser2[i]==-1) and (res2[i]==0):
            c=c+1
        if(ser2[i]==-1) and (res2[i]==1):
            d=d+1
    slice_ = [a,b]
    label = ['Covid Positive and vaccinated', 'Covid Positive and not vaccinated']
    colors = ['#ff7f0e', '#d62728']
    plt.pie(slice_, labels=label, colors=colors, startangle=90, autopct='%.1f%%')
    plt.title("COVID Demographics")
    plt.savefig("media/Figure8.png")
    slice_ = [c,d]
    label = ['Covid Negative and vaccinated', 'Covid Negative and not vaccinated']
    colors = ['b', 'g']
    plt.pie(slice_, labels=label, colors=colors, startangle=90, autopct='%.1f%%')
    plt.title("COVID Demographics")
    plt.savefig("media/Figure9.png")
    # ax = sn.boxplot(x=res2, y=ser, data=data)
    # plt.savefig("media/Figure10.png")

    
    return render(request,"dashboard.html")
