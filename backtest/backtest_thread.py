#monitoring code
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 18:03:40 2023

@author: TENSOR
"""
import pandas as pd
import numpy as np
import copy
#import tsci
import pdb
import time
import warnings
warnings.filterwarnings("ignore")
import math

import datetime
import sys
sys.path.append("../generate_signal")
sys.path.append("../framework")

from account_class import account
from system_function import get_price
from system_function import get_today_open_price
from system_function import get_total_value
from system_function import get_total_value_in_a_monnt
from system_function import get_total_value_every_day
from system_function import stop_lost
from system_function import order_buy
from system_function import order_sell
from system_function import borrow_stock
from system_function import return_stock

from generate_signal_thread import signal

def strategy_test(para1,para2,Open,High,Low,Close):
    cyf=account("dont_care","dont_care",10000000,Close)
    start_coin=cyf.get_coin()
    print(start_coin)
    date_and_time=list(Close.index)
    logsr=""
    date=[]
    for d_and_t in date_and_time:
        if d_and_t.split(" ")[0] not in date:
            date.append(d_and_t.split(" ")[0])
    every_day=[]
    every_day_value=[]
    adict={}
    
    
    
    atimelist=[]
    acoinlist=[]
    atotalvaluelist=[]
    avaluelist=[]
    aearnlist=[]
    aearnpercentlist=[]
    
    for d in Close.loc["2023-09-06"+' 9:31:00':date[-1]+' 15:00:00',:].index:#每一分钟,第一天和最后一天丢了问题也不大，
        #反正第一天没有往前数据给你推,最后一天没有最后一天的下一天的close 价格
        
        
        if d.split(" ")[1]=="14:40:00":#只是预筛选
            starttime = datetime.datetime.now()
            max10_stkcode=signal(para1,para2,d,Close.columns,"14:40:00",cyf,Open,High,Low,Close)#time=14:40:00 stkcode_list=Close.columns
            endtime = datetime.datetime.now()
            print ("2:40 产生信号时间",(endtime - starttime).seconds)
            stop_lost(d,cyf,Close,Open)
        
        if d.split(" ")[1]=="14:50:00":
            starttime = datetime.datetime.now()
            max10_stkcode1=signal(para1,para2,d,max10_stkcode,"14:50:00",cyf,Open,High,Low,Close)#time=14:40:00 stkcode_list=Close.columns
            endtime = datetime.datetime.now()
            print ("2:50 产生信号时间",(endtime - starttime).seconds)
            
            
            #print("处理完涨跌停之前",max10_stkcode1)
            #需要在max10_srkcode1里处理账套跌停
            #for stock_code in max10_stkcode1:#想了下 跌停不需要删去 因为跌停不影响买入 而今天的信号主要是想要买入 
                #那既在今天信号又在昨天信号呢？？？
                #open_time=d.split(" ")[0]+" 09:31:00"
                #if (get_price(stock_code,d)-get_price(stock_code,open_time))/get_price(stock_code,open_time)>=0.1:#涨停无法买入可卖出
                  #  max10_stkcode1.remove(stock_code)
                   # print(stock_code+"涨!!!!!!!!!!!!!!!!!!!!")
        #return "涨停"
                #elif (get_price(stock_code,d)-get_price(stock_code,open_time))/get_price(stock_code,open_time)<=-0.1:#跌停无法卖出但能买入
                    #max10_stkcode1.remove(stock_code)
                    #print(stock_code+"跌!!!!!!!!!!!!!!!!!!!!")
        #return "跌停"
            
            #print("处理完涨跌停之后",max10_stkcode1)
            
            
            
            
            print("昨天的信号",adict)
            starttime = datetime.datetime.now()
            print("14:50:00 (before order of today)  coin:"+str(cyf.get_coin()))
            
            for hij in adict.keys():#在昨天的信号里
                if hij not in max10_stkcode1:#不在今天的信号里
                    print("卖"+hij)
                    #last_price = get_current_data(hij).last_price			# 获取交易当日当前价格
                
                    sell=order_sell(cyf,hij,d,0.0002 ,0.001,cyf.stock[hij],0.05,Close)#卖完
                    print(sell)
                    
                    
                    
                    
                    
                   
                    
                    
                    
            
            
            
            num=len(max10_stkcode1)#今天的信号里有多少只股票
            total_value=get_total_value_in_a_monnt(cyf,d,0.0002 ,0.001,Close)#总价值 包括资金和股票价值 考虑下卖出的税的问题！！！！！偏差！！！
            

            if num>=3:#今天有信号 超过3只开仓
                a_stkcode_value=total_value/num#今天信号里每只股票该有的价值
                #先卖后买啊
                print("单只股票的价值该是",a_stkcode_value)
                for abc1 in max10_stkcode1:#在今天的信号里
                    if abc1 in adict.keys():#在昨天的信号里
                        
                        last_price1 = get_price(abc1,d,Close)
                       
                        target_amount = math.floor(a_stkcode_value/ (last_price1+0.05)/(1+0.001+0.0002) / 100) * 100#昨天的该买或卖到多少股
                        
                        
                    
                        if target_amount<cyf.get_stock(abc1):#当前股数大于目标股数
                            print(d,target_amount)
                            print(abc1+"即在昨天的信号里也在今天的信号里, 单价是",last_price1)
                            print("卖"+abc1)
                            order_amount1=cyf.get_stock(abc1)-target_amount
                            sell=order_sell(cyf,abc1,d,0.0002 ,0.001,order_amount1,0.05,Close)#卖多出的股
                            print(sell)
                            
                for abc2 in max10_stkcode1:#在今天的信号里
                    if abc2 in adict.keys():#在昨天的信号里
                        
                        last_price2 = get_price(abc2,d,Close)
                        
                        target_amount = math.floor(a_stkcode_value/ (last_price2+0.05)/(1+0.0002) / 100) * 100#昨天的该买或卖到多少股
                        
                        
                        if target_amount>=cyf.get_stock(abc2) and get_price(abc2,d,Close)>get_today_open_price(abc2,d,Open):
                            #目标股数大于当前股数
                            print(d,target_amount)
                            print(abc2+"即在昨天的信号里也在今天的信号里, 单价是",last_price2)
                            print(str(cyf.get_coin()))
                            print("买"+abc2)
                            order_amount2=target_amount-cyf.get_stock(abc2)
                            buy=order_buy(cyf,abc2,d,order_amount2,0.0002,0.05,Close) 
                            print(buy)
                            
                for abc in max10_stkcode1:#在今天的信号里
                    if abc not in adict.keys() and get_price(abc,d,Close)>get_today_open_price(abc,d,Open):#不在昨天的信号里
                        print(str(cyf.get_coin()))
                        print("买"+abc)
                        last_price = get_price(abc,d,Close)# 获取交易当日当前价格
                        print("单价",last_price)
                    
                        order_amount = math.floor(a_stkcode_value/ (last_price+0.05)/(1+0.001) / 100) * 100
                        print(d,order_amount)
                        # 计算买入股票的数量， 为100的整数倍,滑点

                        buy=order_buy(cyf,abc,d,order_amount,0.0002,0.05,Close) 
                        #用order函数下单， 买卖一定数量股票， order_amount为正数买入，负数卖出
                        print(buy)
                        
            
            
            print("昨天的交易结果",adict)
            
            for key1 in max10_stkcode1:
                adict[key1]=cyf.get_stock(key1)#存一下今天的符合条件的最大10只股票给明天用
                
                
            for key2 in adict.keys():#把所有买过股票更新一下 避免第一天买入 第二天跌停卖不出的情况（第三天接着卖）
                adict[key2]=cyf.get_stock(key2)#改了之后 有很多0股票 之后卖了也白卖
            
            dellist=[]
            for key3 in adict.keys():
                if adict[key3]==0:
                    dellist.append(key3)
                    
            for item in dellist:
                adict.pop(item)
            print("今天的交易结果",adict)
            print("14:50:00 (after buy or sell)  coin:"+str(cyf.get_coin()))
            print("\n")
            every_day.append(d.split(" ")[0])
            every_day_value.append(get_total_value_every_day(cyf,d,0.0002 ,0.001,Close)/10000000)
            endtime = datetime.datetime.now()
            print ("2:50 交易时间",(endtime - starttime).seconds)
            
            stop_lost(d,cyf,Close,Open)
            atimelist.append(d)
            acoinlist.append(cyf.get_coin())
            atotalvaluelist.append(get_total_value_every_day(cyf,d,0.0002 ,0.001,Close)/start_coin)
            avaluelist.append(get_total_value_every_day(cyf,d,0.0002 ,0.001,Close)-cyf.get_coin())
            aearnlist.append(get_total_value_every_day(cyf,d,0.0002 ,0.001,Close)-start_coin)
            aearnpercentlist.append((get_total_value_every_day(cyf,d,0.0002 ,0.001,Close)-start_coin)/start_coin*100)
            
            print("时间",d)
            print("现金",cyf.get_coin())
            print("净值",get_total_value_every_day(cyf,d,0.0002 ,0.001,Close)/start_coin)
            print("市值",get_total_value_every_day(cyf,d,0.0002 ,0.001,Close)-cyf.get_coin())
            print("盈亏",get_total_value_every_day(cyf,d,0.0002 ,0.001,Close)-start_coin)
            print("盈亏百分比",(get_total_value_every_day(cyf,d,0.0002 ,0.001,Close)-start_coin)/start_coin*100)
            logsr=logsr+"时间: "+str(d)+"\n"
            logsr=logsr+"现金: "+str(cyf.get_coin())+"\n"
            logsr=logsr+"净值: "+str(get_total_value_every_day(cyf,d,0.0002 ,0.001,Close)/start_coin)+"\n"
            logsr=logsr+"市值: "+str(get_total_value_every_day(cyf,d,0.0002 ,0.001,Close)-cyf.get_coin())+"\n"
            logsr=logsr+"盈亏: "+str(get_total_value_every_day(cyf,d,0.0002 ,0.001,Close)-start_coin)+"\n"
            logsr=logsr+"盈亏百分比: "+str((get_total_value_every_day(cyf,d,0.0002 ,0.001,Close)-start_coin)/start_coin*100)+"\n"
        elif d.split(" ")[1]<"14:50:00":#T+1的交易规则
            stop_lost(d,cyf,Close,Open)
            continue
        else:
            continue
    result={"时间":atimelist,"现金":acoinlist,"净值":atotalvaluelist,"市值":avaluelist,"盈亏":aearnlist,"盈亏百分比":aearnpercentlist}    
    result=pd.DataFrame(result)   
    print(result)   
       
    df=pd.DataFrame(every_day_value,every_day)
    df.columns=["earn"]
    df.plot()
        
    end_coin=cyf.get_coin()    
    stock_value=0
    universe=list(Close.columns)[0:len(Close.columns)]
    
    for jjj in range(len(universe)):#对于每一只股票
        if cyf.get_stock(universe[jjj])!=0:#股票数量不为0
            stock_value=stock_value+get_price(universe[jjj],Close.loc[date[0]+' 9:31:00':date[-1]+' 15:00:00',:].index[-1],Close)\
            *cyf.get_stock(universe[jjj])#当分钟股票开盘价*股票数量    
    earn=stock_value+end_coin-start_coin
    #print(stock_value(cyf))
    print(earn)
    return df,result
