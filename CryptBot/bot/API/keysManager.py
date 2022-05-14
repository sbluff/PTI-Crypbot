import codecs
import os
from binance.client import Client
from binance import BinanceSocketManager

#define how to process incoming WebSocket messages
def btcTradeHistory(msg):
    btcPrice = {}
    if msg['e'] != 'error':
        print(msg['c'])
        btcPrice['current'] = msg['c']
        btcPrice['bid'] = msg['b']
        btcPrice['last'] = msg['a']
    else:
        btcPrice['error'] = True

def setWebSocket(client, bsm, symbol):
    bsm = BinanceSocketManager(client)
    connectionKeyBtc = bsm.start_symbol_ticker_socket(symbol, btcTradeHistory)
    bsm.start()
    return     

def initConection(client):
    keys = binanceKeysLoader()
    client = Client(keys[0], keys[1])
    socketManager = ''
    setWebSocket(client, socketManager, 'ETHUSDT')
    return  socketManager       


def binanceKeysLoader():
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, "binance-keys.txt"), "r") as fp:
        lines = []
        for line in fp:
            lines.append(line)
    if len(lines) == 2:
        keys = []
        for line in lines:
            first_quote = line.find("'");
            second_quote = line.find("'", int(first_quote)+1)
            keys.append(line[first_quote+1:second_quote])
        return keys
    else:
        raise Exception("The Binance API file didn't work as expected")

