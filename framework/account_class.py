import pandas as pd
import copy

futures_list=['A9999.XDCE',
 'AG9999.XSGE',
 'AL9999.XSGE',
 'AO9999.XSGE',
 'AP9999.XZCE',
 'AU9999.XSGE',
 'B9999.XDCE',
 'BB9999.XDCE',
 'BC9999.XINE',
 'BR9999.XSGE',
 'BU9999.XSGE',
 'C9999.XDCE',
 'CF9999.XZCE',
 'CJ9999.XZCE',
 'CS9999.XDCE',
 'CU9999.XSGE',
 'CY9999.XZCE',
 'EB9999.XDCE',
 'EC9999.XINE',
 'EG9999.XDCE',
 'FB9999.XDCE',
 'FG9999.XZCE',
 'FU9999.XSGE',
 'HC9999.XSGE',
 'I9999.XDCE',
 'J9999.XDCE',
 'JD9999.XDCE',
 'JM9999.XDCE',
 'JR9999.XZCE',
 'L9999.XDCE',
 'LC9999.GFEX',
 'LH9999.XDCE',
 'LR9999.XZCE',
 'LU9999.XINE',
 'M9999.XDCE',
 'MA9999.XZCE',
 'NI9999.XSGE',
 'NR9999.XINE',
 'OI9999.XZCE',
 'P9999.XDCE',
 'PB9999.XSGE',
 'PF9999.XZCE',
 'PG9999.XDCE',
 'PK9999.XZCE',
 'PM9999.XZCE',
 'PP9999.XDCE',
 'PX9999.XZCE',
 'RB9999.XSGE',
 'RI9999.XZCE',
 'RM9999.XZCE',
 'RR9999.XDCE',
 'RS9999.XZCE',
 'RU9999.XSGE',
 'SA9999.XZCE',
 'SC9999.XINE',
 'SF9999.XZCE',
 'SH9999.XZCE',
 'SI9999.GFEX',
 'SM9999.XZCE',
 'SN9999.XSGE',
 'SP9999.XSGE',
 'SR9999.XZCE',
 'SS9999.XSGE',
 'TA9999.XZCE',
 'UR9999.XZCE',
 'V9999.XDCE',
 'WH9999.XZCE',
 'WR9999.XSGE',
 'Y9999.XDCE',
 'ZC9999.XZCE',
 'ZN9999.XSGE']


def generate_rong(Close):
    rong=pd.read_csv("BListX两融卷单.csv",index_col=0)
    empty_rong=list(rong["0"])
    timedict={}
    rong_dict1={}
    for tk in empty_rong:
        if tk in Close.columns:
            rong_dict1[tk]=copy.deepcopy(timedict)#index1方借入股票的数量 index2放借入股票的资金
    rong_dict=rong_dict1.copy()
    return rong_dict

def generate_stock(Close):
    universe=list(Close.columns)[0:len(Close.columns)]
    stkdict1={}
    for stk in range(len(universe)):
        stkdict1[universe[stk]]=0
    
    stkdict=stkdict1.copy()
    return stkdict

def generate_futures(futures_list):
    timelist=[]
    futures_dict={}
    for futures in futures_list:
        futures_dict[futures]=copy.deepcopy(timelist)
        
    return futures_dict
        



class account:
    def __init__(self,name,key,coin,Close):
        self.name=name
        self.key=key
        self.coin=coin
        self.stock=copy.deepcopy(generate_stock(Close))#股票
        self.credit_stock=copy.deepcopy(generate_rong(Close))#融券
        self.futures=copy.deepcopy(generate_futures(futures_list))#期货
        
    def get_name(self):
        return self.name
    
    def get_coin(self):
        coin=self.coin
        return coin
    
    def get_stock(self,stock_code):
        return self.stock[stock_code]
    
    def update_coin(self,money):
        self.coin=money
        return "update coin successfully"
        
    def update_stock(self,stock_code,amount):
        self.stock[stock_code]=amount
        return "update stock amount successfully"
    
    
    #融券
    def get_credit_stock(self,stock_code,time):
        try:
            return self.credit_stock[stock_code][time]#时间，借的股票的数量，借的股票所欠券商的钱
        except:
             print("找不到融券记录")
             return [0,0]
    
    
    def get_total_credit_stock(self,stock_code):#借的某只股票总数
        total_borrow_number=0
        if self.credit_stock[stock_code]!={}:
            for t in self.credit_stock[stock_code].keys():
                total_borrow_number=total_borrow_number+self.credit_stock[stock_code][t][0]
            return total_borrow_number
        else:
            return 0
            
        
    def update_credit_stock(self,stock_code,time,amount,total_price):
        self.credit_stock[stock_code][time]=[amount,total_price]
        return "update credit stock amount successfully"
    
    #期货
    def get_futures(self,futures_code):
        try:
            return self.futures[futures_code]
        except:
             print("找不到期货记录")
             

        
    def update_futures(self,futures_code,amount,time):
        self.futures[futures_code].append([time,amount])
        return "update futures amount successfully"
    