import os
import sys
import pandas as pd
from stock_code_matcher import StockCodeMatcher
from data_extractor import DataExtractor
from text_generator import TextGenerator
from content_integration import ContentIntegrator


def run_analysis(company_name, stock_code):
    """
    执行数据分析和报告生成的函数
    """
    try:
        # 2. 提取数据 (使用DataExtractor)
        print("步骤2: 提取公司数据...")
        data_extractor = DataExtractor()
        data_extractor_result = data_extractor.get_all_data(stock_code)
        
        # 3. 生成文本信息 (使用TextGenerator)
        print("步骤3: 生成文本信息...")
        text_generator = TextGenerator(words_limit=50)

        # Extract financial data for better text generation
        financial_data = {
            'annual_revenue': data_extractor_result.get('annual_revenue', {}).to_dict() if not data_extractor_result.get('annual_revenue', pd.DataFrame()).empty else {},
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
        print("步骤4: 整合内容并生成报告...")
        content_integrator = ContentIntegrator()
        report_path = content_integrator.integrate_content(
            company_name=company_name,
            stock_code=stock_code,
            data_extractor_result=data_extractor_result,
            text_generator_result=text_generator_result
        )
        
        print(f"\n公司分析报告生成完成！")
        print(f"报告位置: {report_path}")
        
    except Exception as e:
        print(f"程序执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


def main():
    """
    主程序，调用所有模块生成最终的公司分析报告
    """
    print("开始运行公司分析系统...")
    
    try:
        # 1. 获取公司名称和股票代码 using the GUI from stock_code_matcher
        print("步骤1: 通过GUI获取公司名称和股票代码...")
        csv_file_path = os.path.join(os.path.dirname(__file__), 'stock_names.csv')
        
        if not os.path.exists(csv_file_path):
            print(f"错误: 找不到文件 {csv_file_path}")
            company_name = input("请输入公司名称: ").strip()
            stock_code = input("请输入股票代码 (格式如: 000001.SZ): ").strip()
            
            if company_name and stock_code:
                run_analysis(company_name, stock_code)
            else:
                print("未提供有效的公司名称或股票代码")
        else:
            # Initialize the stock code matcher
            matcher = StockCodeMatcher(csv_file_path)
            
            # Show GUI for user input
            print("启动GUI界面以获取公司名称和股票代码...")
            
            # We'll create a simple callback to continue the process after GUI
            def process_with_gui():
                # For now, we'll just provide instructions
                print("\n" + "="*60)
                print("注意: GUI界面是阻塞的，无法直接获取返回值")
                print("请在GUI中查询到股票代码后，关闭GUI窗口")
                print("然后输入公司名称和股票代码以继续分析:")
                print("="*60)
                
                company_name = input("请输入公司名称: ").strip()
                if company_name:
                    stock_code = matcher.find_stock_code(company_name)
                    if stock_code:
                        print(f"找到股票代码: {stock_code}")
                        run_analysis(company_name, stock_code)
                    else:
                        print(f"未找到 {company_name} 的股票代码，请检查名称是否正确")
                else:
                    print("未输入公司名称")
            
            process_with_gui()
        
    except Exception as e:
        print(f"程序执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()