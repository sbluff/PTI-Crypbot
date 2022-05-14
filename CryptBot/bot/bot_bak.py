from twisted.internet import reactor
from binance import BinanceSocketManager
from binance.client import Client
from trade import trade 
import numpy as np
import pandas as pd
import datetime
import API
import Utils
import requests
import json
import os, shutil
import csv


btcPrice = {'error':False}
targetedCryptos = ['LINK', 'DOT', 'SAND', 'LUNA', 'MATIC', 'VET', 'MANA', 'CHESS']

class binanceBot:
    #set the maximum ammount of euros the bot can use 

    def __init__(self, targets, credit, timePeriod):
        self.credit = credit                                #credit for the bot
        self.targetedCryptos = targets                      
        self.clearCandleDirectory()             
        self.keys = API.binanceKeysLoader()                 #load keys
        self.client = Client(self.keys[0], self.keys[1])    #create session
        self.wallet = self.updateWallet()                   
        self.targetData = self.getTargetData(timePeriod)
        print(self.client.get_all_tickers()['ETH'])
        #self.socketManager = API.initConection(self.client);

    #deletes the content of ./candles directory             
    def clearCandleDirectory(self):
        folder = './candles'
        file_path = ''
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
        
    #Updates wallet's attribute content  
    #TODO: import also staked coins     
    def updateWallet(self):
        myWallet = []
        accountInfo = self.client.get_account()['balances']
        for crypto in accountInfo:
            value = float(crypto['free'])
            if value != 0.00000000:
                myWallet.append(crypto)
            if (crypto['asset'] == 'EUR'):
                myWallet.append(crypto)
        return myWallet
    
    #Prints wallet's attribute content
    def printWallet(self):
        print(self.wallet)

    #Getter for client object
    def getClient(self):
        return self.client    

    #Retrieves the data on the targeted cryptos
    def getTargetData(self, startDate):
        targetData = {}
        for crypto in self.targetedCryptos:
            targetData[crypto] = self.getHistoricalKLines(crypto, Client.KLINE_INTERVAL_2HOUR, startDate, "1 minute ago UTC")
            Utils.saveCandleFile(targetData[crypto], crypto, Client.KLINE_INTERVAL_2HOUR, startDate, "1 minute ago UTC")
        return targetData    

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
    
    #TODO this method should also return the crypto name
    #calculates the average price for the targeted cryptos -- stores it in averagePrice
    def calculateAveragePrice(self, symbol, ):
        folder = './candles/'
        file_path = ''
        sum = 0
        counter = 0
        for filename in os.listdir(folder):
            f = open(folder + filename)
            flags = json.load(f)
            for flag in flags:
                sum += float(flag[1]) #flag[1] belongs to open price
                counter = counter + 1
            
            self.averagePrice = float(sum/counter) #average price
            return 0
        return -1                     #error    

    # 1) exports the contents of your wallet into a csv file named "contabilidad/exports/networth-dd-mm-yy.csv"
    # 2) updates networth.csv (containing all the historical csv) -> updateCsvFile()
    # 3) updates networth.odf (containing the last csv export + bank data) -> updateOdsFile()
    # TODO: Broken in windows
    def exportWallet(self):
        date = datetime.datetime.now().strftime('%d-%m.%Y')
        with open("../../../personal/contabilidad/exports/networth-" + date + ".csv", 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            total = 0
            #get the eurusdt pair
            r2 = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=EURUSDT")
            eur_usdt = float(r2.json()['price'])
            
            #headers:
            writer.writerow([date])
            writer.writerow(['Coin', '#Coins', '#LockedCoins', 'Price(EUR)'])
            cryptoList = []
            for crypto in self.wallet: 
                if (float(crypto['free']) > 0 or float(crypto['locked']) > 0) and crypto['asset'] != 'BETH':
                    address = "https://api.binance.com/api/v3/ticker/price?symbol=" + crypto['asset']
                    #if the asset is BUSD we can only get the pair with USD
                    if crypto['asset'] != 'BUSD':
                        address += 'EUR'
                        
                    else:
                        address += 'USDT'
                                     
                    r = requests.get(address)
                    amountFree = 0
                    amountLocked = 0
                    if crypto['asset'] != 'BUSD':
                        amountFree += float(float(r.json()['price']) * float(crypto['free']))
                        amountLocked += float(float(r.json()['price']) * float(crypto['locked']))
                    
                    #keep in mind that the price is in dollars when the coin is BUSD
                    else:
                        amountFree += float(r.json()['price']) * float(crypto['free'])/eur_usdt
                        amountLocked += float(float(r.json()['price']) * float(crypto['locked']))
                    total += amountFree + amountLocked    
                         
                    list = [crypto['asset'], crypto['free'], crypto['locked'], amountFree + amountLocked]
                    cryptoList.append(list)
                    writer.writerow(list)

            writer.writerows([[], ['Total', total]])
            print("csv exported!")
        self.updateOdsFile(cryptoList)    
        self.updateCsvFile()

    # 1) gets all the export files, sorts them and copies all of their data into a list.
    # 2) copy the list into networth.csv 
    def updateCsvFile(self):
        data = []
        files = []
        [files.append(x) for x in os.listdir("../../../personal/contabilidad/exports") if (x not in files)]
        # get all unique files in exports starting with networth and copy their content to data 
        files.sort(reverse=True)
        for file in files:
            if file.startswith("networth"):
                with open("../../../personal/contabilidad/exports/" + file, 'r') as file_csv:
                    csv_reader = csv.reader(file_csv ,delimiter=',')
                    aux = []
                    for row in csv_reader:
                        aux.append(row)
                        
                    data.append(aux)           
        
        #TODO: don't overwrite networth.csv. Instead add the missing entries            
        with open("../../../personal/contabilidad/networth.csv", 'w', newline='') as target_file_csv:
            writer = csv.writer(target_file_csv)
            for export in data:
                for entry in export:
                    writer.writerow(entry)      
    
    # pre: recieves a cryptoList containing all the cryptos in your wallet
    #      each entry of cryptoList has this format: [asset name, free coins, locked coins, euros owned]
    # post:                       
    #       1) r
    def updateOdsFile(self, cryptoList): 
        file = pd.read_excel("../../../personal/contabilidad/networth.ods")
        json_file = file.values.tolist() 
            
        i = 0
        found_array = []
        total = 0
        while i < len(cryptoList):
            found1 = False
            crypto = cryptoList[i]
            asset = crypto[0]
            total += crypto[3]
            
            found2 = False
            j = 0
            found_array.append(asset)
            while j < len(json_file) and not found1 and not found2:       
                if json_file[j][0] == 'TOTAL':
                    # update total!
                    json_file[j][3] = total
                    found1 = True
                    
                # update in json_file
                elif asset in json_file[j]:
                    found2 = True
                    n_coins = float(crypto[1]) + float(crypto[2])
                    asset_price = float(crypto[3])/n_coins
                    json_file[j][1] = n_coins
                    json_file[j][2] = asset_price
                    json_file[j][3] = crypto[3]
                j += 1
            
            #insert in json_file
            if not found2:
                n_coins = float(crypto[1]) + float(crypto[2])
                json_file.insert(0, [asset, float(crypto[1]) + float(crypto[2]), float(crypto[3])/n_coins, crypto[3]])
                
            i += 1

        j = 0    
        found1 = False
        while j < len(json_file):
            if not found1 and json_file[j][0] not in found_array:
                json_file.pop(j)
                j-=1
                
            if not found1 and json_file[j+1][0] == 'TOTAL':
                found1 = True
            
            elif json_file[j][0] == 'Total:': 
                json_file[j][1] = total + float(json_file[j-3][3])
            j+=1 
            
        df = pd.DataFrame(json_file, columns = ['Coin', '#Coins', 'Price(EUR)', 'Total'])  
        df.to_excel('../../../personal/contabilidad/networth_experimental2.ods')

    #This method simulates a trading algorithm   
    def startTrading(self):
        # Each trade will be 10.00 EUR, tradeUnits represents how many simultaneous trades can happen 
        trades = []
        closedTrades = []
        while(True):
            # Check active trades
            for trade in trades:
                tradeInfo = trade.getTradeInfo()
                tradeValue = tradeInfo['coins'] * self.get_symbol_ticker(symbol=tradeInfo['currency'])
                if (1.1 * tradeInfo['paidAmount']) < tradeValue:
                    trade.closeTrade(tradeValue)
                    closedTrades.append(trade)
                    trades.remove(trade)
                    self.credit += tradeValue #Update credit avilable

            if self.credit/10 > 0: #Look for the crypo that has deviated the most of its average price 
                for crypto in targetedCryptos:
                    price = self.get_symbol_ticker(symbol=tradeInfo['currency'])
                    averagePrice = calculateAveragePrice()

            #TODO: cut loss ?     
            

            # TODO: Recalculate tradeUnits
            # TODO: Open new trades    

                            




bot = binanceBot(['ETHEUR'], 10000, "1 month ago UTC")
# bot.calculateAveragePrice()
# bot.startTrading()
# aux = trade (1, 'ETH', 0.019, 100.00)
# print(aux.getTradeInfo())