#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
涨跌停股票分析报告生成程序
获取指定日期的涨跌停股票清单，并为指定连板状态的股票生成完整分析报告
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from get_limit_status_data import get_limit_status_data
from toplist_main import run_analysis
import sys

def save_limit_status_data(df, date_str):
    """
    将涨跌停数据保存为CSV文件

    Parameters:
    df: 涨跌停数据DataFrame
    date_str: 日期字符串，格式为YYYYMMDD
    """
    # 创建日期文件夹路径
    base_dir = "/Users/airry/PythonS/python_learn_company/result"
    date_dir = os.path.join(base_dir, date_str)

    # 创建日期文件夹（如果不存在）
    os.makedirs(date_dir, exist_ok=True)

    # CSV文件名
    csv_filename = f"limit_status_{date_str}.csv"
    csv_path = os.path.join(date_dir, csv_filename)

    # 保存数据到CSV文件
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')

    print(f"涨跌停数据已保存到: {csv_path}")


def save_stock_list(df, date_str):
    """
    将涨跌停股票的代码和名称保存为txt格式

    Parameters:
    df: 涨跌停数据DataFrame
    date_str: 日期字符串，格式为YYYYMMDD
    """
    if df.empty:
        print("涨跌停数据为空，跳过保存股票列表")
        return

    # 创建日期文件夹路径
    base_dir = "/Users/airry/PythonS/python_learn_company/result"
    date_dir = os.path.join(base_dir, date_str)

    # 创建日期文件夹（如果不存在）
    os.makedirs(date_dir, exist_ok=True)

    # TXT文件名
    txt_filename = "股票列表.txt"
    txt_path = os.path.join(date_dir, txt_filename)

    # 保存股票代码和名称到TXT文件
    with open(txt_path, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            stock_code = row['ts_code']
            stock_name = row['name']
            f.write(f"{stock_code}\t{stock_name}\n")

    print(f"股票列表已保存到: {txt_path}")


def get_user_selection(unique_statuses):
    """
    获取用户选择的连板状态
    
    Parameters:
    unique_statuses: 可用的连板状态列表
    
    Returns:
    用户选择的连板状态
    """
    print("\n请选择需要进行分析的连板状态:")
    for i, status in enumerate(unique_statuses, 1):
        print(f"{i}. {status}")
    
    while True:
        try:
            choice = input(f"\n请输入选项编号 (1-{len(unique_statuses)}): ")
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(unique_statuses):
                return unique_statuses[choice_index]
            else:
                print(f"请输入有效的选项编号 (1-{len(unique_statuses)})")
        except ValueError:
            print("请输入有效的数字")


def generate_reports_for_limit_stocks(df, date_str, selected_status):
    """
    为指定连板状态的股票生成完整分析报告

    Parameters:
    df: 涨跌停数据DataFrame
    date_str: 日期字符串，格式为YYYYMMDD
    selected_status: 用户选择的连板状态
    """
    # 筛选出指定连板状态的股票
    selected_df = df[df['连板状态'] == selected_status].reset_index(drop=True)
    
    if selected_df.empty:
        print(f"没有找到连板状态为 '{selected_status}' 的股票")
        return

    total_stocks = len(selected_df)
    print(f"\n开始为连板状态为 '{selected_status}' 的 {total_stocks} 只股票生成分析报告...")
    print("="*60)

    # 创建日期文件夹
    output_base_dir = "/Users/airry/PythonS/python_learn_company/result"
    output_date_dir = os.path.join(output_base_dir, date_str)
    os.makedirs(output_date_dir, exist_ok=True)

    for index, row in selected_df.iterrows():
        current_stock = index + 1
        stock_code = row['ts_code']
        stock_name = row['name']
        consecutive_status = row['连板状态']

        print(f"\n[{current_stock}/{total_stocks}] 正在处理: {stock_name}({stock_code}) - {consecutive_status}")

        try:
            # 调用toplist_main.py中的run_analysis函数生成报告
            run_analysis(stock_name, stock_code, output_date_dir, index=index+1)
        except Exception as e:
            print(f"处理 {stock_name}({stock_code}) 时发生错误: {e}")
            import traceback
            traceback.print_exc()
            continue

    print("="*60)
    print(f"连板状态为 '{selected_status}' 的股票报告生成完成！")
    print(f"总共处理了 {total_stocks} 只股票")


def main():
    """
    主函数
    """
    # 设置minus_days参数，控制获取哪天的数据
    minus_days = 2  # 默认获取2天前的数据，可以根据需要调整
    
    # 获取目标日期
    target_date = (datetime.now() - timedelta(days=minus_days)).strftime('%Y%m%d')

    print(f"正在获取{target_date}的涨跌停数据...")

    # 获取涨跌停数据
    df = get_limit_status_data(minus_days=minus_days, day_range=10)

    # 检查数据是否为空
    if df.empty:
        print("当日无涨跌停股票数据")
        return

    print(f"共获取到 {len(df)} 条涨跌停记录")

    # 保存涨跌停数据
    save_limit_status_data(df, target_date)

    # 保存股票列表到txt文件
    save_stock_list(df, target_date)

    # 显示数据预览
    print("\n涨跌停数据预览:")
    print(df)

    # 显示各连板状态的统计
    print("\n各连板状态统计:")
    status_counts = df['连板状态'].value_counts()
    for status, count in status_counts.items():
        print(f"  {status}: {count} 只")

    # 获取唯一连板状态列表，供用户选择
    unique_statuses = df['连板状态'].unique().tolist()
    
    # 询问用户选择需要分析的连板状态
    selected_status = get_user_selection(unique_statuses)

    # 为指定连板状态的股票生成分析报告
    print(f"\n开始为连板状态为 '{selected_status}' 的股票生成分析报告...")
    generate_reports_for_limit_stocks(df, target_date, selected_status)


if __name__ == "__main__":
    main()