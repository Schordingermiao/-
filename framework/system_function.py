

#获取某分钟的收盘价
def get_price(stock_code,time,Close):
    return Close.loc[time,stock_code]

#获取当天开盘价
def get_today_open_price(stock_code,time,Open):
    return Open.loc[time.split(" ")[0]+' 09:31:00',stock_code]

#股票买入
def order_buy(account,stock_code,time,amount,fee,huadian,Close):

    open_time=time.split(" ")[0]+" 09:31:00"
    

    
    today_close_index=np.where(Close.index==time.split(" ")[0]+" 15:00:00")[0][0]
    yesterday_close_index=today_close_index-240
    yesterday_close_d=Close.index[yesterday_close_index]
    
    
    if (get_price(stock_code,time,Close)-get_price(stock_code,yesterday_close_d,Close))/get_price(stock_code,yesterday_close_d,Close)>=0.1:
        #涨停无法买入可卖出
        return "涨停"
    else:
        single_price=get_price(stock_code,time,Close)+huadian
    
        #print(single_price)
    
        total_price0=single_price*amount
        #print(total_price0)
        total_price=total_price0*(1+fee)
        #print(total_price)
    
        #print(account.get_coin())
        #print(account.get_coin()>=total_price)
        if account.get_coin()>=total_price:#这个if条件语句有个意想不到的收获，解决了股票数据nan的问题，反正都是false 不会交易
            account.update_coin(account.get_coin()-total_price)
            account.update_stock(stock_code,account.stock[stock_code]+amount)
            return "Aoocunt coin: "+str(account.get_coin())+"\n"+stock_code+":"+str(account.stock[stock_code])+"\n"\
                    +"股票"+stock_code+"的数量为: "+str(account.stock[stock_code])+'\n'
        else:
            return "no money don't touch! \n Aoocunt coin:"+str(account.get_coin())
        
#股票卖出
def order_sell(account,stock_code,time,fee,tax,sell_amount,huadian,Close):#fee 卖出手续费 tax印花税 amount:卖多少股

    open_time=time.split(" ")[0]+" 09:31:00"
    
    today_close_index=np.where(Close.index==time.split(" ")[0]+" 15:00:00")[0][0]
    yesterday_close_index=today_close_index-240
    yesterday_close_d=Close.index[yesterday_close_index]
    
    if (get_price(stock_code,time,Close)-get_price(stock_code,yesterday_close_d,Close))/get_price(stock_code,yesterday_close_d,Close)<=-0.1:
        #跌停无法卖出但能买入
        return "跌停"
    else:
        single_price=get_price(stock_code,time,Close)-huadian
        print(stock_code+"卖之前股数： "+str(account.stock[stock_code]))
        if account.stock[stock_code]>=sell_amount:
            account.update_stock(stock_code,account.stock[stock_code]-sell_amount)
            total_price=single_price*sell_amount
            account.update_coin(account.get_coin()+total_price*(1-fee-tax))
            return "Aoocunt coin: "+str(account.get_coin())+"\n"+stock_code+":"+str(account.stock[stock_code])+"\n"
        else:
            return "no stock to sell! \n "+stock_code+":"+str(account.stock[stock_code])
        
#股票融券
def borrow_stock(account,stock_code,amount,time,Close):#一借出就立马卖掉
    open_time=time.split(" ")[0]+" 09:31:00"
    
    today_close_index=np.where(Close.index==d.split(" ")[0]+" 15:00:00")[0][0]
    yesterday_close_index=today_close_index-240
    yesterday_close_d=Close.index[yesterday_close_index]
    
    if (get_price(stock_code,time,Close)-get_price(stock_code,yesterday_close_d,Close))/get_price(stock_code,yesterday_close_d,Close)<=-0.1:
        #跌停无法卖出但能买入
        print("跌停，融到券也无法卖出，不进行融券")
        return "跌停，融到券也无法卖出，不进行融券"
    else:
        single_price=get_price(stock_code,time,Close)
        total_price=single_price*amount
        if  account.get_credit_stock(stock_code,time) is not None:
        
            account.update_credit_stock(stock_code,time,\
            account.get_credit_stock(stock_code,time)[0]+amount,\
            account.get_credit_stock(stock_code,time)[1]+total_price)#记录借出股票代码 借出时间 借出数量 借出价值金额
        else:
            account.update_credit_stock(stock_code,time,\
            amount,\
            total_price)#记录借出股票代码 借出时间 借出数量 借出价值金额
    
        #print(account.get_credit_stock(stock_code,time))
        #print(account.get_stock(stock_code))
        account.update_stock(stock_code,account.get_stock(stock_code)+amount)#借出的股票更新到持仓上
        #print(account.get_stock(stock_code))
        sell=order_sell(account,stock_code,time,0.0002,0.001,amount,0.05,Close)
        print(sell)
        print("融券成功")
        return "融券成功"
    
#股票还券逻辑
def return_logic(account,stock_code,amount,td,time,Close):#还每个时刻欠的股
    credit_info=account.get_credit_stock(stock_code,td)
    
   
    
    borrow_coin=credit_info[1]#借出的资金
    
    borrow_days=(datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")-\
                 datetime.datetime.strptime(td, "%Y-%m-%d %H:%M:%S")).days#借了多少天
    
    before_return_amount=credit_info[0]#借出股票数量
    
    have_stock=account.get_stock(stock_code)#账户上的股票
    
    
    if have_stock<=before_return_amount<=amount:#先把账户上的股票还了，再买入before_return_amount-have_stock的股票去还！！！！！
        print("账户上的股票数量<=欠的融券数量<=打算还的数量")
        rest_price1=(1-have_stock/before_return_amount)*borrow_coin
        account.update_stock(stock_code,0)
        account.update_credit_stock(stock_code,td,before_return_amount-have_stock,rest_price1)#欠900
        account.update_coin(account.get_coin()-have_stock/before_return_amount*borrow_coin*0.0835*borrow_days/360)
        
        
        
        
        buy=order_buy(account,stock_code,time,before_return_amount-have_stock,0.0002,0.05,Close)#买了指定数量的股票来还
        print(buy)
        
        #如果买成功了
        if "涨停" not in buy and "no money don't touch" not in buy:
            account.update_credit_stock(stock_code,td,0,0)#还40股剩60股
            account.update_stock(stock_code,0)
            account.update_coin(account.get_coin()\
            -(before_return_amount-have_stock)/before_return_amount*borrow_coin*0.0835*borrow_days/360)#还了的比例
            return before_return_amount
        else:
            print("买入失败还不了,只还了账户上的股票")
            return have_stock
     
    
    elif have_stock<=amount<=before_return_amount:#先把账户上的股票还了，再买入amount-have_stock的股票去还！！！！！
        print("账户上的股票数量<=打算还的数量<=欠的融券数量")
        rest_price1=(1-have_stock/before_return_amount)*borrow_coin
        account.update_stock(stock_code,0)
        account.update_credit_stock(stock_code,td,before_return_amount-have_stock,rest_price1)#欠900
        account.update_coin(account.get_coin()-have_stock/before_return_amount*borrow_coin*0.0835*borrow_days/360)
        
        rest_amount=amount-have_stock#还200 剩余打算还的数量
        
        
        buy=order_buy(account,stock_code,time,rest_amount,0.0002,0.05,Close)#买了指定数量的股票来还
        print(buy)
        rest_price=((before_return_amount-amount)/before_return_amount)*borrow_coin
        #如果买成功了
        if "涨停" not in buy and "no money don't touch" not in buy:
            account.update_credit_stock(stock_code,td,before_return_amount-amount,rest_price)#还40股剩60股
            account.update_stock(stock_code,0)
            account.update_coin(account.get_coin()-rest_amount/before_return_amount*borrow_coin*0.0835*borrow_days/360)#还了的比例
            return amount
        else:
            print("买入失败还不了,只还了账户上的股票")
            return have_stock
        
            
    elif before_return_amount<=have_stock<=amount:#直接用账户上的股票还before_return_amount股！！！！！！！
        print("欠的融券数量<=账户上的股票数量<=打算还的数量")    
        account.update_stock(stock_code,have_stock-before_return_amount)
        account.update_credit_stock(stock_code,td,0,0)#欠900
        account.update_coin(account.get_coin()-borrow_coin*0.0835*borrow_days/360)
        return before_return_amount
        

            
    elif before_return_amount<=amount<=have_stock:#直接用账户上的股票还before_return_amount股！！！！！！！
        print("欠的融券数量<=打算还的数量<=账户上的股票数量")   
        account.update_stock(stock_code,have_stock-before_return_amount)
        account.update_credit_stock(stock_code,td,0,0)
        account.update_coin(account.get_coin()-borrow_coin*0.0835*borrow_days/360)
        return before_return_amount
            
    elif amount<=have_stock<=before_return_amount:#直接用账户上的股票还amount股！！！！！！！
        print("打算还的数量<=账户上的股票数量<=欠的融券数量")  
        account.update_stock(stock_code,have_stock-amount)
        account.update_credit_stock(stock_code,td,0,0)
        account.update_coin(account.get_coin()-borrow_coin*0.0835*borrow_days/360)
        return amount
            
    elif amount<=before_return_amount<=have_stock:#直接用账户上的股票还amount股！！！！！！！
        print("打算还的数量<=欠的融券数量<=账户上的股票数量")
        account.update_stock(stock_code,have_stock-amount)
        account.update_credit_stock(stock_code,td,0,0)
        account.update_coin(account.get_coin()-borrow_coin*0.0835*borrow_days/360)
        return amount
    
#股票还券
def return_stock(account,stock_code,amount,time,Close):
    borrow_time_list=[]
    for d in account.credit_stock[stock_code].keys():
        if account.get_credit_stock(stock_code,d)[0]!=0:
            borrow_time_list.append(d)#找到所有有借出记录的日期，按最早借的日期排序
            
            
            
    for td in borrow_time_list:
        rest_need_return_amount=return_logic(account,stock_code,amount,td,time,Close)
        amount=amount-rest_need_return_amount
      
#股票收益
def earn_coin(start_coin,end_coin):
    return start_coin-end_coin

#股票收益率
def earn_rate(start_coin,end_coin):
    return (end_coin-start_coin)/start_coin

#账户资金加股票价值
def get_total_value(cyf,Close):
    end_coin=cyf.get_coin()    
    stock_value=0
    universe=list(Close.columns)[0:len(Close.columns)]
    date_and_time=list(Close.index)
    date=[]
    
    for d_and_t in date_and_time:
        if d_and_t.split(" ")[0] not in date:
            date.append(d_and_t.split(" ")[0])
            
    for jjj in range(len(universe)):#对于每一只股票
        if cyf.get_stock(universe[jjj])!=0:#股票数量不为0
            stock_value=stock_value+get_price(universe[jjj],Close.loc[date[0]+' 9:31:00':date[-1]+' 15:00:00',:].index[-1],Close)\
            *cyf.get_stock(universe[jjj])#当分钟股票开盘价*股票数量 
    total_value=end_coin+stock_value
    return total_value

#账户资金加上能卖出的股票价值
def get_total_value_in_a_monnt(cyf,d,fee,tax,Close):
    end_coin=cyf.get_coin() #当前时刻账户上的资金   
    stock_value=0
    universe=list(Close.columns)[0:len(Close.columns)]
    open_time=d.split(" ")[0]+" 09:31:00"
    
    
    today_close_index=np.where(Close.index==d.split(" ")[0]+" 15:00:00")[0][0]
    yesterday_close_index=today_close_index-240
    yesterday_close_d=Close.index[yesterday_close_index]
    
    
    for stock_code in universe:
        if (get_price(stock_code,d,Close)-get_price(stock_code,yesterday_close_d,Close))/get_price(stock_code,yesterday_close_d,Close)<=-0.1:
            universe.remove(stock_code)
            print(stock_code+"跌停!!!!!!!!!!!!!!!!!!!!")
  
            
    for jjj in range(len(universe)):#对于每一只股票
        if cyf.get_stock(universe[jjj])!=0:#股票数量不为0
            stock_value=stock_value+get_price(universe[jjj],d,Close)\
            *cyf.get_stock(universe[jjj])#当分钟股票开盘价*股票数量 
    total_value=end_coin+stock_value*(1-fee-tax)
    print("账户资金",end_coin)
    print("股票价值",stock_value*(1-fee-tax))
    
    return total_value

#账户资金加上股票价值
def get_total_value_every_day(cyf,d,fee,tax,Close):
    end_coin=cyf.get_coin() #当前时刻账户上的资金   
    stock_value=0
    universe=list(Close.columns)[0:len(Close.columns)]
    open_time=d.split(" ")[0]+" 09:31:00"
   
  
            
    for jjj in range(len(universe)):#对于每一只股票
        if cyf.get_stock(universe[jjj])!=0:#股票数量不为0
            stock_value=stock_value+get_price(universe[jjj],d,Close)\
            *cyf.get_stock(universe[jjj])#当分钟股票开盘价*股票数量 
    total_value=end_coin+stock_value*(1-fee-tax)
    print("账户资金",end_coin)
    print("股票价值",stock_value*(1-fee-tax))
    return total_value

#股票止损
def stop_lost(d,account,Close,Open):
    universe=list(Close.columns)[0:len(Close.columns)]
    for jjj in range(len(universe)):#对于每一只股票
        if account.get_stock(universe[jjj])!=0:#股票数量不为0
            if get_price(universe[jjj],d,Close)<get_today_open_price(universe[jjj],d,Open)*(1-0.03):#比开盘价少百分3
                print("触发单只股票的风险预警"+universe[jjj])
                sell=order_sell(account,universe[jjj],d,0.0002 ,0.001,account.stock[universe[jjj]],0.05,Close)#卖完
                print(sell)
                
                
                
                
                
                
                
                
#期货
import numpy as np




#期货计算昨天结算价
def get_futures_ysterday_jie_suan_price(futures_code,time,Close,Volume):
    bussiness=["IF9999.CCFX","TF9999.CCFX","T9999.CCFX","IC9999.CCFX","IH9999.CCFX","TS9999.CCFX","IM9999.CCFX","TL9999.CCFX"]
    #按照黄金开盘收盘时间生成的数据，一天555条数据
    if futures_code not in bussiness:
        #对于商品期货
        if "09:01:00"<=time.split(" ")[1]<="23:59:00":#在同一天
            yesterday_close_index=np.where(Close.index==time.split(" ")[0]+" 02:30:00")[0][0]
            today_open_index=np.where(Close.index==time.split(" ")[0]+" 09:01:00")[0][0]
        
            yesterday_open_index=today_open_index-555
        else:#不在同一天   00:00:00-02:30:00
            today_0_index=np.where(Close.index==time.split(" ")[0]+" 00:00:00")[0][0]
            yesterday_close_index=today_0_index-405
           
            
            
            
            yesterday_open_index=today_0_index-555-404
            
            
        
        yesterday_close_d=Close.index[yesterday_close_index]
        yesterday_open_d=Close.index[yesterday_open_index]
        #print(Close.index[yesterday_close_index])
        #print(Close.index[yesterday_open_index])
        
        yesterday_jie_suan_price=sum(np.array(Volume.loc[yesterday_open_d:yesterday_close_d,[futures_code]].dropna())*\
        np.array(Close.loc[yesterday_open_d:yesterday_close_d,[futures_code]].dropna()))\
        /sum(np.array(Volume.loc[yesterday_open_d:yesterday_close_d,[futures_code]].dropna()))
        
        return float(yesterday_jie_suan_price)
    
   

#期货买入
def order_buy_futures(account,futures_code,time,amount,huadian,Close,Volume):
    fee_dict={'AG': 0.50/100/100,'AL': 3/100/100,'AU': 10/100/100,'BU': 1.00/100/100,'CU': 0.50/100/100,'FU': 0.10/100/100,
              'HC': 1.00/100/100,'NI': 3/100/100,'PB': 0.40/100/100,'RB': 1.00/100/100,'RU': 3.00/100/100,'SN': 3/100/100,
              'WR': 0.40/100/100,'ZN': 3/100/100,'SP': 0.50/100/100,'SS': 2/100/100,'A': 2/100/100,'B': 1/100/100,
              'BB': 1.00/100/100,'C': 2/100/100,'CS': 1.5/100/100,'FB': 1.00/100/100,'I': 1.00/100/100,'J': 1.00/100/100,
              'JD': 1.50/100/100,'JM': 1.00/100/100,'L': 1/100/100,'M': 1.5/100/100,'P': 2.5/100/100,'PP': 1/100/100,
              'V': 1/100/100,'Y': 2.5/100/100,'EG': 3/100/100,'RR': 1/100/100,'EB': 3/100/100,'PG': 6/100/100,
              'LH': 1.00/100/100,'AP': 5/100/100,'CF': 4.3/100/100,'CY': 4/100/100,'FG': 6/100/100,'JR': 3/100/100,
              'LR': 3/100/100,'MA': 1.00/100/100,'OI': 2/100/100,'PM': 30/100/100,'RI': 2.5/100/100,'RM': 1.5/100/100,
              'RS': 2/100/100,'SF': 3/100/100,'SM': 3/100/100,'SR': 3/100/100,'TA': 3/100/100,'WH': 30/100/100,
              'ZC': 150/100/100,'UR': 1.00/100/100,'PF': 3/100/100,'PK': 4/100/100,'SA': 3.5/100/100,'IC': 0.23/100/100,
              'IF': 0.23/100/100,'IH': 0.23/100/100,'IM': 0.23/100/100,'T': 3/100/100,'TF': 3/100/100,'TL': 3/100/100,
              'TS': 3/100/100,'BC': 0.10/100/100,'LU': 0.10/100/100,'NR': 0.20/100/100,'SC': 20/100/100}
    #涨跌幅限制，就不考虑第一涨停，第二天又涨停，第三天又涨停的限制了
    earn_lost_stop_normal=\
{'AG': 9.0/100,
 'AL': 7.0/100,
 'AU': 7.0/100,
 'BU': 10.0/100,
 'CU': 7.0/100,
 'FU': 13.0/100,
 'HC': 11.0/100,
 'NI': 10.0/100,
 'PB': 7.0/100,
 'RB': 11.0/100,
 'RU': 8.0/100,
 'SN': 12.0/100,
 'WR': 11.0/100,
 'ZN': 7.0/100,
 'SP': 8.0/100,
 'SS': 8.0/100,
 'A': 6.0/100,
 'B': 6.0/100,
 'BB': 5.0/100,
 'C': 6.0/100,
 'CS': 5.0/100,
 'FB': 5.0/100,
 'I': 11.0/100,
 'J': 15.0/100,
 'JD': 6.0/100,
 'JM': 15.0/100,
 'L': 6.0/100,
 'M': 6.0/100,
 'P': 7.0/100,
 'PP': 6.0/100,
 'V': 6.0/100,
 'Y': 6.0/100,
 'EG': 7.0/100,
 'RR': 5.0/100,
 'EB': 7.0/100,
 'PG': 7.0/100,
 'LH': 8.0/100,
 'AP': 9.0/100,
 'CF': 6.0/100,
 'CY': 6.0/100,
 'FG': 8.0/100,
 'JR': 7.0/100,
 'LR': 7.0/100,
 'MA': 7.0/100,
 'OI': 8.0/100,
 'PM': 7.0/100,
 'RI': 7.0/100,
 'RM': 8.0/100,
 'RS': 10.0/100,
 'SF': 10.0/100,
 'SM': 10.0/100,
 'SR': 8.0/100,
 'TA': 6.0/100,
 'WH': 7.0/100,
 'ZC': 10.0/100,
 'UR': 7.0/100,
 'PF': 7.0/100,
 'PK': 7.0/100,
 'SA': 8.0/100,
 'IC': 10.0/100,
 'IF': 10.0/100,
 'IH': 10.0/100,
 'IM': 10.0/100,
 'T': 2.0/100,
 'TF': 1.2/100,
 'TL': 10000000.0/100,
 'TS': 0.5/100,
 'BC': 7.0/100,
 'LU': 10.0/100,
 'NR': 8.0/100,
 'SC': 13.0/100}
    #只单边收费
    only_sell=['AU', 'FU', 'PB', 'RU', 'WR', 'ZN', 'SP', 'SS', 'CF', 'CY', 'SF', 'SM', 'SR', 'TA', 'T', 'TF', 'TL', 'TS', 'BC', 'NR', 'SC']
    futures_type=futures_code.split(".")[0].replace("9999","")
    if futures_type in only_sell:
        fee=0
    else:
        if futures_type in fee_dict.keys():
            fee=fee_dict[futures_type]
        else:
            fee=0
    
 
    
    
    if futures_type in earn_lost_stop_normal and\
    (get_price(futures_code,time,Close)-get_futures_ysterday_jie_suan_price(futures_code,time,Close,Volume))/\
    get_futures_ysterday_jie_suan_price(futures_code,time,Close,Volume)>=earn_lost_stop_normal[futures_type]:
        #涨停无法买入可卖出
        return "涨停"
    else:
        single_price=get_price(futures_code,time,Close)+huadian
    
        #print(single_price)
    
        total_price0=single_price*amount
        #print(total_price0)
        total_price=total_price0*(1+fee)
        #print(total_price)
    
        #print(account.get_coin())
        #print(account.get_coin()>=total_price)
        if account.get_coin()>=total_price:#这个if条件语句有个意想不到的收获，解决了股票数据nan的问题，反正都是false 不会交易
            account.update_coin(account.get_coin()-total_price)
            account.update_futures(futures_code,amount,time)
            return "Aoocunt coin: "+str(account.get_coin())+"\n"+futures_code+":"+str(get_futures_amount(account,futures_code))+'\n'
        else:
            return "no money don't touch! \n Aoocunt coin:"+str(account.get_coin())
#获取账户上某只期货的数量        
def get_futures_amount(account,futures_code):
    a_future=account.futures[futures_code]
    total_amount=0
    for record in a_future:
        total_amount=total_amount+record[1]
        
    return total_amount


#期货卖出
def order_sell_futures(account,futures_code,time,sell_amount,huadian,Close,Volume):#fee 卖出手续费 tax印花税 amount:卖多少股
    fee_dict={'AG': 0.50/100/100,'AL': 3/100/100,'AU': 10/100/100,'BU': 1.00/100/100,'CU': 0.50/100/100,'FU': 0.10/100/100,
              'HC': 1.00/100/100,'NI': 3/100/100,'PB': 0.40/100/100,'RB': 1.00/100/100,'RU': 3.00/100/100,'SN': 3/100/100,
              'WR': 0.40/100/100,'ZN': 3/100/100,'SP': 0.50/100/100,'SS': 2/100/100,'A': 2/100/100,'B': 1/100/100,
              'BB': 1.00/100/100,'C': 2/100/100,'CS': 1.5/100/100,'FB': 1.00/100/100,'I': 1.00/100/100,'J': 1.00/100/100,
              'JD': 1.50/100/100,'JM': 1.00/100/100,'L': 1/100/100,'M': 1.5/100/100,'P': 2.5/100/100,'PP': 1/100/100,
              'V': 1/100/100,'Y': 2.5/100/100,'EG': 3/100/100,'RR': 1/100/100,'EB': 3/100/100,'PG': 6/100/100,
              'LH': 1.00/100/100,'AP': 5/100/100,'CF': 4.3/100/100,'CY': 4/100/100,'FG': 6/100/100,'JR': 3/100/100,
              'LR': 3/100/100,'MA': 1.00/100/100,'OI': 2/100/100,'PM': 30/100/100,'RI': 2.5/100/100,'RM': 1.5/100/100,
              'RS': 2/100/100,'SF': 3/100/100,'SM': 3/100/100,'SR': 3/100/100,'TA': 3/100/100,'WH': 30/100/100,
              'ZC': 150/100/100,'UR': 1.00/100/100,'PF': 3/100/100,'PK': 4/100/100,'SA': 3.5/100/100,'IC': 0.23/100/100,
              'IF': 0.23/100/100,'IH': 0.23/100/100,'IM': 0.23/100/100,'T': 3/100/100,'TF': 3/100/100,'TL': 3/100/100,
              'TS': 3/100/100,'BC': 0.10/100/100,'LU': 0.10/100/100,'NR': 0.20/100/100,'SC': 20/100/100}
        
    #涨跌幅限制，就不考虑第一涨停，第二天又涨停，第三天又涨停的限制了
    earn_lost_stop_normal=\
{'AG': 9.0/100,
 'AL': 7.0/100,
 'AU': 7.0/100,
 'BU': 10.0/100,
 'CU': 7.0/100,
 'FU': 13.0/100,
 'HC': 11.0/100,
 'NI': 10.0/100,
 'PB': 7.0/100,
 'RB': 11.0/100,
 'RU': 8.0/100,
 'SN': 12.0/100,
 'WR': 11.0/100,
 'ZN': 7.0/100,
 'SP': 8.0/100,
 'SS': 8.0/100,
 'A': 6.0/100,
 'B': 6.0/100,
 'BB': 5.0/100,
 'C': 6.0/100,
 'CS': 5.0/100,
 'FB': 5.0/100,
 'I': 11.0/100,
 'J': 15.0/100,
 'JD': 6.0/100,
 'JM': 15.0/100,
 'L': 6.0/100,
 'M': 6.0/100,
 'P': 7.0/100,
 'PP': 6.0/100,
 'V': 6.0/100,
 'Y': 6.0/100,
 'EG': 7.0/100,
 'RR': 5.0/100,
 'EB': 7.0/100,
 'PG': 7.0/100,
 'LH': 8.0/100,
 'AP': 9.0/100,
 'CF': 6.0/100,
 'CY': 6.0/100,
 'FG': 8.0/100,
 'JR': 7.0/100,
 'LR': 7.0/100,
 'MA': 7.0/100,
 'OI': 8.0/100,
 'PM': 7.0/100,
 'RI': 7.0/100,
 'RM': 8.0/100,
 'RS': 10.0/100,
 'SF': 10.0/100,
 'SM': 10.0/100,
 'SR': 8.0/100,
 'TA': 6.0/100,
 'WH': 7.0/100,
 'ZC': 10.0/100,
 'UR': 7.0/100,
 'PF': 7.0/100,
 'PK': 7.0/100,
 'SA': 8.0/100,
 'IC': 10.0/100,
 'IF': 10.0/100,
 'IH': 10.0/100,
 'IM': 10.0/100,
 'T': 2.0/100,
 'TF': 1.2/100,
 'TL': 10000000.0/100,
 'TS': 0.5/100,
 'BC': 7.0/100,
 'LU': 10.0/100,
 'NR': 8.0/100,
 'SC': 13.0/100}
    futures_type=futures_code.split(".")[0].replace("9999","")
    if futures_type in fee_dict.keys():
        fee=fee_dict[futures_type]
    else:
        fee=0
    
    
    

    
    if futures_type in earn_lost_stop_normal and\
    (get_price(futures_code,time,Close)-get_futures_ysterday_jie_suan_price(futures_code,time,Close,Volume))\
    /get_futures_ysterday_jie_suan_price(futures_code,time,Close,Volume)<=-earn_lost_stop_normal[futures_type]:
        #跌停无法卖出但能买入
        return "跌停"
    else:
        single_price=get_price(futures_code,time,Close)-huadian
        
        #if account.stock[stock_code]>=sell_amount:期货在数量为0时依然可以卖出，但是要保证金，这里没写保证金
        account.update_futures(futures_code,-sell_amount,time)
        total_price=single_price*sell_amount
        account.update_coin(account.get_coin()+total_price*(1-fee))
        return "Aoocunt coin: "+str(account.get_coin())+"\n"+futures_code+":"+str(account.stock[futures_code])+"\n"
        #else:
            #return "no stock to sell! \n "+stock_code+":"+str(account.stock[stock_code])
            
            
#期货特殊买入，平今仓
def within_day_order_buy_futures(account,futures_code,time,amount,huadian,Close,Volume):
    fee_dict={'CU': '1.00/100/100',
 'J': '1.40/100/100',
 'JM': '3.00/100/100',
 'LH': '2.00/100/100',
 'AP': '20/100/100',
 'IC': '2.30/100/100',
 'IF': '2.30/100/100',
 'IH': '2.30/100/100',
 'IM': '2.30/100/100'}
    #涨跌幅限制，就不考虑第一涨停，第二天又涨停，第三天又涨停的限制了
    earn_lost_stop_normal=\
{'AG': 9.0/100,
 'AL': 7.0/100,
 'AU': 7.0/100,
 'BU': 10.0/100,
 'CU': 7.0/100,
 'FU': 13.0/100,
 'HC': 11.0/100,
 'NI': 10.0/100,
 'PB': 7.0/100,
 'RB': 11.0/100,
 'RU': 8.0/100,
 'SN': 12.0/100,
 'WR': 11.0/100,
 'ZN': 7.0/100,
 'SP': 8.0/100,
 'SS': 8.0/100,
 'A': 6.0/100,
 'B': 6.0/100,
 'BB': 5.0/100,
 'C': 6.0/100,
 'CS': 5.0/100,
 'FB': 5.0/100,
 'I': 11.0/100,
 'J': 15.0/100,
 'JD': 6.0/100,
 'JM': 15.0/100,
 'L': 6.0/100,
 'M': 6.0/100,
 'P': 7.0/100,
 'PP': 6.0/100,
 'V': 6.0/100,
 'Y': 6.0/100,
 'EG': 7.0/100,
 'RR': 5.0/100,
 'EB': 7.0/100,
 'PG': 7.0/100,
 'LH': 8.0/100,
 'AP': 9.0/100,
 'CF': 6.0/100,
 'CY': 6.0/100,
 'FG': 8.0/100,
 'JR': 7.0/100,
 'LR': 7.0/100,
 'MA': 7.0/100,
 'OI': 8.0/100,
 'PM': 7.0/100,
 'RI': 7.0/100,
 'RM': 8.0/100,
 'RS': 10.0/100,
 'SF': 10.0/100,
 'SM': 10.0/100,
 'SR': 8.0/100,
 'TA': 6.0/100,
 'WH': 7.0/100,
 'ZC': 10.0/100,
 'UR': 7.0/100,
 'PF': 7.0/100,
 'PK': 7.0/100,
 'SA': 8.0/100,
 'IC': 10.0/100,
 'IF': 10.0/100,
 'IH': 10.0/100,
 'IM': 10.0/100,
 'T': 2.0/100,
 'TF': 1.2/100,
 'TL': 10000000.0/100,
 'TS': 0.5/100,
 'BC': 7.0/100,
 'LU': 10.0/100,
 'NR': 8.0/100,
 'SC': 13.0/100}
    #只单边收费
    only_sell=['AU', 'FU', 'PB', 'RU', 'WR', 'ZN', 'SP', 'SS', 'CF', 'CY', 'SF', 'SM', 'SR', 'TA', 'T', 'TF', 'TL', 'TS', 'BC', 'NR', 'SC']
    futures_type=futures_code.split(".")[0].replace("9999","")
    if futures_type in only_sell:
        fee=0
    else:
        if futures_type in fee_dict.keys():
            fee=fee_dict[futures_type]
        else:
            fee=0
    
 
    
    
    if futures_type in earn_lost_stop_normal and\
    (get_price(futures_code,time,Close)-get_futures_ysterday_jie_suan_price(futures_code,time,Close,Volume))/\
    get_futures_ysterday_jie_suan_price(futures_code,time,Close,Volume)>=earn_lost_stop_normal[futures_type]:
        #涨停无法买入可卖出
        return "涨停"
    else:
        single_price=get_price(futures_code,time,Close)+huadian
    
        #print(single_price)
    
        total_price0=single_price*amount
        #print(total_price0)
        total_price=total_price0*(1+fee)
        #print(total_price)
    
        #print(account.get_coin())
        #print(account.get_coin()>=total_price)
        if account.get_coin()>=total_price:#这个if条件语句有个意想不到的收获，解决了股票数据nan的问题，反正都是false 不会交易
            account.update_coin(account.get_coin()-total_price)
            account.update_futures(futures_code,amount,time)
            return "Aoocunt coin: "+str(account.get_coin())+"\n"+futures_code+":"+str(get_futures_amount(account,futures_code))+'\n'
        else:
            return "no money don't touch! \n Aoocunt coin:"+str(account.get_coin())
        
        
#期货特殊卖出，平今仓
def within_day_order_sell_futures(account,futures_code,time,sell_amount,huadian,Close,Volume):#fee 卖出手续费 tax印花税 amount:卖多少股
    fee_dict={'CU': '1.00/100/100',
 'J': '1.40/100/100',
 'JM': '3.00/100/100',
 'LH': '2.00/100/100',
 'AP': '20/100/100',
 'IC': '2.30/100/100',
 'IF': '2.30/100/100',
 'IH': '2.30/100/100',
 'IM': '2.30/100/100'}
        
    #涨跌幅限制，就不考虑第一涨停，第二天又涨停，第三天又涨停的限制了
    earn_lost_stop_normal=\
{'AG': 9.0/100,
 'AL': 7.0/100,
 'AU': 7.0/100,
 'BU': 10.0/100,
 'CU': 7.0/100,
 'FU': 13.0/100,
 'HC': 11.0/100,
 'NI': 10.0/100,
 'PB': 7.0/100,
 'RB': 11.0/100,
 'RU': 8.0/100,
 'SN': 12.0/100,
 'WR': 11.0/100,
 'ZN': 7.0/100,
 'SP': 8.0/100,
 'SS': 8.0/100,
 'A': 6.0/100,
 'B': 6.0/100,
 'BB': 5.0/100,
 'C': 6.0/100,
 'CS': 5.0/100,
 'FB': 5.0/100,
 'I': 11.0/100,
 'J': 15.0/100,
 'JD': 6.0/100,
 'JM': 15.0/100,
 'L': 6.0/100,
 'M': 6.0/100,
 'P': 7.0/100,
 'PP': 6.0/100,
 'V': 6.0/100,
 'Y': 6.0/100,
 'EG': 7.0/100,
 'RR': 5.0/100,
 'EB': 7.0/100,
 'PG': 7.0/100,
 'LH': 8.0/100,
 'AP': 9.0/100,
 'CF': 6.0/100,
 'CY': 6.0/100,
 'FG': 8.0/100,
 'JR': 7.0/100,
 'LR': 7.0/100,
 'MA': 7.0/100,
 'OI': 8.0/100,
 'PM': 7.0/100,
 'RI': 7.0/100,
 'RM': 8.0/100,
 'RS': 10.0/100,
 'SF': 10.0/100,
 'SM': 10.0/100,
 'SR': 8.0/100,
 'TA': 6.0/100,
 'WH': 7.0/100,
 'ZC': 10.0/100,
 'UR': 7.0/100,
 'PF': 7.0/100,
 'PK': 7.0/100,
 'SA': 8.0/100,
 'IC': 10.0/100,
 'IF': 10.0/100,
 'IH': 10.0/100,
 'IM': 10.0/100,
 'T': 2.0/100,
 'TF': 1.2/100,
 'TL': 10000000.0/100,
 'TS': 0.5/100,
 'BC': 7.0/100,
 'LU': 10.0/100,
 'NR': 8.0/100,
 'SC': 13.0/100}
    futures_type=futures_code.split(".")[0].replace("9999","")
    if futures_type in fee_dict.keys():
        fee=fee_dict[futures_type]
    else:
        fee=0
    
    
    

    
    if futures_type in earn_lost_stop_normal and\
    (get_price(futures_code,time,Close)-get_futures_ysterday_jie_suan_price(futures_code,time,Close,Volume))\
    /get_futures_ysterday_jie_suan_price(futures_code,time,Close,Volume)<=-earn_lost_stop_normal[futures_type]:
        #跌停无法卖出但能买入
        return "跌停"
    else:
        single_price=get_price(futures_code,time,Close)-huadian
        
        #if account.stock[stock_code]>=sell_amount:期货在数量为0时依然可以卖出，但是要保证金，这里没写保证金
        account.update_futures(futures_code,-sell_amount,time)
        total_price=single_price*sell_amount
        account.update_coin(account.get_coin()+total_price*(1-fee))
        return "Aoocunt coin: "+str(account.get_coin())+"\n"+futures_code+":"+str(account.stock[futures_code])+"\n"
        #else:
            #return "no stock to sell! \n "+stock_code+":"+str(account.stock[stock_code])
            
            
#平仓一只期货            
def end_transation_one_futures(account,futures_code,amount1,d,Close):#平一只期货的仓
    special_future=['CU','J','JM','LH','AP','IC','IF','IH','IM']
    
    futures_type=futures_code.split(".")[0].replace("9999","")

    #账号上所有的期货总数
    all_amount=get_futures_amount(account,futures_code)
    
    #和平仓日期同日期的期货总数
    same_day_open_amount=0
    for record in account.futures[futures_code]:
        if record[0].split(" ")[0]==d.split(" ")[0]:
             same_day_open_amount= same_day_open_amount+record[1]
                
    not_same_day_open_amount=all_amount-same_day_open_amount
    
    if amount1<=all_amount:#不然就不叫平仓了
        if abs(amount1)>= abs(not_same_day_open_amount) and futures_type in special_future:
            if not_same_day_open_amount>=0:
                order_sell_futures(account,futures_code,d,not_same_day_open_amount,0.05,Close,Volume)
            elif not_same_day_open_amount<0:
                order_buy_futures(account,futures_code,d,abs(not_same_day_open_amount),0.05,Close,Volume)
        
            if same_day_open_amount>=0:
                within_day_order_sell_futures(account,futures_code,d,same_day_open_amount,0.05,Close,Volume)
            elif same_day_open_amount<0:
                within_day_order_buy_futures(account,futures_code,d,abs(same_day_open_amount),0.05,Close,Volume)   
        
        
    
        else:#不在特殊平仓名单，
            if amount1>=0:
                order_sell_futures(account,futures_code,d,amount1,0.05,Close,Volume)
            if amount1<0:
                order_buy_futures(account,futures_code,d,abs(amount1),0.05,Close,Volume)
                
'''               
设amount1=800 all_amount=800 same_day_open_amount=-200 not_same_day_open_amount=1000 不进入特殊平仓
非今天买入1000仓，今天已经卖200仓，现在再卖800仓



设amount1=400 all_amount=-400 same_day_open_amount=-1400 not_same_day_open_amount=1000 不进入特殊平仓
非今天买入1000仓，今天已经卖出1400仓，现在再买入400仓，这里应该进入特殊平仓的，有错误
但是在单对期货对的时候没有问题，因为平仓逻辑应该把not_same_day_open_amount平仓，今天最多只能已经卖1000仓


设amount1=1050 all_amount=-1200 same_day_open_amount=-200 not_same_day_open_amount=-1000 进入特殊平仓
非今天卖出1000仓，今天已经卖出200仓，现在再买入1050仓



设amount1=800 all_amount=-800 same_day_open_amount=200 not_same_day_open_amount=-1000 不进入特殊平仓
非今天卖出1000仓，今天已经买入200仓，现在再买入800仓


假设两对期货对 一对做多2000 一对做空-1000 总1000 要平仓2000 amount1>all amount

假设两对期货对 一对做多2000 一对做多1000 总3000 要平仓2000 amount1<all amount 不会出现问题
'''                


#获取某个时刻的期货价格 
def get_total_value_of_futures_in_a_moment(cyf,d,Close):
    fee_dict={'AG': 0.50/100/100,'AL': 3/100/100,'AU': 10/100/100,'BU': 1.00/100/100,'CU': 0.50/100/100,'FU': 0.10/100/100,
              'HC': 1.00/100/100,'NI': 3/100/100,'PB': 0.40/100/100,'RB': 1.00/100/100,'RU': 3.00/100/100,'SN': 3/100/100,
              'WR': 0.40/100/100,'ZN': 3/100/100,'SP': 0.50/100/100,'SS': 2/100/100,'A': 2/100/100,'B': 1/100/100,
              'BB': 1.00/100/100,'C': 2/100/100,'CS': 1.5/100/100,'FB': 1.00/100/100,'I': 1.00/100/100,'J': 1.00/100/100,
              'JD': 1.50/100/100,'JM': 1.00/100/100,'L': 1/100/100,'M': 1.5/100/100,'P': 2.5/100/100,'PP': 1/100/100,
              'V': 1/100/100,'Y': 2.5/100/100,'EG': 3/100/100,'RR': 1/100/100,'EB': 3/100/100,'PG': 6/100/100,
              'LH': 1.00/100/100,'AP': 5/100/100,'CF': 4.3/100/100,'CY': 4/100/100,'FG': 6/100/100,'JR': 3/100/100,
              'LR': 3/100/100,'MA': 1.00/100/100,'OI': 2/100/100,'PM': 30/100/100,'RI': 2.5/100/100,'RM': 1.5/100/100,
              'RS': 2/100/100,'SF': 3/100/100,'SM': 3/100/100,'SR': 3/100/100,'TA': 3/100/100,'WH': 30/100/100,
              'ZC': 150/100/100,'UR': 1.00/100/100,'PF': 3/100/100,'PK': 4/100/100,'SA': 3.5/100/100,'IC': 0.23/100/100,
              'IF': 0.23/100/100,'IH': 0.23/100/100,'IM': 0.23/100/100,'T': 3/100/100,'TF': 3/100/100,'TL': 3/100/100,
              'TS': 3/100/100,'BC': 0.10/100/100,'LU': 0.10/100/100,'NR': 0.20/100/100,'SC': 20/100/100}
    
    
    
    end_coin=cyf.get_coin() #当前时刻账户上的资金   
    stock_value=0
    universe=list(Close.columns)[0:len(Close.columns)]
    
  
            
    for jjj in range(len(universe)):#对于每一只期货
        if cyf.get_stock(universe[jjj])!=0:#期货数量不为0
            futures_type=universe[jjj].split(".")[0].replace("9999","")
            if futures_type in fee_dict.keys():
                fee=fee_dict[futures_type]
            else:
                fee=0
        
            stock_value=stock_value+get_price(universe[jjj],d,Close)*cyf.get_stock(universe[jjj])-\
            get_price(universe[jjj],d,Close)*abs(cyf.get_stock(universe[jjj]))*fee#当分钟股票开盘价*股票数量 
    total_value=end_coin+stock_value

    
    return total_value





from tqdm import trange

#修复期货数据由于按照黄金的数据生成每分钟数据而产生的数据na问题
def fix_na_in_df(df):#如果a行b列的值为na,用b列里离a行最近的非na值代替na，要求该非na的值的索引在a行之前
    #for d in trange(len(df.index)):#电脑卡死
    for d in range(len(df.index)):
        for futures in df.columns:
            today_index=Close.index[d]
            yesterday_index=Close.index[d-1]
            if str(df.loc[today_index,futures])=='nan' and yesterday_index!= df.index[-1] and str(df.loc[yesterday_index,futures])!='nan':
                df.loc[today_index,futures]=df.loc[yesterday_index,futures]
        
    return df


#statsmodels.tsa.stattools.adfuller

import statsmodels.tsa.stattools as ts
# 创建一个函数用来协整检验
def cointegration_check(series01, series02):

    urt_rb2001 = ts.adfuller(np.array(series01), 1)[1]
    urt_rb2005 = ts.adfuller(np.array(series02), 1)[1]
    #print(urt_rb2001)
    #print(urt_rb2005)
    # 同时平稳或不平稳则差分再次检验
    if (urt_rb2001 > 0.1 and urt_rb2005 > 0.1) or (urt_rb2001 < 0.1 and urt_rb2005 < 0.1):
        urt_diff_rb2001 = ts.adfuller(np.diff(np.array(series01)), 1)[1]
        urt_diff_rb2005 = ts.adfuller(np.diff(np.array(series02), 1))[1]

        # 同时差分平稳进行OLS回归的残差平稳检验
        if urt_diff_rb2001 < 0.1 and urt_diff_rb2005 < 0.1:
            matrix = np.vstack([series02, np.ones(len(series02))]).T
            beta, c = np.linalg.lstsq(matrix, series01)[0]
            resid = series01 - beta * series02 - c
            if ts.adfuller(np.array(resid), 1)[1] > 0.1:
                result = 0.0
            else:
                result = 1.0
            return beta, c, resid, result
        else:
            result = 0.0
            return 0.0, 0.0, 0.0, result

    else:
        result = 0.0
        return 0.0, 0.0, 0.0, result
    
    
    
    
from dataclasses import dataclass

@dataclass
class OUParams:
    alpha: float  # mean reversion parameter
    gamma: float  # asymptotic mean
    beta: float  # Brownian motion scale (standard deviation)
        
        
#OU过程的参数估计       
from sklearn.linear_model import LinearRegression
import numpy as np
def estimate_OU_params(X_t: np.ndarray) -> OUParams:
    """
    Estimate OU params from OLS regression.
    - X_t is a 1D array.
    Returns instance of OUParams.
    """
    y = np.diff(X_t)
    X = X_t[:-1].reshape(-1, 1)
    reg = LinearRegression(fit_intercept=True)
    reg.fit(X, y)
    # regression coeficient and constant
    alpha = -reg.coef_[0]
    gamma = reg.intercept_ / alpha
    # residuals and their standard deviation
    y_hat = reg.predict(X)
    beta = np.std(y - y_hat)
    return OUParams(alpha, gamma, beta)


import numpy as np
#计算昨天结算价 
def get_futures_ysterday_jie_suan_price(futures_code,time,Close,Volume):
    bussiness=["IF9999.CCFX","TF9999.CCFX","T9999.CCFX","IC9999.CCFX","IH9999.CCFX","TS9999.CCFX","IM9999.CCFX","TL9999.CCFX"]
    #按照黄金开盘收盘时间生成的数据，一天555条数据
    if futures_code not in bussiness:
        #对于商品期货
        if "09:01:00"<=time.split(" ")[1]<="23:59:00":#在同一天
            yesterday_close_index=np.where(Close.index==time.split(" ")[0]+" 02:30:00")[0][0]
            today_open_index=np.where(Close.index==time.split(" ")[0]+" 09:01:00")[0][0]
        
            yesterday_open_index=today_open_index-555
        else:#不在同一天   00:00:00-02:30:00
            today_0_index=np.where(Close.index==time.split(" ")[0]+" 00:00:00")[0][0]
            yesterday_close_index=today_0_index-405
           
            
            
            
            yesterday_open_index=today_0_index-555-404
            
            
        
        yesterday_close_d=Close.index[yesterday_close_index]
        yesterday_open_d=Close.index[yesterday_open_index]
        #print(Close.index[yesterday_close_index])
        #print(Close.index[yesterday_open_index])
        
        yesterday_jie_suan_price=sum(np.array(Volume.loc[yesterday_open_d:yesterday_close_d,[futures_code]].dropna())*\
        np.array(Close.loc[yesterday_open_d:yesterday_close_d,[futures_code]].dropna()))\
        /sum(np.array(Volume.loc[yesterday_open_d:yesterday_close_d,[futures_code]].dropna()))
        
        return float(yesterday_jie_suan_price)
    
  

#生成统计套利的上下界
def generate_up_down(d,l,i,k):#d为日期，l为从当前时间戳往前多少单位时间，i为单对期货对在所有期货对中的排序，k为开仓的阈值
    futures1=sta_pair[i][0]
    futures2=sta_pair[i][1]
    today_index=Close.index[d]
    #print(today_index)
    yesterday_index=Close.index[d-1]
    #print(yesterday_index)
    l_day_ago_index=Close.index[d-l]
    windows_close=Close.loc[l_day_ago_index:yesterday_index,[futures1,futures2]]

    diff_price=pd.DataFrame(abs(windows_close[futures1]-windows_close[futures2]))
    diff_price.columns=[sta_pair[i][1]+" and "+sta_pair[i][0]+"价差"]
    diff_price=diff_price.dropna()
    #print(diff_price)
    OU_params_hat = estimate_OU_params(np.array(diff_price[sta_pair[i][1]+" and "+sta_pair[i][0]+"价差"].dropna()))
    mean_diff=np.mean(np.array(diff_price[sta_pair[i][1]+" and "+sta_pair[i][0]+"价差"].dropna()))
    std_diff=math.sqrt(np.var(np.array(diff_price[sta_pair[i][1]+" and "+sta_pair[i][0]+"价差"].dropna()))/(2*OU_params_hat.alpha))

    up_open=mean_diff+k*std_diff
    down_open=mean_diff-k*std_diff
    return mean_diff,up_open,down_open
