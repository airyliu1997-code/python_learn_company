#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试extract_direct_post_content函数的改进逻辑
"""

import os
import sys
from bs4 import BeautifulSoup

# 添加当前目录到Python路径
sys.path.append('/Users/airry/PythonS/python_learn_company')

from doubao_websearch import extract_direct_post_content

# 读取示例文件进行测试
def test_extract_logic():
    # 读取示例文件内容
    with open('/Users/airry/PythonS/python_learn_company/web_sample1.txt', 'r', encoding='utf-8') as f:
        sample1_content = f.read()

    with open('/Users/airry/PythonS/python_learn_company/web_sample2.txt', 'r', encoding='utf-8') as f:
        sample2_content = f.read()

    # 使用BeautifulSoup解析示例内容
    soup1 = BeautifulSoup(sample1_content, 'html.parser')
    soup2 = BeautifulSoup(sample2_content, 'html.parser')

    # 测试新逻辑
    print("测试示例1提取逻辑:")
    detail_content1 = soup1.find('div', class_='mt40 fsDetail noneSelect')
    if detail_content1:
        div_tags = detail_content1.find_all('div')

        result = {}
        for idx, tag in enumerate(div_tags):
            text = tag.get_text(strip=True)  # strip=True去除首尾空格和换行
            if '涨跌幅' in text:
                result['涨跌幅'] = text
            elif '涨停时间' in text:
                result['涨停时间'] = text
            elif '板块异动原因：' in text:
                # 板块异动原因的内容在当前标签的下一个兄弟标签中
                if idx+1 < len(div_tags):
                    result['板块异动原因'] = div_tags[idx+1].get_text(strip=True, separator='\n')
            elif '个股异动解析：' in text:
                # 个股异动解析的内容在当前标签内的pre-line类标签中
                pre_line_tag = tag.find('div', class_='pre-line')
                if pre_line_tag:
                    result['个股异动解析'] = pre_line_tag.get_text(strip=True, separator='\n')

        print("提取结果:")
        if '涨跌幅' in result:
            print("涨跌幅:", result['涨跌幅'])
        if '涨停时间' in result:
            print("涨停时间:", result['涨停时间'])
        if '板块异动原因' in result:
            print("板块异动原因:", result['板块异动原因'])
        if '个股异动解析' in result:
            print("个股异动解析:", result['个股异动解析'])

    print("\n" + "="*50 + "\n")

    print("测试示例2提取逻辑:")
    detail_content2 = soup2.find('div', class_='mt40 fsDetail noneSelect')
    if detail_content2:
        div_tags = detail_content2.find_all('div')

        result = {}
        for idx, tag in enumerate(div_tags):
            text = tag.get_text(strip=True)  # strip=True去除首尾空格和换行
            if '涨跌幅' in text:
                result['涨跌幅'] = text
            elif '涨停时间' in text:
                result['涨停时间'] = text
            elif '板块异动原因：' in text:
                # 板块异动原因的内容在当前标签的下一个兄弟标签中
                if idx+1 < len(div_tags):
                    result['板块异动原因'] = div_tags[idx+1].get_text(strip=True, separator='\n')
            elif '个股异动解析：' in text:
                # 个股异动解析的内容在当前标签内的pre-line类标签中
                pre_line_tag = tag.find('div', class_='pre-line')
                if pre_line_tag:
                    result['个股异动解析'] = pre_line_tag.get_text(strip=True, separator='\n')

        print("提取结果:")
        if '涨跌幅' in result:
            print("涨跌幅:", result['涨跌幅'])
        if '涨停时间' in result:
            print("涨停时间:", result['涨停时间'])
        if '板块异动原因' in result:
            print("板块异动原因:", result['板块异动原因'])
        if '个股异动解析' in result:
            print("个股异动解析:", result['个股异动解析'])

def test_function():
    """测试函数的模拟运行"""
    print("\n" + "="*50)
    print("测试模拟函数提取逻辑:")

    # 创建一个模拟文章页面进行测试
    sample_html = '''<!doctype html>
<html>
  <body>
    <div class="jc-home">
      <div class="detail-container">
        <div class="jc-parent">
          <div class="fs28-bold mb28">12月12日航天动力股票异动解析</div>
          <section>
            <div unselectable="on" onselectstart="return false;" class="mt40 fsDetail noneSelect">
              <div>涨跌幅：10.01%（6天4板）</div>
              <div>涨停时间：14:26:39</div>
              <div class="mt30">板块异动原因：</div>
              <div class="text-justify">商业航天；1、2025年12月10盘前消息，SpaceX拟最快于2026年中后期IPO，募资超300亿美元，估值约1.5万亿美元。</div>
              <div class="mt30" style="display:;">
                个股异动解析：
                <div class="pre-line">液体火箭发动机+航天六院唯一证券化平台+水电站
1、公司控股股东是航天六院，是中国液体火箭发动机研制中心，是中国唯一的集运载火箭主动力系统、轨姿控动力系统及空间飞行器推进系统研究、设计、生产、试验为一体的专业研究院，公司当前主要业务均源自于航天液体动力技术。</div>
              </div>
            </div>
            <div class="mt15 textTip text-justify">
              声明：解析内容由公社人工采集整理自新闻、公告、研报等公开信息，团队辛苦编写，未经许可严禁转载。站内所有文章均不构成投资建议，请投资者注意风险，独立审慎决策。
            </div>
          </section>
        </div>
      </div>
    </div>
  </body>
</html>'''

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(sample_html, 'html.parser')

    # 模拟函数内部逻辑
    detail_content = soup.find('div', class_='mt40 fsDetail noneSelect')
    if detail_content:
        div_tags = detail_content.find_all('div')

        result = {}
        for idx, tag in enumerate(div_tags):
            text = tag.get_text(strip=True)  # strip=True去除首尾空格和换行
            if '涨跌幅' in text:
                result['涨跌幅'] = text
            elif '涨停时间' in text:
                result['涨停时间'] = text
            elif '板块异动原因：' in text:
                # 板块异动原因的内容在当前标签的下一个兄弟标签中
                if idx+1 < len(div_tags):
                    result['板块异动原因'] = div_tags[idx+1].get_text(strip=True, separator='\n')
            elif '个股异动解析：' in text:
                # 个股异动解析的内容在当前标签内的pre-line类标签中
                pre_line_tag = tag.find('div', class_='pre-line')
                if pre_line_tag:
                    result['个股异动解析'] = pre_line_tag.get_text(strip=True, separator='\n')

        # 组装结果
        formatted_result = []
        if '涨跌幅' in result:
            formatted_result.append(result['涨跌幅'])
            formatted_result.append("")  # 添加换行
        if '涨停时间' in result:
            formatted_result.append(result['涨停时间'])
            formatted_result.append("")  # 添加换行
        if '板块异动原因' in result:
            formatted_result.append(f"板块异动原因：")
            formatted_result.append(result['板块异动原因'])
            formatted_result.append("")  # 添加换行
        if '个股异动解析' in result:
            formatted_result.append(f"个股异动解析：")
            formatted_result.append(result['个股异动解析'])
            formatted_result.append("")  # 添加换行

        if formatted_result:
            print("完整提取结果:")
            print('\n'.join(formatted_result))

if __name__ == "__main__":
    test_extract_logic()
    test_function()