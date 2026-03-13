from AlgorithmImports import *

class SimpleMeanReversion(QCAlgorithm):
    
    def Initialize(self):
        self.SetStartDate(2015, 1, 1)   # 回测开始日期，可改
        self.SetEndDate(2025, 12, 31)   # 结束日期（或留空跑最新）
        self.SetCash(100000)            # 初始资金
        
        # 添加资产（这里用 SPY，你可以换成其他股票/ETF/期货）
        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
        
        # 指标
        self.sma = self.SMA(self.symbol, 50, Resolution.Daily)     # 50日均线
        self.std = self.STD(self.symbol, 20, Resolution.Daily)     # 20日标准差
        
        # 滚动窗口存收盘价（用于手动算 z-score，如果想更灵活）
        self.price_window = RollingWindow[float](50)               # 存最近50天价格
        
        # 交易参数（可调）
        self.entry_z = 1.5      # 进场 z-score 阈值（越大信号越少但越强）
        self.exit_z  = 0.2      # 出场 z-score 阈值（接近0平仓）
        
        self.position = 0       # 当前持仓方向：1 long, -1 short, 0 flat
        
        self.Debug("Mean Reversion Strategy Initialized")

    def OnData(self, data: Slice):
        if not data.Bars.ContainsKey(self.symbol):
            return
        
        bar = data.Bars[self.symbol]
        self.price_window.Add(bar.Close)
        
        # 确保窗口满了再交易
        if not (self.sma.IsReady and self.std.IsReady and self.price_window.IsReady):
            return
        
        # 当前价格
        price = bar.Close
        
        # 计算 z-score = (price - mean) / std
        mean = self.sma.Current.Value
        std_val = self.std.Current.Value
        if std_val == 0: return  # 防除零
        
        z_score = (price - mean) / std_val
        
        # 交易逻辑
        if self.position == 0:  # 当前无仓
            if z_score < -self.entry_z:
                # 严重低估 → 买入
                self.SetHoldings(self.symbol, 1.0)   # 全仓买入（可改成 0.5 等）
                self.position = 1
                self.Debug(f"BUY at {price:.2f} | z={z_score:.2f}")
                
            elif z_score > self.entry_z:
                # 严重高估 → 卖空
                self.SetHoldings(self.symbol, -1.0)  # 全仓卖空
                self.position = -1
                self.Debug(f"SHORT at {price:.2f} | z={z_score:.2f}")
        
        elif self.position == 1:  # 持有多头
            if z_score > -self.exit_z:   # 回到均值附近
                self.Liquidate(self.symbol)
                self.position = 0
                self.Debug(f"EXIT LONG at {price:.2f} | z={z_score:.2f}")
        
        elif self.position == -1:  # 持有空头
            if z_score < self.exit_z:    # 回到均值附近
                self.Liquidate(self.symbol)
                self.position = 0
                self.Debug(f"EXIT SHORT at {price:.2f} | z={z_score:.2f}")