from openai import OpenAI
import os


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
    # 从环境变量中获取您的API KEY，配置方法见：https://www.volcengine.com/docs/82379/1399008
    api_key = os.getenv('ARK_API_KEY')
    client = OpenAI(
        base_url='https://ark.cn-beijing.volces.com/api/v3',
        api_key=api_key
    )

    tools = [{
        "type": "web_search",
    }]

    # 创建一个对话请求
    response = client.responses.create(
        model="doubao-seed-1-6-251015",
        input=[
            {"role": "system", "content": "你是一名专业投资人，擅长通过网络搜索获取最新的股票市场信息"},
            {"role": "user", "content": f"{stock_code}{stock_name}{date}股价异动的底层原因和事件催化。不需要进行总结"}
        ],
        tools=tools,
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
    result = get_stock_abnormal_info('000973.SZ', '佛塑科技', '2025年11月17日')
    if result:
        print("提取的text结果：")
        print(result)
    else:
        print("获取信息失败")