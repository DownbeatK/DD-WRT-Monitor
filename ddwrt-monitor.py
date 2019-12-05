import requests
import requests_ftp
import subprocess
import filecmp
from os import path
import pycurl

def download_data(file_name):
	requests_ftp.monkeypatch_session()
	resp = requests.Session().list('ftp://ftp.dd-wrt.com/betas/2019/')
	file_path = open(file_name, 'w')
	file_path.write((resp.content).decode('utf-8'))
	file_path.close()
	if(file_name == 'new.txt'):
		compare_files()

def compare_files():
	if not(filecmp.cmp('old.txt', 'new.txt')):
		file_path = open('new.txt', 'r')
		x = file_path.readlines()[-1].split(' ')
		file_path.close()
		send_pushbullet(x[-1].rstrip())
	swap_files()

def send_pushbullet(version):
	postData = '{"type":"note", "title":"DD-WRT Update", "body":"' + version + ' is now available"}'
	push_curl = pycurl.Curl()
	push_curl.setopt(pycurl.URL, 'https://api.pushbullet.com/v2/pushes')
	push_curl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
	push_curl.setopt(pycurl.USERPWD, '<API>')
	push_curl.setopt(pycurl.POST, 1)
	push_curl.setopt(pycurl.POSTFIELDS, postData)
	push_curl.perform()

def swap_files():
	if(path.exists('new.txt')):
		subprocess.Popen('rm old.txt', shell=True)
		subprocess.Popen('mv new.txt old.txt', shell=True)

if(path.exists('old.txt')):
	download_data('new.txt')
else:
	download_data('old.txt')