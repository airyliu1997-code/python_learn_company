import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os
from datetime import datetime, timedelta
import matplotlib
import base64
from io import BytesIO
matplotlib.use('Agg')  # Use non-interactive backend
# 设置字体，解决中文乱码问题
plt.rcParams["font.family"] = ["Heiti TC"]
# 解决负号显示问题（可选）
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

class KLineGenerator:
    def __init__(self):
        # Get token from environment variable
        token = os.environ.get('TUSHARE_TOKEN')
        if not token:
            raise ValueError("TUSHARE_TOKEN环境变量未设置")
        
        ts.set_token(token)
        self.pro = ts.pro_api()

    def get_stock_data(self, stock_code, months=6):
        """
        获取股票的行情数据
        """
        # 计算开始日期
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months*30)  # 近似6个月
        
        start_date_str = start_date.strftime('%Y%m%d')
        end_date_str = end_date.strftime('%Y%m%d')
        
        # 获取日线数据
        df = self.pro.daily(
            ts_code=stock_code,
            start_date=start_date_str,
            end_date=end_date_str,
            fields='trade_date,open,high,low,close,vol,amount'
        )
        
        # 按日期排序（升序）- 最早日期在前，最新日期在后。reset_index确保时序正常
        df = df.sort_values(by='trade_date').reset_index(drop=True)
        # 因子提取复权，准备处理前复权
        adj_df = self.pro.adj_factor(ts_code=stock_code,start_date=start_date_str,end_date=end_date_str)
        # 复权因子按时间升序排序
        adj_df = adj_df.sort_values(by="trade_date").reset_index(drop=True)
        # 获取最新一天的复权因子（最后一行）
        latest_adj = adj_df.iloc[-1]["adj_factor"]  
        # 将后复权因子转化为前复权因子（让最新一天的因子为1）
        adj_df["norm_adj_factor"] = adj_df["adj_factor"] / latest_adj
        df = df.merge(adj_df[["trade_date","norm_adj_factor"]],on="trade_date",how="left")
        # 进行前复权计算
        df["open"] = df["open"] * df["norm_adj_factor"]
        df["high"] = df["high"] * df["norm_adj_factor"]
        df["low"] = df["low"] * df["norm_adj_factor"]
        df["close"] = df["close"] * df["norm_adj_factor"]
        # 转换日期格式
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        return df

    def plot_kline(self, stock_code, company_name):
        """
        绘制K线图，返回base64编码的图片，不保存文件
        """
        # 获取数据
        data = self.get_stock_data(stock_code)
        
        if data.empty:
            print(f"未能获取到 {stock_code} 的数据")
            return None

        # 创建图像，分为上下两个子图
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                       gridspec_kw={'height_ratios': [3, 1]})
        
        # 设置标题
        fig.suptitle(f'{company_name}({stock_code}) K线图 (最近6个月)', fontsize=16)
        
        # 使用索引作为x轴，确保交易日连续 ( oldest date on left, newest on right)
        x = range(len(data))  # 索引位置列表
        opens = data['open'].values
        highs = data['high'].values
        lows = data['low'].values
        closes = data['close'].values
        
        # 蜡烛图部分
        # 绘制蜡烛图 - 根据涨跌设置颜色
        for i in range(len(data)):
            open_price = opens[i]
            high_price = highs[i]
            low_price = lows[i]
            close_price = closes[i]
            
            # 判断涨跌 - 收盘价大于开盘价为涨（红色），否则为跌（绿色）
            color = 'red' if close_price >= open_price else 'green'
            
            # 绘制最高价到最低价的线（影线）
            ax1.plot([x[i], x[i]], [low_price, high_price], color=color, linewidth=0.5)
            
            # 绘制开盘价到收盘价的实体（蜡烛）
            bottom = min(open_price, close_price)
            top = max(open_price, close_price)
            ax1.bar(x[i], top - bottom, width=0.8, bottom=bottom, 
                   color=color, alpha=0.8, edgecolor=color, linewidth=0.3)
        
        # 设置上图的属性
        ax1.set_ylabel('价格', fontsize=12)
        ax1.grid(True, linestyle='--', alpha=0.6, axis='y')
        ax1.set_title('K线图', fontsize=14)
        
        # 添加价格均线
        # 使用x轴索引绘制均线
        ax1.plot(x, data['close'].rolling(window=5).mean(), label='5日均线', color='orange', linewidth=1)
        ax1.plot(x, data['close'].rolling(window=20).mean(), label='20日均线', color='purple', linewidth=1)
        ax1.legend(loc='best')
        
        # 成交额图部分
        amount = data['amount'].values/100000  # 成交额（亿元）原单位为千元
        colors = ['red' if closes[i] >= opens[i] else 'green' for i in range(len(data))]
        
        ax2.bar(x, amount, color=colors, alpha=0.7, width=0.8)
        ax2.set_ylabel('成交额(亿元)', fontsize=12)
        ax2.grid(True, linestyle='--', alpha=0.6, axis='y')
        ax2.set_title('成交额图', fontsize=14)
        
        # 设置X轴标签，使用实际日期 - 每隔10个交易日显示一个日期
        date_labels = data['trade_date'].dt.strftime('%m-%d')
        step = max(1, len(date_labels) // 10)  # 确保最多显示10个日期标签
        visible_dates = [date_labels[i] if i % step == 0 else '' for i in range(len(date_labels))]
        # Set the same x-axis for both subplots
        ax1.set_xticks(x)  # Ensure both subplots have the same x-axis ticks
        ax1.set_xticklabels(visible_dates, rotation=45, ha='right')
        ax2.set_xticks(x)  # 刻度位置与索引对应
        ax2.set_xticklabels(visible_dates, rotation=45, ha='right')  # 仅显示部分日期以避免拥挤
  
        # 调整布局
        plt.tight_layout()
        
        # 将图像保存到字节流中并转换为base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()  # 关闭图形以释放内存
        return f"data:image/png;base64,{image_base64}"


def main():
    """
    主函数，演示K线图生成功能
    """
    try:
        # 示例股票代码
        generator = KLineGenerator()
        # 使用一个示例股票进行测试
        sample_stock_code = "600749.SH"  # 西藏旅游
        sample_company_name = "西藏旅游"
        
        result_path = generator.plot_kline(sample_stock_code, sample_company_name)
        if result_path:
            print(f"K线图生成成功")
        else:
            print("K线图生成失败")
    except Exception as e:
        print(f"K线图生成失败: {e}")


if __name__ == "__main__":
    main()