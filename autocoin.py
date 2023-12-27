import pyupbit
import pandas as pd
from datetime import datetime
import numpy as np
import math
import time
import calendar
import asyncio
import telebot
import json
import pickle
import os

token = "6850065807:AAGwnB_HwBkUV1SCAS9gApVOP-cmMuTCzpQ"
chat_id = "1477960276"
access = "YWRkoBsxCb1KN43m9GBOyOdydcSsFYGvEx8ziEes"
secret = "aKDix7HiDvHOXsNK6qdV6AbSQPtc01BxTzeRNpY9"
    
upbit = pyupbit.Upbit(access, secret)
bot = telebot.TeleBot(token=token)
upbit.get_balances()
last_checked_time = None
crypto_list = ["KRW-BTC","KRW-SOL","KRW-STX","KRW-NEAR","KRW-MATIC","KRW-MINA"]


def telegramlog(message):
    print(datetime.now().strftime('[%y/%m/%d %H:%M:%S]'), message)
    strbuf = datetime.now().strftime('[%y/%m/%d %H:%M:%S] ') + message
    bot.send_message(chat_id, text = strbuf)


def printlog(message, *args):
    print(datetime.now().strftime('[%y/%m/%d %H:%M:%S]'), message, *args)

def get_candle_high_low_range(crypto):
    df = pyupbit.get_ohlcv(crypto, interval = 'minute240', to=datetime.now()).tail(20)
    candle_high = max(df['high'])
    candle_low = min(df['low'])
    candle_high80 = candle_low + 0.8 * (candle_high - candle_low)
    candle_low20 = candle_low + 0.2 * (candle_high - candle_low)   
    return candle_high, candle_low, candle_high80, candle_low20

def buy_crypto(crypto):
    current_price = pyupbit.get_current_price(crypto)
    unit = upbit.get_balance(ticker=crypto)
    if current_price > get_candle_high_low_range(crypto)[2] and str(unit)=='0':
        krw = upbit.get_balance(ticker="KRW")
        orderbook = pyupbit.get_orderbook(ticker=crypto)['orderbook_units'][0]['ask_price']
        amount = krw / (1 + len(crypto_list) - len(upbit.get_balances())) - 0.01 * krw
        unit = amount / orderbook
        upbit.buy_market_order(crypto, amount)
        telegramlog("BUY ORDER SUBMITTED: "+str(amount)+" "+str(crypto))


def sell_crypto(crypto):
    current_price = pyupbit.get_current_price(crypto)
    unit = upbit.get_balance(ticker=crypto)
    if current_price < get_candle_high_low_range(crypto)[3] and str(unit) != '0':
        upbit.sell_market_order(crypto, unit)
        amount = unit * current_price
        profit = round((current_price/ upbit.get_avg_buy_price(ticker=crypto) - 1) * 100,2)
        telegramlog("SELL ORDER SUBMITTED "+str(amount)+" "+str(profit)+"%"+" "+str(crypto))

def stoploss_crypto(crypto):
    current_price = pyupbit.get_current_price(crypto)
    unit = upbit.get_balance(ticker=crypto)
    if current_price < 0.91 * upbit.get_avg_buy_price(ticker=crypto) and str(unit) != '0':
        upbit.sell_market_order(crypto, unit)
        amount = unit * current_price
        telegramlog("STOP LOSS ORDER SUBMITTED "+str(amount)+" "+str(crypto))

def ROC_crypto(crypto):
    current_price = pyupbit.get_current_price(crypto)
    average_price = upbit.get_avg_buy_price(ticker=crypto)
    ROC = round((current_price/ average_price - 1) * 100,1)
    return ROC

def wait_until_top_of_hour():
    current_time = datetime.now()
    if current_time.minute == 00:
        time.sleep(59)  # 59초 대기

while True:
    try:
        buy_crypto(crypto_list[0])
        buy_crypto(crypto_list[1])
        buy_crypto(crypto_list[2])
        buy_crypto(crypto_list[3])
        buy_crypto(crypto_list[4])
        buy_crypto(crypto_list[5])
        
        sell_crypto(crypto_list[0])
        sell_crypto(crypto_list[1])
        sell_crypto(crypto_list[2])
        sell_crypto(crypto_list[3])
        sell_crypto(crypto_list[4])
        sell_crypto(crypto_list[5])
        
        stoploss_crypto(crypto_list[0])
        stoploss_crypto(crypto_list[1])
        stoploss_crypto(crypto_list[2])
        stoploss_crypto(crypto_list[3])
        stoploss_crypto(crypto_list[4])
        stoploss_crypto(crypto_list[5])
        
        roi_crypto_0 = ROC_crypto(crypto_list[0])
        roi_crypto_1 = ROC_crypto(crypto_list[1])
        roi_crypto_2 = ROC_crypto(crypto_list[2])
        roi_crypto_3 = ROC_crypto(crypto_list[3])
        roi_crypto_4 = ROC_crypto(crypto_list[4])
        roi_crypto_5 = ROC_crypto(crypto_list[5])
        
        current_time = datetime.now()
        if last_checked_time is None or (current_time.minute == 00 and current_time != last_checked_time):
           telegramlog("YOUR CURRENT ROC IS "
                 + str(crypto_list[0]) + " " + str(roi_crypto_0) + "%, "
                 + str(crypto_list[1]) + " " + str(roi_crypto_1) + "%, "
                 + str(crypto_list[2]) + " " + str(roi_crypto_2) + "%, "
                 + str(crypto_list[3]) + " " + str(roi_crypto_3) + "%, "
                 + str(crypto_list[4]) + " " + str(roi_crypto_4) + "%, "      
                 + str(crypto_list[5]) + " " + str(roi_crypto_5) + "%")     
           last_checked_time = current_time
           wait_until_top_of_hour()
           
    except:
        print("Error!")
        telegramlog("Bot Error!")
    
    time.sleep(1)
