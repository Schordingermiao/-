import pandas as pd
import numpy as np

from algorithm import tslopex
    
#产生信号
import os
def signal(para1,para2,d,stkcode_list,time,cyf,Open,High,Low,Close,Volume):#time=14:40:00 stkcode_list=Close.columns 目前只有做多

    #print(cyf.get_coin())
    if time=="14:40:00":
        final_min=20
    elif time=="14:50:00":
        final_min=10
    
    c=0
    tem_dict={}
    for t in stkcode_list:#收盘价，每一只股票吧
             
      
            idx = np.where(Close.index==d)[0][0]
        #每日收盘价，7月11日,减个20到14:40
            y_close = Close.at[Close.index[idx-240+final_min], t] #昨天收盘价，7月10日
            yy_close=Close.at[Close.index[idx-240*2+final_min],t]
            yyy_close=Close.at[Close.index[idx-240*3+final_min],t]

            if yyy_close<yy_close<y_close:
                 tem_dict[t]=Volume.at[Volume.index[idx-240+final_min], t]
    bdict_sorted=sorted(tem_dict.items(),key=lambda kv:kv[1],reverse=False)#按2:50收盘价排序  
    max10=bdict_sorted[:10]#最大10只 list来的
    #print(max10)
    #result=pd.DataFrame(bdict_sorted,columns=['stock_code', 'open'])
    #result.to_csv("max10_result.csv")     
        
    max10_stkcode=[]#净值最大的10只的股票代码
    for key in max10:
        max10_stkcode.append(key[0])
        
    print("today is "+d.split(" ")[0]+", follow are logs")
    print("\n")
    print("信号识别到",max10_stkcode)
    
    print(time+"   coin:"+str(cyf.get_coin()))
    return max10_stkcode#time=14:40:00