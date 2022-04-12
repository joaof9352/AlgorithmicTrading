#!pip install yfinance

import requests
import pandas as pd
import numpy as np
import yfinance as yf

r = requests.get("https://api.alternative.me/fng/?limit=0")
df = pd.DataFrame(r.json()["data"])
df.timestamp = pd.to_datetime(df['timestamp'], unit='s')
df.value = df.value.astype(int)
df.set_index(df.timestamp, inplace=True)
df.pop('timestamp')

df = df[::-1]
df1 = yf.download("BTC-USD",start='2018-02-01',end='2022-04-09')[['Close']]
df1.index.name = 'timestamp'

tog = df.merge(df1, on='timestamp')
tog['change'] = tog.Close.pct_change()

tog['position'] = 0

def setPosition(min, max):
    indicador = 0
    tog['position'] = 0
    for i in range(len(tog.index)):
        if indicador == 0 and tog['value'].iloc[i] < min:
            tog['position'].iloc[i] = 1
            indicador = 1
        elif indicador == 1 and tog['value'].iloc[i] > max:
            tog['position'].iloc[i] = -1
            indicador = 0

def evaluatePosition():
    total = 1
    buyPrice = 0
    for i in range(len(tog.index)):
        if tog['position'].iloc[i] == 1:
            buyPrice = tog['Close'].iloc[i]
        elif tog['position'].iloc[i] == -1:
            change = ((tog['Close'].iloc[i] - buyPrice) / buyPrice)
            total = total * (1+change)

    return total

path = input('Introduza o caminho do output.')
f = open(path, "w")
if f:
    bestPosition = 0
    values = 0,0
    f.write('low_bound,upper_bound;value\n')
    #0 a 99
    for i in range(100):
        for j in range(i+1,101):
            setPosition(i,j)
            result = evaluatePosition()
            if result > bestPosition:
                values = i,j
            f.write(f'{values[0]},{values[1]};{result}\n')
            print(f'{i} - {j} => {result}')

    print(values)
    f.close()