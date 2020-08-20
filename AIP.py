# -*- coding: utf-8 -*-
# @Author: hanzhiyun
# @Email:  hanzhiyun1995@foxmail.com
# @Date:   2020-08-15 21:02:44
# @Last Modified by:   hanzhiyun
# @Last Modified time: 2020-08-20 19:33:43

# automatic investment plan

import os
import requests
import datetime as dt
import json, js2py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xlwings as xw
# import urllib

# import io
# import sys
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

# 接口构造

# 构造一个url
def getUrl(fscode):
	head = 'http://fund.eastmoney.com/pingzhongdata/'
	# tail = '.js?v='+ time.strftime("%Y%m%d%H%M%S",time.localtime())
	tail = '.js?v='+ dt.datetime.now().strftime("%Y%m%d%H%M%S")
	return head+fscode+tail

def getValueUrl(index_code):
	head = 'https://danjuanapp.com/djapi/index_eva/detail/'
	return head + index_code

# 时间戳转换为日期
def getDate(timeStamp):
	# 输入为毫秒格式，转为秒
	timeStamp /= 1000
	timeArray = dt.datetime.fromtimestamp(timeStamp)
	timeStyle = timeArray.strftime("%Y-%m-%d")
	return timeStyle

# 获取净值
def getWorth(fscode):
	#用requests获取到对应的文件
	content = requests.get(getUrl(fscode))
	# jsContent2 = js2py.EvalJs()
	# jsContent2.execute(content.text)
	# name2 = jsContent2.fS_name
	# print(name2)
   #使用js2py获取到相应的数据
	jsContent = js2py.EvalJs()
	jsContent.execute(content.text)
	name = jsContent.fS_name
	code = jsContent.fS_code
	#单位净值走势,时间正方向
	netWorthTrend = jsContent.Data_netWorthTrend
	#累计净值走势
	ACWorthTrend = jsContent.Data_ACWorthTrend
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
	return name, netWorth, ACWorth


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
	return name, eva_type

# 计算移动均线
def getMA(data, N):
	data['MA_' + str(N)] = data[1].rolling(N).mean() 


# 均线策略
def aveStrategy(data):
	# 返回投资金额比例系数
	netWorth_T = float(data.iloc[-1,1])
	MA_T = float(data.iloc[-1,2])
	ten_AM = float(data.iloc[-10:,1].max())/float(data.iloc[-10:,1].min()) - 1
	ten_AM = ten_AM * 100
	ref_T = (netWorth_T - MA_T) / MA_T * 100
	print('T-1日净值: %.3f\n均线值： %.3f' %(netWorth_T, MA_T))
	print('T-1日净值比均线高 %.2f%%, 十日振幅为 %.2f%%' %(ref_T, ten_AM))
	all_list = [format(netWorth_T, '.3f'), format(MA_T, '.3f'), format(ref_T, '.2f'), format(ten_AM, '.2f')]
	if ref_T >= 0 and ref_T < 15:
		k = 0.9
	elif ref_T >= 15 and ref_T <50:
		k = 0.8
	elif ref_T >=50 and ref_T < 100:
		k = 0.7
	elif ref_T >= 100:
		k = 0.6
	elif ref_T >= -5 and ref_T < 0:
		if ten_AM >= 5:
			k = 0.6
		else:
			k = 1.6
	elif ref_T >= -10 and ref_T < -5:
		if ten_AM >= 5:
			k = 0.7
		else:
			k = 1.7
	elif ref_T >= -20 and ref_T < -10:
		if ten_AM >= 5:
			k = 0.8
		else:
			k = 1.8
	elif ref_T >= -30 and ref_T < -20:
		if ten_AM >= 5:
			k = 0.9
		else:
			k = 1.9
	elif ref_T >= -40 and ref_T < -30:
		if ten_AM >= 5:
			k = 1
		else:
			k = 2
	elif ref_T >= -50 and ref_T < -40:
		if ten_AM >= 5:
			k = 1.1
		else:
			k = 2.1
	else:
		k = 0
	return all_list, k
# 记录投资情况
def record(index_code, fund_code, record_list):
	# 初始化xlwings模块
	app = xw.App(visible=True, add_book=False)
	app.display_alerts=False
	app.screen_updating=False

	record_file = '基金定投记录.xlsx'
	# 判断是否存在excel文件
	if not os.path.exists(record_file):
		wb = app.books.add() 		# 创建新文件
		wb.save(record_file)
	else:
		wb = app.books.open(record_file) # 打开已有文件
	
	# 判断是否存在相应工作表
	shts = wb.sheets
	shts_name = [shts[i].name for i in range(len(shts))]
	# print(shts_name)
	if fund_code in shts_name:
		# print('exist')
		sht = wb.sheets[fund_code] # 打开已有页面
	else:
		# print('non-exist')
		sht = wb.sheets.add(fund_code) 	# 创建新的页面
		fund_name, index_name = record_list[-2:]
		header1 = ['基金名称', '基金代码', '标的指数', '指数代码', '总买入金额（元）']
		header2 = [fund_name, "'" + fund_code, index_name, index_code, '=SUM(G:G)']
		header3 = ['日期', 'T-1日净值', '均线值', 'T-1日净值较均线高（%）', '十日振幅（%）', '指数估值', '今日买入（元）']
		sht.range('a1').value = header1
		sht.range('a2').value = header2
		sht.range('a3').value = header3
		# 格式排版
		sht.range('a1:g3').column_width = 12 # 设置列宽
		sht.range('a1:g3').api.HorizontalAlignment = -4108
		# -4108 水平居中。 -4131 靠左，-4152 靠右。 
		sht.range('a1:g3').api.VerticalAlignment = -4130
		# -4108 垂直居中（默认）。 -4160 靠上，-4107 靠下， -4130 自动换行对齐。
		sht.autofit('r') # 自适应行高

	# sht.autofit('c') # 自适应列宽

	# 获取表行列数
	info = sht.used_range
	nrows = info.last_cell.row
	ncols = info.last_cell.column
	# print(nrows, ncols)

	# 获取时间
	# today = time.strftime("%Y/%m/%d",time.localtime())
	today = dt.date.today().strftime("%Y/%m/%d")
	# print(today)

	# 写入内容
	content = [today]
	content.extend(record_list[:6])
	# print(content)

	if nrows > 3:		
		# print(sht.range('a' + str(nrows)).value)
		read_date = sht.range('a' + str(nrows)).value.strftime("%Y/%m/%d")
		# print(read_date)
		if read_date != today:
			print(read_date)
			sht.range('a' + str(nrows + 1)).value = content
		else:
			print("Today's data already exists!")
	else:
		sht.range('a' + str(nrows + 1)).value = content

	# 格式排版
	sht.range(nrows + 1, 1).row_height = 20 # 设置行高
	sht.range(nrows + 1, 1).expand('right').api.HorizontalAlignment = -4152
	# -4108 水平居中。 -4131 靠左，-4152 靠右。


	# 文件保存、关闭、退出	
	wb.save()
	wb.close()
	app.quit()

# # 画趋势图
# plt.figure(figsize=(10,5))
# # plt.plot(netWorth[-60:, 0], netWorth[-60:, 1])
# plt.plot(netWorth[-30:, 0], netWorth[-30:, 1].astype(np.float))
# new_ticks = netWorth[-30::5, 0]
# plt.xticks(new_ticks)
# plt.show()

# 定义AIP函数，自动计算
def aip(index_code, fund_code, basic_invest):
	# 标的指数、基金代码、定投基础金额，单位：元
	index_name, eva = getValue(index_code)
	fund_name, netWorth, ACWorth = getWorth(fund_code)
	ma_data = pd.DataFrame(netWorth)
	getMA(ma_data, 250)
	# print(ma_data)	
	if eva == 'low':
		# 低估值下策略
		(record_list, k) = aveStrategy(ma_data)
		real_invest = basic_invest * k
		print('估值偏低，今日买入 %d 元！' %real_invest)
	elif eva == 'mid':
		print('估值适中，暂停定投！')
	elif eva == 'high':
		print('估值偏高，考虑卖出！')
	record_list.extend([eva, real_invest, fund_name, index_name])
	record(index_code, fund_code, record_list)



if __name__ == '__main__':
	index_code = 'SZ399986' # 标的指数
	fund_code = '001594' # 基金代码
	basic_invest = 20  # 定投基础金额，单位：元
	index_name, eva = getValue(index_code)
	fund_name, netWorth, ACWorth = getWorth(fund_code)
	ma_data = pd.DataFrame(netWorth)
	getMA(ma_data, 250)
	# print(ma_data)	
	if eva == 'low':
		# 低估值下策略
		(record_list, k) = aveStrategy(ma_data)
		real_invest = basic_invest * k
		print('估值偏低，今日买入 %d 元！' %real_invest)
	elif eva == 'mid':
		print('估值适中，暂停定投！')
	elif eva == 'high':
		print('估值偏高，考虑卖出！')
	# print(record_list)
	record_list.extend([eva, real_invest, fund_name, index_name])
	# print(record_list)
	record(index_code, fund_code, record_list)
