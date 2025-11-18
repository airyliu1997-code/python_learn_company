#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
龙虎榜交易明细获取程序
通过Tushare的top_list接口获取当天龙虎榜交易数据，并对每个股票生成完整分析报告
"""

import os
import tushare as ts
import pandas as pd
from datetime import datetime
from datetime import timedelta
import time
import sys
from data_extractor import DataExtractor
from text_generator import TextGenerator
from content_integration import ContentIntegrator


def run_analysis(company_name, stock_code, output_dir, index=None):
    """
    执行数据分析和报告生成的函数
    """
    try:
        # 2. 提取数据 (使用DataExtractor)
        print(f"步骤2: 提取 {company_name}({stock_code}) 的公司数据...")
        data_extractor = DataExtractor()
        data_extractor_result = data_extractor.get_all_data(stock_code)

        # 3. 生成文本信息 (使用TextGenerator)
        print(f"步骤3: 生成 {company_name}({stock_code}) 的文本信息...")
        text_generator = TextGenerator(words_limit=500)

        # Extract financial data for better text generation
        financial_data = {
            'annual_revenue': data_extractor_result.get('annual_revenue', pd.DataFrame()).to_dict() if not data_extractor_result.get('annual_revenue', pd.DataFrame()).empty else {},
            'main_business_composition': data_extractor_result.get('main_business_composition', pd.DataFrame()),  # 传递DataFrame而不是字典，便于处理
            'top10_holders': data_extractor_result.get('top10_holders', pd.DataFrame())  # 传递前十大股东数据
        }

        # Extract management information
        management_info = data_extractor_result.get('management_info', None)

        text_generator_result = text_generator.generate_all_company_info(
            company_name=company_name,
            stock_code=stock_code,
            financial_data=financial_data,
            management_info=management_info
        )

        # 4. 整合内容 (使用ContentIntegrator)
        print(f"步骤4: 整合 {company_name}({stock_code}) 的内容并生成报告...")
        content_integrator = ContentIntegrator()
        # 临时修改输出目录
        original_output_dir = content_integrator.output_dir
        content_integrator.output_dir = output_dir

        report_path = content_integrator.integrate_content(
            company_name=company_name,
            stock_code=stock_code,
            data_extractor_result=data_extractor_result,
            text_generator_result=text_generator_result,
            index=index
        )

        print(f"\n{company_name}({stock_code}) 公司分析报告生成完成！")
        print(f"报告位置: {report_path}")

    except Exception as e:
        print(f"处理 {company_name}({stock_code}) 时发生错误: {e}")
        import traceback
        traceback.print_exc()


def get_toplist_data(today):
    """
    通过Tushare的top_list接口获取当天的龙虎榜交易明细
    """
    # 从环境变量获取Tushare token
    token = os.environ.get('TUSHARE_TOKEN')
    if not token:
        raise ValueError("TUSHARE_TOKEN环境变量未设置")

    # 设置token并初始化API
    ts.set_token(token)
    pro = ts.pro_api()

    try:
        # 调用top_list接口获取当天龙虎榜数据
        # 使用fields参数指定需要的字段
        fields = 'ts_code,name,pct_change,turnover_rate,net_amount,amount_rate,reason'
        df = pro.top_list(trade_date=today, fields=fields)
        
        if df.empty:
            return df
            
        #去除重复项
        df.drop_duplicates(subset=['name'], keep='first', inplace=True)
        #剔除北交所和转债
        df = df[df['ts_code'].str[:3].isin(['000', '300', '600', '688'])]
        #转化数据格式
        df["pct_change"] = df["pct_change"].map(lambda x: '{:,.2f}%'.format(x))
        df["turnover_rate"] = df["turnover_rate"].map(lambda x: '{:,.2f}%'.format(x))
        df["amount_rate"] = df["amount_rate"].map(lambda x: '{:,.2f}%'.format(x))
        df["net_amount"] = df["net_amount"].map(lambda x: '{:,.0f}M'.format(x/1000000))
        #按reason排序
        df.sort_values(by=["reason"], ascending=True, inplace=True)
        # 重置索引
        df.reset_index(drop=True, inplace=True)
        return df
    except Exception as e:
        print(f"获取龙虎榜数据时发生错误: {e}")
        return pd.DataFrame()


def save_toplist_data(df, date_str):
    """
    将龙虎榜数据保存为CSV文件

    Parameters:
    df: 龙虎榜数据DataFrame
    date_str: 日期字符串，格式为YYYYMMDD
    """
    # 创建日期文件夹路径
    base_dir = "/Users/airry/PythonS/python_learn_company/result"
    date_dir = os.path.join(base_dir, date_str)

    # 创建日期文件夹（如果不存在）
    os.makedirs(date_dir, exist_ok=True)

    # CSV文件名
    csv_filename = f"toplist_{date_str}.csv"
    csv_path = os.path.join(date_dir, csv_filename)

    # 保存数据到CSV文件
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')

    print(f"龙虎榜数据已保存到: {csv_path}")


def save_stock_list(df, date_str):
    """
    将龙虎榜中所有股票的代码和名称保存为txt格式

    Parameters:
    df: 龙虎榜数据DataFrame
    date_str: 日期字符串，格式为YYYYMMDD
    """
    if df.empty:
        print("龙虎榜数据为空，跳过保存股票列表")
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


def generate_reports_for_toplist(df, date_str):
    """
    为龙虎榜中的每只股票生成完整分析报告

    Parameters:
    df: 龙虎榜数据DataFrame
    date_str: 日期字符串，格式为YYYYMMDD
    """
    if df.empty:
        print("龙虎榜数据为空，跳过报告生成")
        return

    total_stocks = len(df)
    print(f"\n开始为龙虎榜中的 {total_stocks} 只股票生成分析报告...")
    print("="*60)

    # 创建日期文件夹
    output_base_dir = "/Users/airry/PythonS/python_learn_company/result"
    output_date_dir = os.path.join(output_base_dir, date_str)
    os.makedirs(output_date_dir, exist_ok=True)

    start_time = time.time()

    for index, row in df.iterrows():
        current_stock = index + 1
        stock_code = row['ts_code']
        stock_name = row['name']
        
        print(f"\n[{current_stock}/{total_stocks}] 正在处理: {stock_name}({stock_code})")
        
        try:
            run_analysis(stock_name, stock_code, output_date_dir, index=index+1)
        except Exception as e:
            print(f"处理 {stock_name}({stock_code}) 时发生错误: {e}")
            import traceback
            traceback.print_exc()
            continue

    end_time = time.time()
    total_duration = end_time - start_time
    print("="*60)
    print(f"所有报告生成完成！")
    print(f"总共处理了 {total_stocks} 只股票")
    print(f"总耗时: {total_duration:.2f} 秒")
    print(f"平均每个股票耗时: {total_duration/total_stocks:.2f} 秒")


def main():
    """
    主函数
    """
    # 获取当天（或几天前的）日期字符串
    today = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

    print(f"正在获取{today}的龙虎榜数据...")

    # 获取龙虎榜数据
    df = get_toplist_data(today)

    # 检查数据是否为空
    if df.empty:
        print("今日龙虎榜尚未更新")
        return

    # 保存龙虎榜数据
    save_toplist_data(df, today)

    # 保存股票列表到txt文件
    save_stock_list(df, today)

    print(f"共获取到 {len(df)} 条龙虎榜交易记录")

    # 显示前几条数据作为预览
    print("\n数据预览:")
    print(df)

    # 为每只股票生成完整分析报告
    print(f"\n开始为 {len(df)} 只股票生成分析报告...")
    generate_reports_for_toplist(df, today)


if __name__ == "__main__":
    main()