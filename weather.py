#本程序从中国天气网（http://www.weather.com.cn）按照地区获取从今天到7天后每个地区所有的城市的各项天气情况
#由于中国天气网18点后今日白天的天气情况就会消失，晚上更新会有部分数据消失。
#所有的数据均存入CSV表格
from bs4 import BeautifulSoup
import requests								
import numpy as np
import pandas as pd
import datetime 

def get_city(soup):						#获取每个地区城市的名称
	city_name = soup.find_all(width='83',height='23')   	#因为抓取的是7天的天气，所以每个城市会有七次的重复，这个在主程序中会处理
	ct = []
	for city in city_name:
		ct.append(list(city.strings)[1])
	ct = np.array(ct)
	#print(ct)
	return ct


def get_high_temperature(soup):					#获取每个城市当天的最高气温
	city_high_temperature = soup.find_all(width='92')
	tp_high = []
	for temperature in city_high_temperature:
		if temperature.string == '最高气温':
			continue
		else:
			tp_high.append(temperature.string)
	tp_high = np.array(tp_high)
	#print(tp_high)
	return tp_high


def get_low_temperature(soup):
	city_low_temperature = soup.find_all(width='86')	#获取每个城市当天的最低气温
	tp_low = []
	for temperature_low in city_low_temperature:		#里面参杂了一些多余信息，需要剔除
		if temperature_low.string == '最低气温':
			continue
		else:
			tp_low.append(temperature_low.string)
	tp_low = np.array(tp_low)
	#print(tp_low)
	return tp_low


def get_sun_condition(soup):
	city_sun_condition = soup.find_all(width='89')		#获取当天天气情况（白天）
	sun = []
	for condition in city_sun_condition:
		if condition.string == "天气现象":
			continue
		else:
			sun.append(condition.string)
	sun = np.array(sun)
	#print(sun)
	return sun


def get_moon_conditon(soup):
	city_moon_condition = soup.find_all(width='98')		#获取当天天气情况（夜晚）
	moon = []
	for condition_moon in city_moon_condition:
		if condition_moon.string == "天气现象":
			continue
		else:
			moon.append(condition_moon.string)
	moon = np.array(moon)
	#print(moon)
	return moon


def get_sun_wind(soup):
	city_sun_wind = soup.find_all(width='162')		#获取每个城市白天的风力状况
	sun_wind_temp = []
	sun_wind = []
	for wind_sun_condition in city_sun_wind:
	#	print(list(wind_sun_condition.strings))
		for item in wind_sun_condition.strings:
			if item == '风向风力' or item == '\n':
				continue
			else:
				sun_wind_temp.append(item)
	
	sun_wind_temp = np.array(sun_wind_temp)				#网页抓取的文字格式杂乱，做些处理
	sun_wind_temp = sun_wind_temp.reshape(int(len(sun_wind_temp)/2),2)		
	num_ = 0
	for num_ in range(int(len(sun_wind_temp))):
		#print(sun_wind_temp[num_][0],sun_wind_temp[num_][1])
		sun_wind = np.append(sun_wind,[sun_wind_temp[num_][0]+sun_wind_temp[num_][1]])
		num_ += 1
	#print(sun_wind)
	return sun_wind

def get_moon_wind(soup):
	city_moon_wind = soup.find_all(width='177')			#获取每个城市夜晚的风力状况
	moon_wind_temp = []
	moon_wind = []
	for wind_moon_condition in city_moon_wind:
		for item2 in wind_moon_condition.strings:
			if item2 == '风向风力' or item2 == '\n':
				continue
			else:
				moon_wind_temp.append(item2)
	
	moon_wind_temp = np.array(moon_wind_temp)			#格式杂乱，同上面的处理方法
	moon_wind_temp = moon_wind_temp.reshape(int(len(moon_wind_temp)/2),2)
	#print(len(moon_wind_temp))
	num = 0
	for num in range(int(len(moon_wind_temp))):
		#print(moon_wind_temp[num][0],moon_wind_temp[num][1])
		moon_wind = np.append(moon_wind,[moon_wind_temp[num][0]+moon_wind_temp[num][1]])
		num += 1
	#print(len(moon_wind))
	return moon_wind


def get_date():								#获取从今天开始七天后的日期
	date_list = []
	for time in range(7):
		today = datetime.date.today()
		delta = datetime.timedelta(days=time)
		day = (today + delta).strftime('%Y-%m-%d')		#输出成文本状态
		date_list.append(day)
	#print(date_list)
	return date_list


aeras = ['hb','db','hd','hz','hn','xb','xn','gat']
for aera in aeras:
	req = requests.get("http://www.weather.com.cn/textFC/{}.shtml".format(aera))	#全国各地区循环
	#req = requests.get("http://www.weather.com.cn/textFC/hb.shtml")
	req.encoding = 'utf-8'								#需要转换，不然无法显示中文
	html = req.text
	soup = BeautifulSoup(html,'lxml')
	#print(len(get_city(soup)))
	
	array_city = get_city(soup)							#此项将重复的数据部分平均的分成7分，刚好对应7天的数据
	array_city = np.split(array_city,7)						#刚好处理了城市列表中重复的问题

	array_sun_condition = get_sun_condition(soup)
	array_sun_condition = np.split(array_sun_condition,7)

	array_sun_wind = get_sun_wind(soup)
	array_sun_wind = np.split(array_sun_wind,7)

	array_high_temperature = get_high_temperature(soup)
	array_high_temperature = np.split(array_high_temperature,7)

	array_moon_condition = get_moon_conditon(soup)
	array_moon_condition = np.split(array_moon_condition,7)

	array_moon_wind = get_moon_wind(soup)
	array_moon_wind = np.split(array_moon_wind,7)

	array_low_temperature = get_low_temperature(soup)
	array_low_temperature = np.split(array_low_temperature,7)


	i = 0
	for i in range(7):
		content = pd.DataFrame({						#将本地区的天气汇总成表格输出
				"城市": array_city[i],
				"白天天气状况": array_sun_condition[i],
				"白天风力状况": array_sun_wind[i],
				"最高气温（°C）": array_high_temperature[i],
				"夜晚天气状况": array_moon_condition[i],
				"夜晚风力状况": array_moon_wind[i],
				"最低气温（°C）": array_low_temperature[i]
			})
		content.to_csv('{} {}.csv'.format(get_date()[i],aera),encoding='utf-8-sig')
		#print(content)

