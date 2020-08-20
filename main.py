# -*- coding: utf-8 -*-
# @Author: hanzhiyun
# @Email:  hanzhiyun1995@foxmail.com
# @Date:   2020-08-18 16:32:15
# @Last Modified by:   hanzhiyun
# @Last Modified time: 2020-08-20 11:42:16


import AIP

if __name__ == '__main__':

	AIP.aip('SZ399986', '001594', 20) 
	# 标的指数：中证银行  基金名称：天弘中证银行指数A
	
	AIP.aip('SH000922', '100032', 20)
	# 标的指数：中证红利  基金名称：富国中证红利指数增强A

	AIP.aip('SZ399998', '161724', 20)
	# 标的指数：中证煤炭  基金名称：招商中证煤炭等权指数分级	

	AIP.aip('SPACEVCP', '501310', 20)
	# 标的指数：标普价值  基金名称：华宝沪港深中国增强(LOF)A

	temps = input("Press <enter> to exit")
	# 让窗口不会自动关闭
