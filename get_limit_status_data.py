import os
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

TUSHARE_TOKEN = os.getenv("TUSHARE_TOKEN")
pro = ts.pro_api(TUSHARE_TOKEN)

def get_limit_status_data(minus_days=2, day_range=10):
    """
    获取股票涨跌停状态数据

    Parameters:
    minus_days (int): 设置为1表示获取昨天的数据，默认为2（获取2天前的数据）
    day_range (int): 定义查询的天数范围，默认为10天

    Returns:
    pandas.DataFrame: 包含股票代码、名称和连续涨跌停状态的DataFrame
    """
    # 获取目标日期
    target_date = datetime.now() - timedelta(days=minus_days)

    # 定义一个函数来判断涨跌停状态
    def judge_limit_status(row):
        if pd.isna(row['up_limit']) or pd.isna(row['down_limit']):
            return '未涨跌停'
        if row['close'] >= row['up_limit']:
            return '涨停'
        elif row['close'] <= row['down_limit']:
            return '跌停'
        elif row['high'] >= row['up_limit'] and row['close'] < row['up_limit']:
            if row['change'] >= 0:
                return '炸板'
            else:
                return '大面'
        elif row['low'] <= row['down_limit'] and row['close'] > row['down_limit']:
            if row['change'] <= 0:
                return '翘板'
            else:
                return '反攻'
        else:
            return '未涨跌停'

    # 获取最近十天的涨跌停状态
    limit_status_table = pro.stock_basic(exchange='', list_status='L', fields=['ts_code','name'])
    for i in reversed(range(day_range)):  # reversed确保日期从远到近
        date = (target_date - timedelta(days=i)).strftime('%Y%m%d')
        df_limit = pro.stk_limit(trade_date=date)
        df_price = pro.daily(trade_date=date)
        # 合并数据以便判断涨跌停状态
        df_merged = pd.merge(
        df_price,
        df_limit,
        on=['ts_code', 'trade_date'],
        how='left'
    )
        if not df_merged.empty:
            df_merged[date] = df_merged.apply(judge_limit_status,axis=1)
            limit_status_table = pd.merge(
            limit_status_table,
            df_merged[['ts_code', date]],
            on='ts_code',
            how='left'
        )

    # 判断连续涨跌停状态的函数
    def judge_consecutive_status(row):
        date = target_date.strftime('%Y%m%d')
        if row[date] == '未涨跌停':
            return '未涨跌停'
        elif row[date] == '炸板':
            return '炸板'
        elif row[date] == '翘板':
            return '翘板'
        elif row[date] == '反攻':
            return '反攻'
        elif row[date] == '大面':
            return '大面'
        elif row[date] == '涨停':
            count = 0
            for i in range(day_range):
                check_date = (target_date - timedelta(days=i)).strftime('%Y%m%d')
                if check_date in row and row[check_date] == '涨停':
                    count += 1. # count是连续涨停的天数
                else:
                    break
            count = int(count) # 不然会出现2.0连板的情况
            up_limit_num = row.eq('涨停').sum() # 计算总共涨停的天数
            first_up_limit_date = row.eq('涨停').argmax()  # 获取第一次涨停的日期索引
            up_limit_days = len(row) - first_up_limit_date # 计算从第一次涨停到现在的总天数,+2是因为有ts_code和name两列
            if up_limit_num == 1:
                return f'首板'
            elif count == up_limit_num:
                return f'{count}连板'
            else:
                return f'{up_limit_days}天{up_limit_num}板'
        elif row[date] == '跌停':
            count = 0
            for i in range(day_range):
                check_date = (target_date - timedelta(days=i)).strftime('%Y%m%d')
                if check_date in row and row[check_date] == '跌停':
                    count += 1
                else:
                    break
            return f'{count}连跌停板'

    if not limit_status_table.empty:
        limit_status_table['连板状态'] = limit_status_table.apply(judge_consecutive_status,axis=1)
    limit_status_table = limit_status_table.dropna() # nan是由于提取的基础股票list和提取交易日数据不匹配导致的，有些股票停牌了
    limit_status_table = limit_status_table[limit_status_table['连板状态'] != '未涨跌停']# 把不是涨跌停的股票删除
    limit_status_table = limit_status_table[['ts_code','name','连板状态']] # 只保留这三列
    final_result = limit_status_table.sort_values(by=['连板状态']).reset_index(drop=True)# 按照涨停状态排序

    return final_result

# Example usage of the function
if __name__ == "__main__":
    result = get_limit_status_data(minus_days=2, day_range=10)
    print(result)