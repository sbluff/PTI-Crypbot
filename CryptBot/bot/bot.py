# from twisted.internet import reactor
from binance import BinanceSocketManager
from binance.client import Client
from binance.enums import *
from trade import trade 
from datetime import datetime
from mysql.connector import Error
import mysql.connector
import settings
import numpy as np
import time
import API
import Utils
import requests
import random
import json


btcPrice = {'error':False}
targetedCryptos = {'BTCUSDT'}
binanceRestApiUrl = 'https://api.binance.com/api/v3/avgPrice?symbol='
requestHeaders = {'user-agent': 'my-app/0.0.1'}

class binanceBot:
    #set the maximum ammount of euros the bot can use 

    def __init__(self, credit, timePeriod, mode):
        self.conn = self.initDbConnection()
        self.timePeriod = timePeriod
        self.credit = self.loadCredit(credit)               #credit for the bot 
        self.tradeAmount = float(self.loadTradeAmount())           #tradeAmount for the trades
        self.mode = self.loadMode(mode)
        print(self.mode)
        if self.tradeAmount == 0:
            self.tradeAmount = 25.00   
        self.keys = API.binanceKeysLoader()                 #load keys
        self.client = Client(self.keys[0], self.keys[1])    #create session
        self.targetData = self.getTargetData(self.timePeriod)
        self.displayMenu()

    #Starts the connection with the db
    def initDbConnection(self):
        try:
            parameters = settings.getSQLParameters("local")
            connection = mysql.connector.connect(
                host=parameters["server"],
                user=parameters["username"],
                password=parameters["password"],
                database=parameters["db_name"]
            )
        except Error as e:
            print("Error while connecting to MySQL", e)    
        finally:
            if connection.is_connected():
                return connection             
            else:    
                exit


    #Getter for client object
    def getClient(self):
        return self.client    


    #Gets the current value of opened and closed trades
    def getWorth(self):
        data = []
        cursor = self.conn.cursor()
        sql = "SELECT * FROM trades"
        cursor.execute(sql)
        allTrades = cursor.fetchall()
        for x in allTrades:
            data.append(trade(self.client, x, "load", cursor))  

        totalValue = 0
        totalPaid = 0
        for x in data:
            tradeData = x.getTradeData()
            totalPaid += float(tradeData['paidAmount']) 
            if tradeData['status'] == 'opened':
                totalValue += float(tradeData['currentValue']) 
            elif tradeData['status'] == 'closed':
                totalValue += float(tradeData['paidAmount']) + float(tradeData['balance'])   

        return {'totalValue': totalValue, 'totalPaid': totalPaid}    


    #Retrieves the data on the targeted cryptos
    def getTargetData(self, startDate):
        targetData = {}
        for crypto in targetedCryptos:
            # print(crypto)
            targetData[crypto] = self.getHistoricalKLines(crypto, Client.KLINE_INTERVAL_2HOUR, startDate, "1 minute ago UTC")
        return self.calculateAveragePrice(targetData)    


    #Returns tradeCounter (variable used for id)
    #If the db is empty it returns 0, if it isn't it returns the next available number
    def getTradeCounter(self, cursor):
        sql = "SELECT COUNT(*) FROM trades"
        cursor.execute(sql)
        if cursor.fetchone()[0] > 0:
            sql = "SELECT MAX(id) FROM trades"
            cursor.execute(sql)
            tradeCounter = cursor.fetchone()[0] + 1
        else:    
            tradeCounter = 0 

        return tradeCounter   


    #Gets the candles of the selected cryptos and stores it in a file
    def getHistoricalKLines(self, symbol, interval, start_str, end_str=None):
        """Get Historical Klines from Binance
        See dateparse docs for valid start and end string formats http://dateparser.readthedocs.io/en/latest/
        If using offset strings for dates add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
        :param symbol: Name of symbol pair e.g BNBBTC
        :type symbol: str
        :param interval: Biannce Kline interval
        :type interval: str
        :param start_str: Start date string in UTC format
        :type start_str: str
        :param end_str: optional - end date string in UTC format
        :type end_str: str
        :return: list of OHLCV values
        """
        # create the Binance client, no need for api key
        client = Client("", "")

        # init our list
        output_data = []

        # setup the max limit
        limit = 500

        # convert interval to useful value in seconds
        timeframe = Utils.intervalToMilliseconds(interval)

        # convert our date strings to milliseconds
        start_ts = Utils.dateToMilliseconds(start_str)

        # if an end time was passed convert it
        end_ts = None
        if end_str:
            end_ts = Utils.dateToMilliseconds(end_str)

        idx = 0
        # it can be difficult to know when a symbol was listed on Binance so allow start time to be before list date
        symbol_existed = False
        while True:
            # fetch the klines from start_ts up to max 500 entries or the end_ts if set
            temp_data = client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit,
                startTime=start_ts,
                endTime=end_ts
            )

            # handle the case where our start date is before the symbol pair listed on Binance
            if not symbol_existed and len(temp_data):
                symbol_existed = True

            if symbol_existed:
                # append this loops data to our output data
                output_data += temp_data

                # update our start timestamp using the last value in the array and add the interval timeframe
                start_ts = temp_data[len(temp_data) - 1][0] + timeframe
            else:
                # it wasn't listed yet, increment our start date
                start_ts += timeframe

            idx += 1
            # check if we received less than the required limit and exit the loop
            if len(temp_data) < limit:
                # exit the while loop
                break

            # sleep after every 3rd call to be kind to the API
            if idx % 3 == 0:
                time.sleep(1)

        return output_data
     
    
    #Returns a list with all the trades still open
    def loadOpenedTrades(self):
        result = []
        cursor = self.conn.cursor()
        sql = "SELECT * FROM trades WHERE status = 'opened'"
        cursor.execute(sql)
        openedTrades = cursor.fetchall()
        for x in openedTrades:
            result.append(trade(self.client, x, "load", cursor))  
        return result     


    #If the db has previous trades, it loads the last credit stored, otherwise it return credit
    def loadCredit(self, credit):
        cursor = self.conn.cursor()
        result = credit 
        sql = "SELECT credit FROM bot_parameters"
        cursor.execute(sql)       
        result = cursor.fetchone()[0]
        return result    

    def loadMode(self, mode):
        cursor = self.conn.cursor()
        result = mode 
        sql = "SELECT mode FROM bot_parameters"
        cursor.execute(sql)       
        result = cursor.fetchone()[0]
        return result 

    #Load the tradeAmount used in previous executions if it existed
    def loadTradeAmount(self):        
        cursor = self.conn.cursor()
        sql = "SELECT entryAmount FROM bot_parameters"
        cursor.execute(sql)       
        result = cursor.fetchone()[0]
        return result    

    #Adds addAmount to the available quantity and stores it into the db 
    def addCredit(self, addAmount):
        cursor = self.conn.cursor()
        self.credit += addAmount
        sql = "SELECT credit FROM trades where id = (select MAX(id) from trades)"       
        cursor.execute(sql)
        credit = cursor.fetchone()
        sql = "SELECT MAX(id) FROM trades"       
        cursor.execute(sql)
        id = cursor.fetchone()[0]
        print(id)
        sql = "UPDATE trades SET credit =" + str(float(credit[0]) + float(addAmount)) + " WHERE id = " + str(id)
        print(sql)
        cursor.execute(sql)
        self.conn.commit()

    #This method simulates a trading algorithm, tradeAmount is in Dollars
    #tradeAmount represents the packet size
    def startTrading(self, tradeAmount = 20.00):
        cursor = self.conn.cursor()
        trades = self.loadOpenedTrades()
        tradeCounter = self.getTradeCounter(cursor)
        while(True):
            self.targetData = self.getTargetData(self.timePeriod)
            # Check active trades
            for currentTrade in trades:
                tradeData = currentTrade.getTradeData()
                if 1.015 * (tradeAmount) < tradeData['currentValue']:
                    currentTrade.closeTrade(tradeData['currentValue'], tradeData['currentPrice'])
                    self.conn.commit()
                    trades.remove(currentTrade)
                    currentTrade.printInfo()            
                    self.credit += tradeData['currentValue'] #Update credit avilable
                    print("Selling package")
                

            if int(self.credit/tradeAmount) > 0: #Look for the crypo that has deviated the most of its average price 
                for cryptoData in self.targetData:
                    deviation = float(cryptoData['deviation'][0:len(cryptoData['deviation'])-1])
                    if deviation < -2.0 and int(self.credit/tradeAmount) > 0:
                    # if int(self.credit/tradeAmount) > 0:
                        self.credit -= tradeAmount
                        startDate = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                        coins = '%.6f'%float(tradeAmount/cryptoData['price'])
                        data = [tradeCounter, cryptoData['crypto'], cryptoData['price'], tradeAmount, "opened", None, None, startDate, None, None, self.mode, self.credit, coins]
                        # if self.mode == 'prod': #place real orders
                        #     self.placeOrder(cryptoData['crypto'], coins)

                        newTrade = trade(self.client, data, "create", cursor) #CREATE NEW TRADE!
                        self.conn.commit()
                        trades.append(newTrade)
                        tradeCounter += 1
                        newTrade.printInfo()
                    else:
                        print("BOT STOPS... deviation is at " + str(deviation) + " for " + cryptoData['crypto'])
                    time.sleep(5)    

            time.sleep(20)             

    #calculates the average price for the targeted cryptos and the 
    def calculateAveragePrice(self, targetData):
        result = []
        for crypto in targetData:
            sum = 0
            for flag in targetData[crypto]:
                sum += float(flag[1]) #flag[1] belongs to open price
            averagePrice = float(sum/len(targetData[crypto])) 
            price = float((requests.get(binanceRestApiUrl + crypto, headers=requestHeaders)).json()['price'])
            # print("PRICE: " + str(price) + "; AVERAGE PRICE: " + str(averagePrice))
            deviation = round((price-averagePrice)/averagePrice * 100.00, 3)
            result.append(
                {
                    'crypto': crypto,
                    'averagePrice': averagePrice * 0.88,
                    'price': price,
                    'deviation': deviation
                 }
            )
        random.shuffle(result)
        for dict in result:
            dict['deviation'] = str(dict['deviation']) + '%'
        return result    

    #MENU
    def printOptions(self):
        print("PYTHON-BINANCE TRADING BOT")
        print("")
        print("(A) Start trading")
        print("(B) Get current worth")
        print("(C) Print targeted crpyto data")
        print("(D) Place ETH order")
        print("(E) Sell ETH")
        print("(F) Add credit")
        print("(G) Get possible credit")
        print("(H) Exit")
        print("")
        print("Developed by Alonso Fernandez https://github.com/spanishblufff")

    #MENU
    def displayMenu(self):
        while (True):
            self.printOptions()
            option = input()
            if option == "A" or option == "a":
                self.startTrading(self.tradeAmount)
            elif option == "B" or option == "b":
                print(self.getWorth())
            elif option == "C" or option == "c":
                print(self.getTargetData())
            elif option == "D" or option == "d":
                self.placeOrder('ETHUSDT', 0.005)    
            elif option == "E" or option == "e":
                self.closeOrder()
            elif option == "F" or option == "f":
                self.addCredit(float(input("Enter amount to add: ")))
            elif option == "G" or option == "g":
                self.getCredit()    
            elif option == "H" or option == "h":
                exit() 
            else:
                print("Option not found, try again...")

    def getCredit(self):
        usdt = self.client.get_account()['balances'] 
        #print(usdt)
        list(filter(lambda person: person['asset'] == 'usdt', usdt))
        print(usdt)


bot = binanceBot(1000, "2 months ago UTC", "test")
