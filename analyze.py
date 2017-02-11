#!/usr/bin/python

# 2017 load pictures and analyze

import time
import sys
import datetime
import subprocess
import sys
import urllib2
import os
import datetime
import ftplib
import traceback
import math
import random, string
import base64
import json
import paho.mqtt.client as mqtt
import picamera
from time import sleep
from time import gmtime, strftime
import inception_predict

packet_size=3000

def randomword(length):
 return ''.join(random.choice(string.lowercase) for i in range(length))

# Create camera interface
camera = picamera.PiCamera()
while True:

    # Create unique image name
	uniqueid = 'mxnet_uuid_{0}_{1}'.format(randomword(3),strftime("%Y%m%d%H%M%S",gmtime()))

    # Take the jpg image from camera
    filename = '/home/pi/cap.jpg'
    
    # Capture image from RPI
    camera.capture(filename)
 
    # Run inception prediction on image
    topn = inception_predict.predict_from_local_file(filename, N=5)
      
 	# CPU Temp
    p = subprocess.Popen(['/opt/vc/bin/vcgencmd','measure_temp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
       	
    # MQTT
	client = mqtt.Client()
	client.username_pw_set("username","password")
	client.connect("mqttcloudprovider", 14162, 60)
	
	# CPU Temp
	out = out.replace('\n','')
	out = out.replace('temp=','')
	
	# 5 MXNET Analysis
	top1 = str(topn[0][1])
	top1pct = str(round(topn[0][0],3) * 100)

	top2 = str(topn[1][1])
	top2pct = str(round(topn[1][0],3) * 100)
		
	top3 = str(topn[2][1])
	top3pct = str(round(topn[2][0],3) * 100)

	top4 = str(topn[3][1])
	top4pct = str(round(topn[3][0],3) * 100)

	top5 = str(topn[4][1])
	top5pct = str(round(topn[4][0],3) * 100)
	
	row = [ { 'uuid': uniqueid,  'top1pct': top1pct, 'top1': top1, 'top2pct': top2pct, 'top2': top2,'top3pct': top3pct, 'top3': top3,'top4pct': top4pct,'top4': top4, 'top5pct': top5pct,'top5': top5, 'cputemp': out} ]
	json_string = json.dumps(row)
	
	client.publish("mxnet",payload=json_string,qos=1,retain=False)
	client.disconnect()
	
