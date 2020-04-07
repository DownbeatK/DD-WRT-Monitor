import requests
import requests_ftp
import subprocess
import filecmp
from os import path
import pycurl
import http.client
import urllib

old_path = '/home/pi/scripts/ddwrt/old.txt'
new_path = '/home/pi/scripts/ddwrt/new.txt'
found_path = '/home/pi/scripts/ddwrt/found.txt'

def download_data(file_name):
	requests_ftp.monkeypatch_session()
	resp = requests.Session().list('ftp://ftp.dd-wrt.com/betas/2020/')
	file_path = open(file_name, 'w')
	file_path.write((resp.content).decode('utf-8'))
	file_path.close()
	if(file_name == new_path):
		compare_files()

def compare_files():
	if not(filecmp.cmp(old_path, new_path)):
		file_path = open(new_path, 'r')
		x = file_path.readlines()[-1].split(' ')
		file_path.close()
		check_found(x[-1].rstrip())
	swap_files()

def check_found(version):
	found_prev = 0
	file_path = open(found_path, 'r')
	file_contents = file_path.readlines()
	file_path.close()

	if(len(version) is 17):
		for line in file_contents:
			if(line[:-1] == version):
				found_prev = 1
				break

	if(found_prev is not 1):
		file_path = open(found_path, 'a+')
		file_path.write(version + "\n")
		file_path.close()
		send_pushover(version)
		send_pushbullet(version)

def send_pushover(version):
	conn = http.client.HTTPSConnection("api.pushover.net:443")
	conn.request("POST", "/1/messages.json", urllib.parse.urlencode({"token": "<TOKEN>", "user": "<USER>", "message": version + " is now available",}), { "Content-type": "application/x-www-form-urlencoded" })
	conn.getresponse()

def send_pushbullet(version):
	push_curl = pycurl.Curl()
	push_curl.setopt(pycurl.URL, 'https://api.pushbullet.com/v2/pushes')
	push_curl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
	push_curl.setopt(pycurl.USERPWD, '<API>')
	push_curl.setopt(pycurl.POST, 1)
	push_curl.setopt(pycurl.POSTFIELDS, '{"channel_tag":"ddwrtupdates", "type":"note", "title":"DD-WRT Update", "body":"' + version + ' is now available"}')
	push_curl.perform()

def swap_files():
	if(path.exists(new_path)):
		subprocess.Popen('rm ' + old_path, shell=True)
		subprocess.Popen('mv ' + new_path + ' ' + old_path, shell=True)

if(path.exists(old_path)):
	download_data(new_path)
else:
	download_data(old_path)
