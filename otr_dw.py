#!/usr/bin/env python3
'''
pip3 install beautifulsoup4, requests
'''

from bs4 import BeautifulSoup
import requests
import io
import m3u8

import sys
import xml.etree.ElementTree as ET

def find_iframe(url) -> str:
	''' Поиск на странице iframe 
	
	returns:
		возвращает src на iframe
	'''
	r = requests.get(url)

	bf_data = BeautifulSoup(r.text, "html.parser")

	iframe = bf_data.find_all("iframe", attrs={"allow": "encrypted-media"})
	
	if len(iframe) > 1:
		print("Упс чет многовато получатеся iframe\n\n")
		
		for item in iframe:
			print(item)
			print('=====')

		sys.exit(-1)

	src = "http:" + iframe[0]['src']

	return src

def find_into_iframe(src) -> str:
	''' Парсит содержимое iframe и находит следующий кусок

	returns:
		Возвращает строку на какой то набор данных для плеера
	'''
	r = requests.get(src)

	bf_data = BeautifulSoup(r.text, "html.parser")
	span = bf_data.find_all("span")

	if len(span) > 1:
		print("Упс а их чет много")

		print(span)
		sys.exit(-1)

	data_config = span[0]['data-config']
	r = data_config.split("=")

	if len(r) < 2:
		print("Чет не рассплитилось")
		print(data_config)
		sys.exit(-1)
	
	url = r[1]

	return url

def parse_xml_data_config(url) -> str:
	'''
	return:
		Возвращаем адрес уже на видео
	'''
	
	r = requests.get(url)
	root = ET.fromstring(r.text)
	
	video = None
	video_hd = None

	for child in root:
		if child.tag.lower() == 'video':
			video = child.text
		if child.tag.lower() == 'video_hd':
			video_hd = child.text
		
	video_url = video_hd if video_hd is not None else video

	return video_url

def extract_video_m3u8_playlist_url(url):
	r = requests.get(url)

	root = ET.fromstring(r.text)
	
	track = root.find('iphone').find('track').text

	return track

def select_resolution_from_play_list(url):
	''' Выбираем нужное разрешение для потока
	'''
	data = m3u8.load(url)

	for index, item in enumerate(data.playlists):
		print("#{} - {}".format(index+1, item.stream_info.resolution))

	ind = input("Выберите нужное разрешение: ")
	ind = int(ind) - 1
	
	url_m3u8 = data.playlists[ind].uri
	return url_m3u8

def download_m3u8(url, file_name):
	''' Непосредственно само скачавание
	'''
	data = m3u8.load(url)
	
	with open(file_name, "wb") as f:
		print("Сегментов:", len(data.segments))

		for index, segment in enumerate(data.segments):
			
			r = requests.get(segment.uri, stream=True)
			f.write(r.raw.read())
			print("Скачали {} сегмент".format(index))

if __name__ == "__main__":

	url = input("Вверди URL адрес: ")

	# if len(sys.argv) < 2:
	# 	print("Нужно ввести URL адрес")
	# 	sys.exit(-1)

	# url = sys.argv[1]

	download_m3u8(
		select_resolution_from_play_list(
			extract_video_m3u8_playlist_url(
				parse_xml_data_config(
					find_into_iframe(
						find_iframe(url)
					)
				)
			)
		),
		"test.mp4"
	)

	input("Я закончил, нажмите Enter")
	