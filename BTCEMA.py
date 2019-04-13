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

class ETHEMACross(QCAlgorithm):

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
        BTC = self.AddCrypto("BTCUSD", Resolution.Minute).Symbol
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
            usdTotal = self.Portfolio.CashBook["USD"].Amount
            usdReserved = sum(x.Quantity * x.LimitPrice for x
                in [x for x in self.Transactions.GetOpenOrders()
                    if x.Direction == OrderDirection.Buy
                        and x.Type == OrderType.Limit
                        and (x.Symbol.Value == "BTCUSD" or x.Symbol.Value == "BTCUSD")])
            usdAvailable = usdTotal - usdReserved
            self.Debug("usdAvailable: {}".format(usdAvailable))

            limitPrice = round(self.Securities["BTCUSD"].Price * d.Decimal(0.98), 2)

            # use all of our available USD
            quantity = usdAvailable / limitPrice

            # use only half of our available USD
            quantity = usdAvailable * d.Decimal(1) / limitPrice

            if self.btc_fast > self.btc_slow:
                if self.Portfolio.CashBook["BTC"].Amount == 0:
                       self.LimitOrder("BTCUSD", quantity, limitPrice)
            else:
                if self.Portfolio.CashBook["BTC"].Amount > 0:

                    self.SetHoldings("BTCUSD", 0)

                    
        elif self.Time.hour == 19:
            if self.Portfolio.CashBook["BTC"].Amount > 0:
                    self.SetHoldings("BTCUSD", 0)
                    # self.SetHoldings("LTCUSD", 0)
            
    # def OnOrderEvent(self, orderEvent):
    #     self.Debug("{} {}".format(self.Time, orderEvent.ToString()))
    # def OnEndOfAlgorithm(self):
    #     self.Log("{} - TotalPortfolioValue: {}".format(self.Time, self.Portfolio.TotalPortfolioValue))