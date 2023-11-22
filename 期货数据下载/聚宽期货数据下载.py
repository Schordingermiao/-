from jqdatasdk import *
auth('账号','密码')

import pandas as pd
import time
import numpy as np
import os

#按照白银期货的时间下载所有商品期货的数据
def aaa(type):
    data_futures=get_all_securities(types=['futures'], date=None)
    unique_class=[]
    for item in data_futures.index:
        name=item[:-9]+"9999"+item[-5:-1]+item[-1]
        if name not in unique_class:
            unique_class.append(name)
            
            
    unique_class.remove("IF9999.CCFX")
    unique_class.remove("TF9999.CCFX")
    unique_class.remove("T9999.CCFX")
    unique_class.remove("IC9999.CCFX")
    unique_class.remove("IH9999.CCFX")
    unique_class.remove("TS9999.CCFX")
    unique_class.remove("IM9999.CCFX")
    unique_class.remove("TL9999.CCFX")

   
    Ticks = unique_class
    SD = str(datetime.datetime.now()+datetime.timedelta(days=-365*2)).split()[0]
    ED = str(datetime.datetime.now().date())
    dfs = get_price('AG9999.XSGE', start_date = SD, end_date=ED, frequency='1m', fields= 'volume', fq='none')
    

    
    print('num of futures ' + str(len(Ticks)))

    c=0
    start = time.time()
    df = pd.DataFrame(np.nan, index = dfs.index, columns = list(Ticks))
    df.shape
    for t in Ticks[0:len(Ticks)]:
        try:
            dfu = get_price(t, start_date = SD, end_date=ED, frequency='1m',  fields=type, fq='none') 
            df.loc[dfu.index, t] = dfu[type]
        
        except:
            pass
        c = c + 1
        if c%50==0:
            print(c)
    end = time.time()
    print(end-start)

    today=str(datetime.datetime.now()).split(" ")[0]   
    if not os.path.exists(today):
                os.makedirs(today)
    df.to_csv(today+'/Afutures'+type+'1m.csv')
    print('file saved')



#一共6种分钟线数据
def generate_today_futures():
    typelist=["open","high","low","close","volume","money"]
    for type in typelist:
        aaa(type)
