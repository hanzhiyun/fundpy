# -*- coding: utf-8 -*-
# @Author: hanzhiyun
# @Email:  hanzhiyun1995@foxmail.com
# @Date:   2020-08-15 21:02:44
# @Last Modified by:   hanzhiyun
# @Last Modified time: 2020-08-17 15:37:07

# automatic investment plan

import requests
import time
import execjs, json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# import urllib

# import io
# import sys
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

# 接口构造

# 构造一个url
def getUrl(fscode):
	head = 'http://fund.eastmoney.com/pingzhongdata/'
	tail = '.js?v='+ time.strftime("%Y%m%d%H%M%S",time.localtime())
	return head+fscode+tail

def getValueUrl(index_code):
	head = 'https://danjuanapp.com/djapi/index_eva/detail/'
	return head + index_code

# 时间戳转换为日期
def getDate(timeStamp):
	# 输入为毫秒格式，转为秒
	timeStamp /= 1000
	timeArray = time.localtime(timeStamp)
	timeStyle = time.strftime("%Y-%m-%d", timeArray)
	return timeStyle

# 获取净值
def getWorth(fscode):
	#用requests获取到对应的文件
	content = requests.get(getUrl(fscode))
   #使用execjs获取到相应的数据
	jsContent = execjs.compile(content.text)
	name = jsContent.eval('fS_name')
	code = jsContent.eval('fS_code')
	#单位净值走势,时间正方向
	netWorthTrend = jsContent.eval('Data_netWorthTrend')
	#累计净值走势
	ACWorthTrend = jsContent.eval('Data_ACWorthTrend')
	# print(netWorthTrend)
	netWorth = []
	ACWorth = []
   #提取出里面的净值
	for dayWorth in netWorthTrend:
		netWorth.append([getDate(dayWorth['x']), dayWorth['y']])
		# print(dayWorth)
	for dayACWorth in ACWorthTrend:
		ACWorth.append([getDate(dayACWorth[0]), dayACWorth[1]])
	print('基金名称：%s' %name)
	print('基金代码：%s' %code)	
	# print(name, code)
	netWorth = np.array(netWorth)
	ACWorth = np.array(ACWorth)
	return netWorth, ACWorth


# 获取指数估值
def getValue(index_code):
	header = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
	(KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 Edg/84.0.522.59'
	}
	content = requests.get(getValueUrl(index_code), headers = header)
	# print(content.text)
	jsonContent = json.loads(content.text)
	jsdata = jsonContent['data']
	name = jsdata['name']
	code = jsdata['index_code']
	eva_type = jsdata['eva_type']
	print('标的指数：%s' %name)
	print('指数代码：%s' %code)
	print('指数估值：%s' %eva_type)
	# print(name, code, eva_type)
	return eva_type

# 计算移动均线
def getMA(data, N):
	data['MA_' + str(N)] = data[1].rolling(N).mean() 


# 均线策略
def aveStrategy(data):
	# 返回投资金额比例系数
	netWorth_T = float(data.iloc[-1,1])
	MA_T = float(data.iloc[-1,2])
	ten_AM = float(data.iloc[-10:,1].max())/float(data.iloc[-10:,1].min()) - 1
	ten_AM = int(ten_AM * 100)
	ref_T = int((netWorth_T - MA_T) / MA_T * 100)
	print(netWorth_T, MA_T)
	print('T-1日净值比均线高 %d%%, 十日振幅为 %d%%' %(ref_T,ten_AM))
	if ref_T >= 0 and ref_T < 15:
		return 0.9
	elif ref_T >= 15 and ref_T <50:
		return 0.8
	elif ref_T >=50 and ref_T < 100:
		return 0.7
	elif ref_T >= 100:
		return 0.6
	elif ref_T >= -5 and ref_T < 0:
		if ten_AM >= 5:
			return 0.6
		else:
			return 1.6
	elif ref_T >= -10 and ref_T < -5:
		if ten_AM >= 5:
			return 0.7
		else:
			return 1.7
	elif ref_T >= -20 and ref_T < -10:
		if ten_AM >= 5:
			return 0.8
		else:
			return 1.8
	elif ref_T >= -30 and ref_T < -20:
		if ten_AM >= 5:
			return 0.9
		else:
			return 1.9
	elif ref_T >= -40 and ref_T < -30:
		if ten_AM >= 5:
			return 1
		else:
			return 2
	elif ref_T >= -50 and ref_T < -40:
		if ten_AM >= 5:
			return 1.1
		else:
			return 2.1
	else:
		return 0


# netWorth, ACWorth = getWorth('001594')
# df = pd.DataFrame(netWorth)
# getMA(df, 250)
# print(df)

# # print(netWorth[-30:, 1])
# # print(netWorth)

# # 画趋势图
# plt.figure(figsize=(10,5))
# # plt.plot(netWorth[-60:, 0], netWorth[-60:, 1])
# plt.plot(netWorth[-30:, 0], netWorth[-30:, 1].astype(np.float))
# new_ticks = netWorth[-30::5, 0]
# plt.xticks(new_ticks)
# plt.show()

if __name__ == '__main__':
	index_code = 'SZ399986' # 标的指数
	fund_code = '001594' # 基金代码
	basic_invest = 20  # 定投基础金额，单位：元
	eva = getValue(index_code)
	netWorth, ACWorth = getWorth(fund_code)
	ma_data = pd.DataFrame(netWorth)
	getMA(ma_data, 250)
	# print(ma_data)	
	if eva == 'low':
		# 低估值下策略
		k = aveStrategy(ma_data)
		real_invest = basic_invest * k
		print('估值偏低，今日买入 %d 元！' %real_invest)
	elif eva == 'mid':
		print('估值适中，暂停定投！')
	elif eva == 'high':
		print('估值偏高，考虑卖出！')
