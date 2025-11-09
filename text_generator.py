import os
import json
from typing import Dict, Optional
from http import HTTPStatus
import dashscope  # Alibaba Cloud Qwen SDK
import markdown


class TextGenerator:
    def __init__(self):
        """
        初始化文本生成器
        从环境变量中获取阿里云API密钥
        """
        # 从环境变量获取阿里云API KEY
        api_key = os.environ.get('DASHSCOPE_API_KEY')
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY环境变量未设置")
        
        dashscope.api_key = api_key
        print("成功初始化阿里云Qwen API客户端")

    def generate_income_structure_info(self, company_name: str, financial_data: Optional[Dict] = None) -> str:
        """
        生成公司收入结构和主要收入贡献来源的信息
        """
        # 只提取主营业务构成数据，避免传递过多无关信息
        main_bz_data = "无主营业务构成数据"
        if financial_data and isinstance(financial_data, dict):
            # 从financial_data中提取main_business_composition部分
            main_bz_composition = financial_data.get('main_business_composition', None)
            if main_bz_composition is not None and hasattr(main_bz_composition, 'to_dict'):
                # 如果是DataFrame，转换为适合输出的格式
                try:
                    # 取主要的收入结构相关字段，包括报告期
                    required_cols = ['报告期', '业务项目', '业务收入', '收入占比']
                    if not main_bz_composition.empty and all(col in main_bz_composition.columns for col in required_cols):
                        # 只取关键字段并转换为字典
                        selected_data = main_bz_composition[required_cols].dropna()
                        if not selected_data.empty:
                            simplified_records = selected_data.to_dict('records')
                            main_bz_data = json.dumps({
                                'main_business_composition': simplified_records
                            }, ensure_ascii=False, indent=2)
                        else:
                            main_bz_data = "无主营业务构成数据"
                    else:
                        # 如果DataFrame没有预期的列，尝试包含报告期在内的所有可用列
                        if '报告期' in main_bz_composition.columns:
                            # 至少包含报告期和业务项目
                            available_cols = ['报告期', '业务项目']
                            for col in ['业务收入', '收入占比', '业务利润', '毛利率']:
                                if col in main_bz_composition.columns:
                                    available_cols.append(col)
                            selected_data = main_bz_composition[available_cols]
                            main_bz_data = json.dumps(selected_data.to_dict('records'), ensure_ascii=False, indent=2)
                        else:
                            # 如果没有报告期列，直接转换整个DataFrame
                            main_bz_data = json.dumps(main_bz_composition.to_dict('records'), ensure_ascii=False, indent=2)
                except Exception as e:
                    main_bz_data = f"主营业务构成数据处理错误: {str(e)}"
            elif main_bz_composition is not None:
                # 如果不是DataFrame，直接使用
                main_bz_data = json.dumps(main_bz_composition, ensure_ascii=False, indent=2)
        
        prompt = f"""
        请联网搜索并分析{company_name}的收入结构和主要收入贡献来源。基于以下主营业务构成数据（如果提供）：
        
        {main_bz_data}
        
        请从以下角度详细分析：
        1. 主要收入来源（产品/服务线/地区）
        2. 各收入来源的占比情况
        3. 收入结构的变化趋势

        我是一名专业的投资人，请提供专业、详细的分析内容，如果不确定具体信息，请联网进行搜索。
        """
        
        return self._call_qwen_api(prompt)

    def generate_history_and_founder_info(self, company_name: str, management_info=None) -> str:
        """
        生成公司发展历史沿革和创始人背景信息
        """
        # 整理管理层信息，用于提供给模型
        management_details = ""
        if management_info is not None:
            # 检查是否为DataFrame类型
            if hasattr(management_info, 'to_dict'):
                # 如果是DataFrame，转换为字典格式
                try:
                    # 取前10条记录以避免上下文过长
                    records = management_info.head(10).to_dict('records')
                    management_details = "当前管理层信息：\n"
                    for record in records:
                        name = record.get('name', '未知')
                        gender = record.get('gender', '未知')
                        lev = record.get('lev', '未知')  # 职务级别
                        title = record.get('title', '未知')  # 职位名称
                        edu = record.get('edu', '未知')  # 学历
                        national = record.get('national', '未知')  # 国籍
                        birthday = record.get('birthday', '未知')  # 生日
                        begin_date = record.get('begin_date', '未知')  # 任职开始日期
                        end_date = record.get('end_date', '未知')  # 任职结束日期
                        resume = record.get('resume', '无详细简历')  # 简历
                        
                        management_details += f"- {name} ({title})，性别：{gender}，级别：{lev}，学历：{edu}，国籍：{national}，生日：{birthday}，任职期间：{begin_date}至{end_date}，简历：{resume}\n"
                except:
                    management_details = "当前管理层信息：无法解析的管理层数据"
            else:
                management_details = "当前管理层信息：非DataFrame格式数据"
        else:
            management_details = "无管理层信息"
        
        prompt = f"""
        请联网搜索并详细介绍{company_name}的发展历史沿革和创始人的背景，内容需要尽可能详细，包括：
        
        1. 公司创立背景和初衷
        2. 创始人是谁，创始团队成员有哪些。创始人的教育背景、职业经历
        3. 重要发展阶段和里程碑事件，对近五年的情况时间颗粒度要细化
        4. 关键转型或业务扩展节点，对近五年的情况时间颗粒度要细化
        
        当前管理层信息作为参考：
        {management_details}
        
        请提供详尽的内容，如果部分具体历史信息不确定，请基于行业背景进行合理推测。
        """
        
        return self._call_qwen_api(prompt)

    def generate_customer_and_sales_info(self, company_name: str, industry_info: Optional[str] = None) -> str:
        """
        生成公司下游主要客户构成和销售模式的信息
        """
        prompt = f"""
        请联网搜索并详细分析{company_name}的下游主要客户构成和销售模式：
        
        行业背景信息：
        {industry_info if industry_info else "无具体行业背景信息"}
        
        请从以下角度详细分析：
        1. 下游主要客户类型和构成
        2. 主要销售渠道和分销模式
        3. 产业链上下游的基本情况
        
        我是一名专业的投资人，请提供专业、详细的分析内容，如果不确定具体信息，请基于行业常识进行合理推测。
        """
        
        return self._call_qwen_api(prompt)

    def generate_shareholders_info(self, company_name: str, stock_code: str, top10_holders_data=None) -> str:
        """
        生成公司前十大股东信息，包括持股比例超过5%的股东背景和股份变动情况
        """
        holders_info = "无前十大股东数据"
        if top10_holders_data is not None:
            # 检查是否为DataFrame类型
            if hasattr(top10_holders_data, 'to_dict'):
                try:
                    # 转换为字典格式，只取关键字段
                    required_cols = ['end_date', 'holder_name', 'hold_ratio', 'hold_change', 'holder_type']
                    available_cols = [col for col in required_cols if col in top10_holders_data.columns]
                    selected_data = top10_holders_data[available_cols].copy()
                    
                    # 只取非空数据
                    if not selected_data.empty:
                        holders_info = json.dumps(selected_data.to_dict('records'), ensure_ascii=False, indent=2)
                    else:
                        holders_info = "无前十大股东数据"
                except Exception as e:
                    holders_info = f"前十大股东数据处理错误: {str(e)}"
            else:
                holders_info = json.dumps(top10_holders_data, ensure_ascii=False, indent=2)
        prompt = f"""
        请基于{company_name}（股票代码：{stock_code}）的前十大股东数据，详细介绍该公司的股东结构：

        前十大股东数据：
        {holders_info}

        请从以下角度详细分析：
        1. 前十大股东分别是谁
        2. 对于其中持股比例超过5%的股东（排除公募基金），请介绍其背景
        3. 近期有什么大股东的股份重要变动

        请注意：
        - 如果数据中存在公募基金类型的股东，请忽略其背景介绍
        - 基于实际数据进行描述，不要编造信息
        - 如果数据中没有明确的持股变动信息，请明确说明

        我是一名专业的投资人，请提供专业、详细的分析内容。
        """

        return self._call_qwen_api(prompt)

    def _call_qwen_api(self, prompt: str, model: str = "qwen-plus") -> str:
        """
        调用阿里云Qwen API生成文本
        """
        try:
            response = dashscope.Generation.call(
                model=model,
                prompt=prompt,
                result_format='message',  # 设置返回格式为message
                max_tokens=1000,  # 限制最大token数
                temperature=0.75,  # 控制生成的随机性
            )
            
            if response.status_code == HTTPStatus.OK:
                # 提取生成的文本内容
                if hasattr(response, 'output') and 'choices' in response.output:
                    content = response.output['choices'][0]['message']['content']
                    # 将markdown格式转换为HTML格式，以便在HTML中正确显示
                    html_content = markdown.markdown(content, extensions=['extra', 'codehilite', 'toc', 'tables', 'fenced_code'])
                    return html_content
                else:
                    print(f"API响应格式异常: {response}")
                    return f"API响应格式异常: {response}"
            else:
                print(f"API调用失败，状态码: {response.status_code}, 错误信息: {response.message}")
                return f"API调用失败: {response.message}"
                
        except Exception as e:
            print(f"调用Qwen API时发生错误: {e}")
            return f"API调用错误: {e}"

    def generate_all_company_info(self, company_name: str, stock_code: str, 
                                financial_data: Optional[Dict] = None, 
                                industry_info: Optional[str] = None,
                                management_info: Optional[Dict] = None) -> Dict[str, str]:
        """
        生成所有公司信息
        """
        print(f"开始为公司 {company_name} (股票代码: {stock_code}) 生成文本信息...")
        
        # 生成收入结构信息
        print("正在生成收入结构信息...")
        income_structure_info = self.generate_income_structure_info(company_name, financial_data)
        
        # 生成历史和创始人信息（现在传入管理层信息）
        print("正在生成公司历史沿革和创始人背景信息...")
        history_info = self.generate_history_and_founder_info(company_name, management_info)
        
        # 生成客户和销售信息
        print("正在生成客户构成和销售模式信息...")
        customer_sales_info = self.generate_customer_and_sales_info(company_name, industry_info)
        
        # 生成前十大股东信息
        print("正在生成前十大股东信息...")
        top10_holders_data = financial_data.get('top10_holders', None) if financial_data else None
        shareholders_info = self.generate_shareholders_info(company_name, stock_code, top10_holders_data)
        
        # 将生成的信息保存到字典中
        generated_info = {
            'company_name': company_name,
            'stock_code': stock_code,
            'income_structure_info': income_structure_info,
            'history_info': history_info,
            'customer_sales_info': customer_sales_info,
            'shareholders_info': shareholders_info
        }
        
        print("文本信息生成完成！")
        return generated_info


def main():
    """
    主函数，用于测试文本生成器
    """
    try:
        # 初始化文本生成器
        generator = TextGenerator()
        
        # 示例公司名称和股票代码
        company_name = "潍柴动力"
        stock_code = "000338.SZ"
        
        # 调用生成函数
        result = generator.generate_all_company_info(company_name, stock_code)
        
        # 打印结果概览
        print("\n=== 生成结果概览 ===")
        print(f"公司名称: {result['company_name']}")
        print(f"股票代码: {result['stock_code']}")
        print(f"收入结构信息长度: {len(result['income_structure_info'])} 字符")
        print(f"历史信息长度: {len(result['history_info'])} 字符")
        print(f"客户销售信息长度: {len(result['customer_sales_info'])} 字符")
        
        # 保存生成的信息到文件以备后续使用
        output_file = f"{company_name}_generated_info.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n生成的信息已保存到: {output_file}")
        
    except Exception as e:
        print(f"执行过程中发生错误: {e}")


if __name__ == "__main__":
    main()