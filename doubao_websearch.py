import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
from Jiuyan_spider import JiuYanGongSheSpider, get_valid_cookie
from datetime import datetime


def extract_direct_post_content(stock_name, date_str):
    """
    尝试直接从韭研公社搜索特定的解析帖子

    Args:
        stock_name (str): 股票名称
        date_str (str): 日期字符串，格式为 'm月n日'，例如 '11月17日'

    Returns:
        str or None: 如果找到帖子则返回帖子内容，否则返回None
    """
    import time
    import random

    # 构建搜索URL - FIXED: Include date_str in search query
    search_url = f"https://www.jiuyangongshe.com/search/new?k={date_str}{stock_name}股票异动解析"

    # 获取cookie并设置请求头
    cookie = get_valid_cookie()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
    }

    cookies = {}
    for pair in cookie.split(';'):
        if '=' in pair:
            name, value = pair.strip().split('=', 1)
            cookies[name] = value

    # 尝试最多3次提取
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"尝试提取帖子 (第 {attempt + 1} 次)...")

            # 发送搜索请求
            response = requests.get(search_url, headers=headers, cookies=cookies)
            response.raise_for_status()

            # 解析搜索结果页面
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找标题为 '{date_str}{stock_name}股票异动解析' 的帖子链接
            target_title = f"{date_str}{stock_name}股票异动解析"

            # FIXED: More robust approach based on HTML structure analysis
            # Find all article entries (li elements)
            article_items = soup.find_all('li')

            target_link = None
            for item in article_items:
                # Look for the highlights-text span that contains the target title
                title_spans = item.find_all(class_=lambda x: x and 'highlights-text' in x if x else False)
                found_target_title = False
                for title_span in title_spans:
                    if target_title in title_span.get_text():
                        found_target_title = True
                        break

                if found_target_title:
                    # Look for article links within this specific item (starting with '/a/')
                    article_links = item.find_all('a', href=lambda x: x and x.startswith('/a/'))
                    if article_links:
                        # Take the first article link in this item
                        target_link = article_links[0]['href']
                        break

            # If not found using the optimized method, try a backup approach
            if not target_link:
                # Find all elements with the target title text
                title_elements = soup.find_all(string=lambda text: text and target_title in text)
                for title_text in title_elements:
                    # Find the parent element containing this title
                    parent_elem = title_text.parent
                    # Go up the tree to find the article container
                    while parent_elem and parent_elem.name != 'body':
                        # Look for article links within this container (only those starting with /a/)
                        article_links = parent_elem.find_all('a', href=lambda x: x and x.startswith('/a/'))
                        if article_links:
                            target_link = article_links[0]['href']
                            break
                        parent_elem = parent_elem.parent
                    if target_link:
                        break

            if not target_link:
                # Final fallback: Look for links that start with /a/ and have the target title somewhere nearby
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    if link['href'].startswith('/a/') and target_title in link.get_text():
                        target_link = link['href']
                        break

            if target_link:
                # 构建完整的文章URL
                if target_link.startswith('/'):
                    full_url = f"https://www.jiuyangongshe.com{target_link}"
                else:
                    full_url = target_link

                # 访问目标文章页面
                article_response = requests.get(full_url, headers=headers, cookies=cookies)
                article_response.raise_for_status()

                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                # 使用新逻辑提取内容
                detail_content = article_soup.find('div', class_='mt40 fsDetail noneSelect')
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
                        print(f"成功获取 {target_title} 的帖子内容，并按新逻辑提取")
                        return '\n'.join(formatted_result)

                # 如果新逻辑没有提取到内容，则使用旧逻辑
                print("新逻辑未提取到内容，使用旧逻辑...")

                # 尝试提取文章正文内容，根据可能的HTML结构进行查找
                # 常见的正文内容容器类名
                content_selectors = [
                    '.article-content', '.content', '.main-content', '.article-body',
                    '.post-content', '.entry-content', '[class*="content"]',
                    '[class*="article"]', '[class*="post"]', '.jc-home',
                    '.detail-content', '.content-body'
                ]

                content = None
                for selector in content_selectors:
                    content_elem = article_soup.select_one(selector)
                    if content_elem:
                        # 保留换行格式，不使用strip=True
                        content = content_elem.get_text()
                        break

                # 如果没有找到，尝试查找所有段落
                if not content:
                    paragraphs = article_soup.find_all('p')
                    if paragraphs:
                        # 用换行符连接段落，保留格式
                        content = '\n'.join([p.get_text() for p in paragraphs])

                # 如果仍未找到，尝试查找所有div内容
                if not content:
                    divs = article_soup.find_all(['div', 'section'])
                    for div in divs:
                        div_text = div.get_text()
                        if len(div_text) > 100:  # 选择内容较长的div
                            content = div_text
                            break

                if content:
                    # 提取有效内容部分：从'涨跌幅：'开始，到'基础设施和运营服务的需要。'结束
                    start_marker = "涨跌幅："
                    end_marker = "基础设施和运营服务的需要。"

                    start_idx = content.find(start_marker)
                    end_idx = content.find(end_marker)

                    if start_idx != -1 and end_idx != -1:
                        # 找到标记，提取有效内容
                        end_idx += len(end_marker)  # 包含结束标记
                        extracted_content = content[start_idx:end_idx]

                        # 进一步清理内容，去除不需要的部分
                        # 查找并截断到声明部分
                        disclaimer_marker = "声明：解析内容由公社人工采集整理"
                        disclaimer_pos = extracted_content.find(disclaimer_marker)
                        if disclaimer_pos != -1:
                            extracted_content = extracted_content[:disclaimer_pos].strip()

                        print(f"成功获取 {target_title} 的帖子内容，并提取有效部分")
                        return extracted_content.strip()
                    elif start_idx != -1:
                        # 只找到开始标记，从开始标记处提取内容
                        extracted_content = content[start_idx:]

                        # 查找并截断到声明部分
                        disclaimer_marker = "声明：解析内容由公社人工采集整理"
                        disclaimer_pos = extracted_content.find(disclaimer_marker)
                        if disclaimer_pos != -1:
                            extracted_content = extracted_content[:disclaimer_pos].strip()

                        print(f"成功获取 {target_title} 的帖子内容，并从指定位置提取")
                        return extracted_content.strip()
                    else:
                        # 没有找到标记，返回原始内容
                        print(f"成功获取 {target_title} 的帖子内容，但未找到预期标记，返回完整内容")
                        return content.strip()
                else:
                    print(f"找到了 {target_title} 的链接，但未能提取正文内容")
            else:
                print(f"未找到标题为 '{target_title}' 的帖子")

            # 如果是最后一次尝试仍未成功，则跳出循环
            if attempt == max_retries - 1:
                print("已达到最大尝试次数，未找到帖子")
                return None

            # 延时3-8秒再试
            delay = random.uniform(3, 8)
            print(f"等待 {delay:.2f} 秒后进行下一次尝试...")
            time.sleep(delay)

        except Exception as e:
            print(f"第 {attempt + 1} 次尝试时发生错误: {e}")
            if attempt == max_retries - 1:
                print("已达到最大尝试次数，未找到帖子")
                return None
            # 延时3-8秒再试
            delay = random.uniform(3, 8)
            print(f"等待 {delay:.2f} 秒后进行下一次尝试...")
            time.sleep(delay)

    return None


def get_stock_abnormal_info(stock_code, stock_name, date):
    """
    获取股票异动信息

    Args:
        stock_code (str): 股票代码，例如 '000973.SZ'
        stock_name (str): 股票名称，例如 '佛塑科技'
        date (str): 查询日期，格式为 'YYYY年MM月DD日'，例如 '2025年11月17日'

    Returns:
        str: 股票异动原因的分析结果，如果查询失败则返回None
    """
    # 将日期格式从 'YYYY年MM月DD日' 转换为 'M月D日' 格式
    try:
        # 解析日期
        dt_obj = datetime.strptime(date, '%Y年%m月%d日')
        date_str = dt_obj.strftime('%-m月%-d日')  # 使用%-m和%-d来获取不带前导零的月份和日期
    except:
        # 如果解析失败，尝试其他格式
        try:
            date_str = date.replace('年', '').replace('月', '月').replace('日', '日')
            # 简单去除前导零
            parts = date_str.split('月')
            month = str(int(parts[0]))
            day = parts[1].replace('日', '')
            date_str = f"{month}月{int(day)}日"
        except:
            print(f"日期格式解析失败: {date}")
            date_str = date

    # 首先尝试直接搜索特定的解析帖子
    print(f"尝试搜索 {date_str}{stock_name}股票异动解析 的帖子...")
    direct_content = extract_direct_post_content(stock_name, date_str)

    if direct_content:
        print("成功获取到指定的解析帖子内容，直接返回")
        return direct_content
    else:
        print(f"未找到 {date_str}{stock_name}股票异动解析 的帖子，使用原有逻辑...")

    # 如果没有找到特定的帖子，则按原有逻辑运行
    # 获取韭研公社的相关帖子内容
    print(f"正在爬取 {stock_name} 在韭研公社的相关帖子...")
    cookie = get_valid_cookie()
    spider = JiuYanGongSheSpider(cookie)
    jiuyan_content = spider.crawl_stock_posts(stock_name)

    # 从环境变量中获取您的API KEY，配置方法见：https://www.volcengine.com/docs/82379/1399008
    api_key = os.getenv('ARK_API_KEY')
    client = OpenAI(
        base_url='https://ark.cn-beijing.volces.com/api/v3',
        api_key=api_key
    )

    # 创建一个对话请求，包含从韭研公社获取的内容作为上下文
    response = client.responses.create(
        model="doubao-seed-1-6-251015",
        input=[
            {"role": "system", "content": "你是一名专业投资人，擅长分析股票市场信息"},
            {"role": "user", "content": f"以下是我在网络上搜集到的关于{stock_name}的最新资讯：\n\n{jiuyan_content}\n\n基于以上信息，提炼{stock_code}{stock_name}{date}股价异动的主要原因。注意关注发帖时间，判断帖子的时效性"},
        ],
        temperature=0.4
    )

    # 从response中提取text内容
    if response.output and len(response.output) > 0:
        # 获取output中的消息对象（通常是最后一个output元素）
        output_message = response.output[-1]
        # 从消息对象的content中提取text（content是列表，取第一个元素的text）
        if output_message.content and len(output_message.content) > 0:
            answer_text = output_message.content[0].text
            return answer_text
        else:
            print("未找到content中的text内容")
            return None
    else:
        print("未找到有效的output内容")
        return None


# 示例调用
if __name__ == "__main__":
    result = get_stock_abnormal_info('600693.SH', '东百集团', '2025年12月11日')
    if result:
        print("提取的text结果：")
        print(result)
    else:
        print("获取信息失败")