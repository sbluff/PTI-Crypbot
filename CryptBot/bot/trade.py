from datetime import datetime
from typing import Sized
from binance.exceptions import BinanceAPIException, BinanceOrderException
import requests


binanceRestApiUrl = 'https://api.binance.com/api/v3/avgPrice?symbol='
requestHeaders = {'user-agent': 'my-app/0.0.1'}

#
class trade:
   def __init__(self, client, data, action, cursor):
      self.cursor = cursor
      self.id = data[0]
      self.currency = data[1]
      self.entryPrice = data[2]
      self.paidAmount = str(data[3])
      self.status = data[4]
      self.balance = data[5]
      self.sellAmount = data[6]
      self.startDate = data[7]
      self.closeDate = data[8] 
      self.exitPrice = data[9]
      self.mode = data[10]
      self.credit = data[11] 
      self.coins = data[12]
      self.client = client
      if action == 'create':
         self.writeDb()
         if self.mode == 'prod':
            self.placeOrder()

   #Stores the objet's data in the db    
   def writeDb(self):
      sql = "INSERT INTO trades (id, startDate, crypto, entryPrice, entryAmount, number_coins, status, mode, credit) VALUE " + "(" + str(self.id) + "," + "'" + str(self.startDate) + "'" + "," + "'" + self.currency + "'" + "," + str(self.entryPrice) + "," + str(self.paidAmount) + "," + str(self.coins) + "," + "'" + self.status + "'" + "," + "'" + self.mode + "'" +  "," + str(self.credit) + ")"
      self.cursor.execute(sql)

   #This method places a close order on the binance api
   def closeTrade(self, tradeValue, exitPrice):
      self.status = "closed"
      self.exitPrice = exitPrice
      self.closeDate = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
      self.sellAmount = tradeValue
      self.balance = self.sellAmount - float(self.paidAmount)
      sql = "UPDATE trades SET closeDate=" + "'" + self.closeDate + "'"  + ",status= " + "'" + self.status + "'" + ",sellAmount= " + str(self.sellAmount) + ",exitPrice= " + str(self.exitPrice) + ", balance= " + str(self.balance) + "WHERE id=" + str(self.id)
      self.cursor.execute(sql)
      
      sql = "SELECT credit FROM trades where id = (select MAX(id) from trades)"       
      self.cursor.execute(sql)
      credit = self.cursor.fetchone()
      sql = "SELECT MAX(id) FROM trades"       
      self.cursor.execute(sql)
      id = self.cursor.fetchone()[0]
      sql = "UPDATE trades SET credit =" + str(float(credit[0]) + float(tradeValue)) + " id = " + str(id)

      if self.mode == "prod":
         result = self.client.order_market_sell(symbol=self.currency, quantity=self.coins)
         print(result)

   #This method places a buy order on the binance api
   def placeOrder(self):
      # create a real order if the test orders did not raise an exception
      try:
         print(self.currency + " COINS:" + str(self.coins))
         order = self.client.create_order(
               symbol=self.currency,
               side='BUY',
               type='MARKET',
               quantity=self.coins,
         )
         print(order) 

      except BinanceAPIException as e:
         # error handling goes here
         print(e)
         exit()
      except BinanceOrderException as e:
         # error handling goes here
         print(e)
         exit()

   #Displays information related to the trade and its status
   def printInfo(self):
      print("Trade #" + str(self.id) + " started on: " + str(self.startDate))
      print("Bought " + str(self.coins) + " of " + self.currency + " at " + str(self.entryPrice) + "USDT")
      if self.status == 'closed':
         print("Closed at " + self.closeDate)
         print("Sold " + str(self.coins) + " of " + self.currency + " for " + str(self.sellAmount) + "USDT")
         print("BALANCE: " + str(self.balance))
      print('-----------------------------------')
   
   #Returns a dictionary containing: status, currency, coins, paidAmount, currentPrice, currentValue(open trades), balance(closed trades)
   def getTradeData(self):
      currentPrice = float((requests.get(binanceRestApiUrl + self.currency, headers=requestHeaders)).json()['price'])
      currentValue = float(self.coins) * currentPrice
      if self.status == 'opened':
         result = {
            'status': self.status,
            'currency': self.currency,
            'coins': self.coins,
            'paidAmount': self.paidAmount,
            'currentPrice': currentPrice,
            'currentValue': currentValue
         }

      elif self.status == 'closed':
         result = {
            'status': self.status,
            'currency': self.currency,
            'coins': self.coins,
            'paidAmount': self.paidAmount,
            'balance': self.balance,
            'currentPrice': currentPrice,
         }

      return result   