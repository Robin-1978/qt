import yfinance as yf
import talib as ta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class QuantTradingFramework:
    def __init__(self, symbol, start, end, initial_cash=100000):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.data = self.get_data()
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.position = 0  # 持仓数量
        self.trades = []   # 交易记录
        self.current_value = initial_cash

    def get_data(self):
        """获取历史数据"""
        data = yf.download(self.symbol, self.start, self.end)
        data.dropna(inplace=True)
        return data

    def add_indicators(self):
        """添加技术指标"""
        self.data['MA20'] = ta.SMA(self.data['Close'], timeperiod=20)  # 20日均线
        self.data['RSI'] = ta.RSI(self.data['Close'], timeperiod=14)  # 相对强弱指数
        self.data['MACD'], self.data['MACD_signal'], _ = ta.MACD(self.data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)  # MACD

    def strategy(self):
        """简单的交易策略：基于均线交叉和RSI超买超卖"""
        buy_signals = []
        sell_signals = []
        for i in range(1, len(self.data)):
            if self.data['Close'].iloc[i] > self.data['MA20'].iloc[i] and self.data['RSI'].iloc[i] < 30:
                # 买入信号：价格上穿20日均线且RSI低于30
                if self.position == 0:
                    self.buy(self.data.index[i], self.data['Close'].iloc[i])
                    buy_signals.append(self.data.index[i])
            elif self.data['Close'].iloc[i] < self.data['MA20'].iloc[i] and self.data['RSI'].iloc[i] > 70:
                # 卖出信号：价格下穿20日均线且RSI高于70
                if self.position > 0:
                    self.sell(self.data.index[i], self.data['Close'].iloc[i])
                    sell_signals.append(self.data.index[i])
        return buy_signals, sell_signals

    def buy(self, date, price):
        """执行买入操作"""
        num_shares = self.cash // price
        self.cash -= num_shares * price
        self.position += num_shares
        self.trades.append({'Date': date, 'Type': 'Buy', 'Price': price, 'Shares': num_shares})
        print(f"买入: {num_shares} 股, 每股价格: {price}， 日期: {date}")

    def sell(self, date, price):
        """执行卖出操作"""
        if self.position > 0:
            self.cash += self.position * price
            self.trades.append({'Date': date, 'Type': 'Sell', 'Price': price, 'Shares': self.position})
            print(f"卖出: {self.position} 股, 每股价格: {price}， 日期: {date}")
            self.position = 0

    def calculate_portfolio_value(self):
        """计算当前的组合价值"""
        self.current_value = self.cash + (self.position * self.data['Close'].iloc[-1])
        return self.current_value

    def backtest(self):
        """回测策略"""
        self.add_indicators()
        buy_signals, sell_signals = self.strategy()
        
        # 绘制交易信号图
        plt.figure(figsize=(14,7))
        plt.plot(self.data.index, self.data['Close'], label='Close Price', alpha=0.5)
        plt.plot(self.data.index, self.data['MA20'], label='20-Day MA', alpha=0.5)
        plt.scatter(buy_signals, self.data.loc[buy_signals]['Close'], marker='^', color='green', label='Buy Signal', alpha=1)
        plt.scatter(sell_signals, self.data.loc[sell_signals]['Close'], marker='v', color='red', label='Sell Signal', alpha=1)
        plt.title(f'{self.symbol} Backtest')
        plt.legend()
        plt.show()

        # 打印最终结果
        final_value = self.calculate_portfolio_value()
        print(f"初始资金: {self.initial_cash}")
        print(f"回测结束后账户余额: {self.cash}")
        print(f"最终持仓价值: {self.position * self.data['Close'].iloc[-1]}")
        print(f"最终组合总价值: {final_value}")

if __name__ == '__main__':
    # 示例：回测苹果股票从2020年到2023年的数据
    framework = QuantTradingFramework('AAPL', '2020-01-01', '2023-01-01')
    framework.backtest()