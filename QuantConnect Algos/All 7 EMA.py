from clr import AddReference
AddReference("System")
AddReference("QuantConnect.Algorithm")
AddReference("QuantConnect.Common")

from System import *
from QuantConnect import *
from QuantConnect.Algorithm import *
from QuantConnect.Brokerages import *
from QuantConnect.Orders import *
from QuantConnect.Indicators import *
import pandas as pd
import numpy as np
import decimal as d

class EmaCross(QCAlgorithm):

    def Initialize(self):
        
        self.SetStartDate(2018, 1, 1)
        self.SetEndDate(2018, 12, 31)

        self.SetCash(100000)

        self.SetBrokerageModel(BrokerageName.GDAX, AccountType.Cash)

        '''
        You can uncomment the following lines when live trading with GDAX,
        to ensure limit orders will only be posted to the order book and never executed as a taker (incurring fees).
        Please note this statement has no effect in backtesting or paper trading.
        self.DefaultOrderProperties = GDAXOrderProperties()
        self.DefaultOrderProperties.PostOnly = True
        '''
        #@TODO add EMAs and make two sigmas
        eth = self.AddCrypto("ETHUSD", Resolution.Minute).Symbol
        ltc = self.AddCrypto("LTCUSD", Resolution.Minute).Symbol
        btc = self.AddCrypto("BTCUSD", Resolution.Minute).Symbol

        # moving averages
        self.eth_fast = self.EMA(ltc, 7, Resolution.Minute)
        self.eth_slow = self.EMA(ltc, 30, Resolution.Minute)
        
        self.ltc_fast = self.EMA(ltc, 7, Resolution.Minute)
        self.ltc_slow = self.EMA(ltc, 30, Resolution.Minute)
        
        self.btc_fast = self.EMA(btc, 7, Resolution.Minute)
        self.btc_slow = self.EMA(btc, 30, Resolution.Minute)

    def OnData(self, data):
        if self.Time.hour == 14:
        #(self.Time.hour >= 14 or self.Time.hour <= 15) or (self.Time.hour >= 17 or self.Time.hour <= 18):
            # Get current USD available, subtracting amount reserved for buy open orders
            usdTotal = self.Portfolio.CashBook["USD"].Amount
            usdReserved = sum(x.Quantity * x.LimitPrice for x
                in [x for x in self.Transactions.GetOpenOrders()
                    if x.Direction == OrderDirection.Buy
                        and x.Type == OrderType.Limit
                        and (x.Symbol.Value == "BTCUSD" or x.Symbol.Value == "ETHUSD")])
            usdAvailable = usdTotal - usdReserved
            self.Debug("usdAvailable: {}".format(usdAvailable))

            limitPrice = round(self.Securities["BTCUSD"].Price * d.Decimal(0.95), 2)

            # use all of our available USD
            quantity = usdAvailable / limitPrice
            
            quantity = usdAvailable * d.Decimal(1) / limitPrice
            

            if self.btc_fast > self.btc_slow or self.eth_fast > self.eth_slow or self.ltc_fast > self.ltc_slow:
                
                #or eth.btc_fast > self.eth_slow or elf.ltc_fast > self.ltc_slow:
                if self.btc_fast > self.eth_fast and self.btc_fast > self.ltc_fast:
                    if self.Portfolio.CashBook["BTC"].Amount == 0:
                           self.LimitOrder("BTCUSD", quantity, limitPrice)
                           
                if self.eth_fast > self.btc_fast and self.eth_fast > self.ltc_fast:
                    if self.Portfolio.CashBook["ETH"].Amount == 0:
                           self.LimitOrder("ETHUSD", quantity, limitPrice)
                           
                if self.ltc_fast > self.btc_fast and self.ltc_fast > self.eth_fast:
                    if self.Portfolio.CashBook["ETH"].Amount == 0:
                           self.LimitOrder("ETHUSD", quantity, limitPrice)
                           
                           
            else:
                if self.Portfolio.CashBook["BTC"].Amount > 0:
                        self.SetHoldings("BTCUSD", 0)
                        
                if self.Portfolio.CashBook["ETH"].Amount > 0:
                        self.SetHoldings("ETHUSD", 0)
                        
                if self.Portfolio.CashBook["LTC"].Amount > 0:
                        self.SetHoldings("LTCUSD", 0)
                    
                    
        elif self.Time.hour == 19:
            if self.Portfolio.CashBook["BTC"].Amount > 0:
                    self.SetHoldings("BTCUSD", 0)
                    
            if self.Portfolio.CashBook["ETH"].Amount > 0:
                    self.SetHoldings("ETHUSD", 0)
                    
            if self.Portfolio.CashBook["LTC"].Amount > 0:
                    self.SetHoldings("LTCUSD", 0)
            
    '''
    This was removed because a full back test with this over a year made too many logs and would get force stopped. :(
    It might have been just part of the problem but its working now so im not going back.
    '''
    # def OnOrderEvent(self, orderEvent):
    #     self.Debug("{} {}".format(self.Time, orderEvent.ToString()))
    # def OnEndOfAlgorithm(self):
    #     self.Log("{} - TotalPortfolioValue: {}".format(self.Time, self.Portfolio.TotalPortfolioValue))