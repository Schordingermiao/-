import math


def generate_close_and_obv(d,tick,L,Open,High,Low,Close,Volume,Open_day,High_day,Low_day,Close_day,Volume_day):
    obv=[0]*L
    volume=[0]*L
    close_price=[0]*L
    high_price=[0]*L
    close_ridx=np.where(Close_day.index==d.split(" ")[0])[0][0]
    first_day=Close_day.index[close_ridx-L+1]
    #print(first_day)
    close_price[0]=Close_day.loc[first_day,tick]
    high_price[0]=High_day.loc[first_day,tick]
    volume[0]=Volume_day.loc[first_day,tick]
    obv[0]=Volume_day.loc[first_day,tick]
    for i in range(1,L-1):
        day_index=Close_day.index[close_ridx-L+1+i]
        close_price[i]=Close_day.loc[day_index,tick]
        high_price[i]=High_day.loc[day_index,tick]
        volume[i]=Volume_day.loc[day_index,tick]
        if close_price[i]>close_price[i-1]:
            a=1
        elif close_price[i]<close_price[i-1]:
            a=-1
        elif close_price[i]==close_price[i-1]:
            a=0
        obv[i]=obv[i-1]+a*volume[i]
    
    
    #对于最后一天，还没有收盘！！！
    open_ridx=np.where(Close.index==d.split(" ")[0]+" 09:31:00")[0][0]
    close_ridx=np.where(Close.index==d.split(" ")[0]+" 14:50:00")[0][0]
    last_day_open=Open.index[open_ridx]
    last_day_last=Close.index[close_ridx]
    close_price[-1]=Close.loc[last_day_last,tick]
    high_price[-1]=max(High.loc[last_day_open:last_day_last,tick])
    volume[-1]=math.floor(sum(Volume.loc[last_day_open:last_day_last,tick])*24/23)#因为最后一天只有230根bar
    if close_price[-1]>close_price[-2]:
        a=1
    elif close_price[-1]<close_price[-2]:
        a=-1
    elif close_price[-1]==close_price[-2]:
        a=0
    obv[-1]=obv[-2]+a*volume[-1]
    return high_price,obv

import numpy as np

import  scipy.signal.signaltools
from scipy.signal._signaltools import _centered
import statsmodels.api as sm

def _centered(arr, newsize):
    # Return the center newsize portion of the array.
    newsize = np.asarray(newsize)
    currsize = np.array(arr.shape)
    startind = (currsize - newsize) // 2
    endind = startind + newsize
    myslice = [slice(startind[k], endind[k]) for k in range(len(endind))]
    return arr[tuple(myslice)]

scipy.signal.signaltools._centered = _centered


def trend(d,tick,L):
    x=np.array(list(range(L)))
    high_y,obv_y=generate_close_and_obv(d,tick,L)
    high_y=np.array(high_y/high_y[0])  
    obv_y=np.array(obv_y/obv_y[0]) 
    x = sm.add_constant(x)
    ols_model_high = sm.OLS(high_y, x) 
    ols_model_obv = sm.OLS(obv_y, x) 
    results_high = ols_model_high.fit()
    results_obv = ols_model_obv.fit()
        
    return results_high.params[1], results_obv.params[1]
