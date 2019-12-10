import requests
import requests_ftp
import subprocess
import filecmp
from os import path
import pycurl

old_path = '/home/pi/scripts/ddwrt/old.txt'
new_path = '/home/pi/scripts/ddwrt/new.txt'

def download_data(file_name):
	requests_ftp.monkeypatch_session()
	resp = requests.Session().list('ftp://ftp.dd-wrt.com/betas/2019/')
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
		send_pushbullet(x[-1].rstrip())
	swap_files()

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