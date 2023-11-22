#无奈之下的阻止曲线拟合报错的方法
import  scipy.signal.signaltools

def _centered(arr, newsize):
    # Return the center newsize portion of the array.
    newsize = np.asarray(newsize)
    currsize = np.array(arr.shape)
    startind = (currsize - newsize) // 2
    endind = startind + newsize
    myslice = [slice(startind[k], endind[k]) for k in range(len(endind))]
    return arr[tuple(myslice)]

scipy.signal.signaltools._centered = _centered


import numpy as np 
from scipy.signal._signaltools import _centered
import statsmodels.api as sm

#预测某只股票的算法
def tslopex(Open, High, Low, Close, tick, d, L,final_min):
    
    open_ridx = np.where(Open.index==d.split(" ")[0]+" 09:31:00")[0][0]#每日开盘价
    close_ridx=np.where(Close.index==d.split(" ")[0]+" 15:00:00")[0][0]#每日收盘价
    tick_index=Close.columns.get_loc(tick)
    #print(tick_index)
    x=[]
    y=[]
    
    ds0 = Close.index[close_ridx-L*240+240]
    if ds0<d:
        #print(ds0)
        #print(Close.loc[ds0,[tick]])#基准是哪一天
        #print("aaaaaa")
    
    
        for i in range(L-1):#L=5 0 1 2 3 
            ds_close = Close.index[close_ridx+(-L+i+1)*240]#循环中收盘
        
            ds_open=Open.index[open_ridx+(-L+i+1)*240]#循环中开盘
        
            #print("close\n")
            #print(Close.loc[ds_close,[tick]])
            #print("open\n")
            #print(Open.loc[ds_open,[tick]])
            #print("-----")
        
            x.append(i)
            x.append(i)
            x.append(i)
            x.append(i)
            y.append(Open.at[ds_open,tick]/Close.at[ds0, tick])
        
            #print("high\n")
            #print(High.iloc[open_ridx+(-L+1+i)*240:close_ridx+(-L+1+i)*240+1, tick_index])
        
            Max_High=max(High.iloc[open_ridx+(-L+1+i)*240:close_ridx+(-L+1+i)*240+1, tick_index].values)#一天最高
            y.append(Max_High/Close.at[ds0, tick])
        
            #print("low\n")
            #print(Low.iloc[open_ridx+(-L+1+i)*240:close_ridx+(-L+1+i)*240+1, tick_index])
        
            Min_Low=min(Low.iloc[open_ridx+(-L+1+i)*240:close_ridx+(-L+1+i)*240+1, tick_index].values)#一天最低
            y.append(Min_Low/Close.at[ds0, tick])
        
            y.append(Close.at[ds_close, tick]/Close.at[ds0, tick])
    
        #最后一天拿2点40 填充close！！！！！！！！！！！ 4
        x.append(L-1)
        x.append(L-1)
        x.append(L-1)
        x.append(L-1)
    
        ds_open=Open.index[open_ridx+(-L+(L-1)+1)*240]
        y.append(Open.at[ds_open,tick]/Close.at[ds0, tick])
    
        #print(Open.loc[ds_open,[tick]])
        #print("high\n")
        #print(High.iloc[open_ridx+(-L+1+(L-1))*240:close_ridx+(-L+1+(L-1))*240+1-final_min, tick_index])
        #print(High.iloc[open_ridx+(-L+1+(L-1))*240:close_ridx+(-L+1+(L-1))*240+1-final_min, tick_index])
        Max_High=max(High.iloc[open_ridx+(-L+1+(L-1))*240:close_ridx+(-L+1+(L-1))*240+1-final_min, tick_index].values)#一天最高
        y.append(Max_High/Close.at[ds0, tick])
    
        #print("low\n")
        #print(Low.iloc[open_ridx+(-L+1+(L-1))*240:close_ridx+(-L+1+(L-1))*240+1-final_min, tick_index])
    
        Min_Low=min(Low.iloc[open_ridx+(-L+1+(L-1))*240:close_ridx+(-L+1+(L-1))*240+1-final_min, tick_index].values)#一天最低
        y.append(Min_Low/Close.at[ds0, tick])
     
       
        ds_close1 = Close.index[close_ridx+(-L+(L-1)+1)*240-final_min]#循环中收盘
        #print(Close.loc[ds_close1,[tick]])
        y.append(Close.at[ds_close1, tick]/Close.at[ds0, tick])
    
        x=np.array(x)
        y=np.array(y)   
        x = sm.add_constant(x)
        ols_model = sm.OLS(y, x) 
        results = ols_model.fit()
        if abs(results.params[1])>0 and results.rsquared>0:#边缘情况 不然7月3日（前3天）往前5天是7月26日不合理:
            return results.params[1], results.rsquared 
        else:
            return 0,0
    else:
        return 0,0