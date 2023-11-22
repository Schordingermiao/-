import pandas as pd
import numpy as np

from algorithm import tslopex
    
#产生信号
import os
def signal(para1,para2,d,stkcode_list,time,cyf,Open,High,Low,Close):#time=14:40:00 stkcode_list=Close.columns 目前只有做多

    #print(cyf.get_coin())
    if time=="14:40:00":
        final_min=20
    elif time=="14:50:00":
        final_min=10
    
    c=0
    tem_dict={}
    for t in stkcode_list:#收盘价，每一只股票吧
             
      
            idx = np.where(Close.index==d.split(" ")[0]+" 15:00:00")[0][0]-final_min
        #每日收盘价，7月11日,减个20到14:40
            ndstr = Close.index[idx-240] #昨天收盘价，7月10日
            regs =np.ndarray([8,2])#8行两列
            ls =[]
            w =[]
            #逻辑：l=5,用7月4日到7月10日数据输出模型
            for l in range(3,11):#3到10,前3天数据算一下
                regs[l-3,0], regs[l-3,1]=tslopex(Open, High, Low, Close, t, d, l,final_min)#包括7月11日
                #l=5,7月5日到7月11日(只有交易日)
                ls.append(str(l)+'d')
                w.append(l)
            
            regs = pd.DataFrame(regs)#模型结果塞进去
            regs.columns=['slope', 'rsqr'] 
            regs['w'] = w    
            regs['p']= regs['slope']*regs['rsqr']
            regs = regs.sort_values(by ='rsqr', ascending = False)#最大的
            regs.index = range(len(regs))
            c+=1
            
            if not os.path.exists("./regs/"+str(para1)+"-"+str(para2)+"regs"):
                os.makedirs("./regs/"+str(para1)+"-"+str(para2)+"regs")
            regs.to_csv("./regs/"+str(para1)+"-"+str(para2)+"regs/"+str(para1)+"_"+str(para2)\
                        +"_regs_"+d.split(" ")[0]+"_"+time.split(":")[0]+"_"+time.split(":")[1]+t+".csv")
        

            if regs.iat[0, 1]>para1 and regs.iat[0,0]>para2 and  Close.at[d, t]/Close.at[ndstr, t]>0:#今天14：50除以昨天
                #斜率和r方 0.9 0.02
                #print(regs)
                tem_dict[t]=regs.iat[0,1]#相关性排序
        
    bdict_sorted=sorted(tem_dict.items(),key=lambda kv:kv[1],reverse=True)#按2:50收盘价排序  
    max10=bdict_sorted[0:10]#最大10只 list来的
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