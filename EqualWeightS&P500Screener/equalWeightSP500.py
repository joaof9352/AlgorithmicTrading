#Given the value of the portfolio, this script calculates the number of shares of each stock from S&P500 to buy to have a equal weight portfolio.

import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math

from secrets import IEX_CLOUD_API_TOKEN #API_TOKEN

#Get List of Stocks from S&P500 acessing wikipedia!
listOfStocks = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies#S&P_500_component_stocks')[0]
listOfStocks = listOfStocks.drop(['Founded','CIK','Date first added','Headquarters Location','SEC filings'],axis=1)
listOfStocks = listOfStocks.sort_values('Symbol')
print(len(listOfStocks.index))

my_columns = ['Ticker','Stock Price','Market Cap', 'Number of Shares to Buy']
final_dataframe = pd.DataFrame(columns=my_columns)

#Divide our list of stocks into lists of 100
chunkedListStocks = list(chunks(listOfStocks['Symbol'],100))
symbol_strings = []

#Make the n lists of 100 into n strings
for chunk in chunkedListStocks:
    symbol_strings.append(','.join(chunk))

#For the n strings, get the data and put it on the final_dataframe
for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    #For every symbol in each one of n strings, append the data to final_dataframe
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(pd.Series([symbol,data[symbol]['quote']['latestPrice'],data[symbol]['quote']['marketCap'],'N/A'], index=my_columns), ignore_index=True)

#Calculate the number of shares to buy based on the value of portfolio
portfolio_size = input("Enter the value of your portfolio: ")
position_size = int(portfolio_size)/len(final_dataframe.index)
for i in range(0,len(final_dataframe.index)):
    final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size/final_dataframe.loc[i, 'Stock Price'])
   
#Write to Xlsx
writer = pd.ExcelWriter('recommended_trades.xlsx', engine='xlsxwriter')
final_dataframe.drop(['Stock Price','Market Cap'],axis=1).to_excel(writer, sheet_name='Recommended Trades', index = False)
