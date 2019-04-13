from clr import AddReference
AddReference("System")
AddReference("QuantConnect.Algorithm")
AddReference("QuantConnect.Common")

from System import *
from QuantConnect import *
from QuantConnect.Algorithm import *
from QuantConnect.Brokerages import *
from QuantConnect.Orders import *
import pandas as pd
import numpy as np
import decimal as d

class BollingerBreakoutAlgorithm(QCAlgorithm):

    def Initialize(self):

        self.SetStartDate(2018, 1, 1) 
        self.SetEndDate(2018, 12, 31) 
        self.SetCash(10000) 
        self.SetBrokerageModel(BrokerageName.GDAX, AccountType.Cash)
        self.AddCrypto("BTCUSD", Resolution.Daily)
        
        self.Bolband = self.BB("BTCUSD", 20, 2, MovingAverageType.Simple, Resolution.Daily)


    def OnData(self, data):
        
        usdTotal = self.Portfolio.CashBook["USD"].Amount
        usdReserved = sum(x.Quantity * x.LimitPrice for x
            in [x for x in self.Transactions.GetOpenOrders()
                if x.Direction == OrderDirection.Buy
                    and x.Type == OrderType.Limit
                    and (x.Symbol.Value == "BTCUSD" or x.Symbol.Value == "BTCUSD")])
        usdAvailable = usdTotal - usdReserved
        self.Debug("usdAvailable: {}".format(usdAvailable))

        limitPrice = round(self.Securities["BTCUSD"].Price * d.Decimal(0.98), 2)

        quantity = usdAvailable / limitPrice

        quantity = usdAvailable * d.Decimal(0.5) / limitPrice
            
        holdings = self.Portfolio["BTCUSD"].Quantity
        price = self.Securities["BTCUSD"].Close
        
        if holdings <= 0:
             if price > self.Bolband.LowerBand.Current.Value:
                if self.Portfolio.CashBook["BTC"].Amount == 0:
                       self.LimitOrder("BTCUSD", quantity, limitPrice)
                       
        if holdings > 0 and price < self.Bolband.MiddleBand.Current.Value:
                self.SetHoldings("BTCUSD", 0)