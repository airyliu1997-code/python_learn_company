import os
import datetime
import pandas as pd
from typing import Dict, Any
from kline_generator import KLineGenerator


class ContentIntegrator:
    def __init__(self):
        """
        初始化内容整合模块
        """
        self.output_dir = "/Users/airry/PythonS/python_learn_company/result"
        os.makedirs(self.output_dir, exist_ok=True)  # Create directory if it doesn't exist

    def integrate_content(self, company_name: str, stock_code: str, 
                         data_extractor_result: Dict[str, Any], 
                         text_generator_result: Dict[str, str]) -> str:
        """
        整合所有内容并生成HTML格式的报告
        """
        # Get today's date
        today = datetime.datetime.now().strftime('%Y年%m月%d日')

        # Create HTML content
        html_content = []
        
        # HTML Header with basic styling
        html_content.append('<!DOCTYPE html>')
        html_content.append('<html lang="zh-CN">')
        html_content.append('<head>')
        html_content.append('    <meta charset="UTF-8">')
        html_content.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html_content.append('    <title>{}（{}）公司分析报告</title>'.format(company_name, stock_code))
        html_content.append('    <style>')
        html_content.append('        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }')
        html_content.append('        h1, h2, h3 { color: #333; }')
        html_content.append('        h1 { border-bottom: 2px solid #333; padding-bottom: 10px; }')
        html_content.append('        table { border-collapse: collapse; width: 100%; margin: 10px 0; }')
        html_content.append('        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }')
        html_content.append('        th { background-color: #f2f2f2; }')
        html_content.append('        .section { margin: 20px 0; }')
        html_content.append('        .subsection { margin: 15px 0; }')

        html_content.append('        .kline-image { width: 100%; max-width: 1000px; height: auto; margin: 20px 0; }')
        html_content.append('        strong { color: #444; }')
        html_content.append('    </style>')
        html_content.append('</head>')
        html_content.append('<body>')
        
        # 1. Title and subtitle
        html_content.append(f'    <h1>{company_name}（{stock_code}）</h1>')
        html_content.append(f'    <h2>{today}</h2>')

        # Generate and add K-line chart
        try:
            kline_generator = KLineGenerator()
            kline_base64 = kline_generator.plot_kline(stock_code, company_name)
            if kline_base64:
                html_content.append(f'    <div class="section">')
                html_content.append(f'        <h2>K线图分析</h2>')
                html_content.append(f'        <img src="{kline_base64}" class="kline-image" alt="K线图">')
                html_content.append(f'    </div>')
        except Exception as e:
            print(f"生成K线图时出错: {e}")
            html_content.append(f'    <div class="section">')
            html_content.append(f'        <h2>K线图分析</h2>')
            html_content.append(f'        <p>无法生成K线图: {e}</p>')
            html_content.append(f'    </div>')

        # 2. First section: Company introduction, main business, and history
        html_content.append('    <div class="section">')
        html_content.append('        <h2>公司概况</h2>')
        
        # Get company info from data extractor
        company_info = data_extractor_result.get('company_info', {})
        company_intro = company_info.get('introduction', 'N/A')
        main_business = company_info.get('main_business', 'N/A')
        
        # Get history info from text generator
        history_info = text_generator_result.get('history_info', 'N/A')
        
        html_content.append(f'        <p><strong>公司介绍：</strong> {company_intro}</p>')
        html_content.append(f'        <p><strong>主要业务和产品：</strong> {main_business}</p>')
        html_content.append('        <div class="subsection">')
        html_content.append('            <h3>公司历史沿革和创始人背景：</h3>')
        html_content.append(f'            {history_info}')
        html_content.append('        </div>')
        html_content.append('    </div>')

        # 3. Second section: Income structure and main_bz_data table
        html_content.append('    <div class="section">')
        html_content.append('        <h2>收入结构分析</h2>')
        
        # Get income structure info from text generator
        income_structure_info = text_generator_result.get('income_structure_info', 'N/A')
        html_content.append('        <div class="subsection">')
        html_content.append('            <h3>收入结构和主要收入贡献来源：</h3>')
        html_content.append(f'            {income_structure_info}')
        html_content.append('        </div>')
        
        # Add the main_bz_data table from data extractor
        main_bz_data = data_extractor_result.get('main_business_composition', pd.DataFrame())
        html_content.append('        <div class="subsection">')
        html_content.append('            <h3>主营业务构成数据表</h3>')
        if not main_bz_data.empty:
            html_content.append(self._df_to_html_table(main_bz_data))
        else:
            html_content.append('            <p>主营业务构成数据表：无数据</p>')
        html_content.append('        </div>')
        
        # 4. Additional section: Customer and sales information
        # Get customer and sales info from text generator
        customer_sales_info = text_generator_result.get('customer_sales_info', 'N/A')
        html_content.append('        <div class="subsection">')
        html_content.append('            <h3>客户构成和销售模式</h3>')
        html_content.append(f'            {customer_sales_info}')
        html_content.append('        </div>')
        html_content.append('    </div>')

        # 5. Third section: Various financial data tables
        html_content.append('    <div class="section">')
        html_content.append('        <h2>财务数据分析</h2>')
        
        # Annual income statement - Revenue
        annual_revenue = data_extractor_result.get('annual_revenue', pd.DataFrame())
        annual_indicators = data_extractor_result.get('annual_indicators', pd.DataFrame())
        if not annual_revenue.empty:
            html_content.append('        <div class="subsection">')
            html_content.append('            <h3>年度营业收入与营收增长率数据</h3>')

            
            # Combine revenue and growth data in the same table
            if not annual_indicators.empty and '年度营收增长率' in annual_indicators.columns:
                # Merge revenue and growth data
                combined_annual_revenue = annual_revenue.merge(
                    annual_indicators[['报告期', '年度营收增长率']], 
                    on='报告期', 
                    how='left'
                )
                combined_annual_revenue = combined_annual_revenue.rename(columns={'年度营收增长率': '年度营收增长率(%)'})
            else:
                combined_annual_revenue = annual_revenue.copy()
            html_content.append(self._df_to_html_table(combined_annual_revenue))
            html_content.append('        </div>')
        
        # Annual income statement - Net Profit
        annual_net_profit = data_extractor_result.get('annual_net_profit', pd.DataFrame())
        annual_indicators = data_extractor_result.get('annual_indicators', pd.DataFrame())
        if not annual_net_profit.empty:
            html_content.append('        <div class="subsection">')
            html_content.append('            <h3>年度归母净利润与利润增长率数据</h3>')

            
            # Combine net profit and growth data in the same table
            if not annual_indicators.empty and '年度利润增长率' in annual_indicators.columns:
                # Merge net profit and growth data
                combined_annual_net_profit = annual_net_profit.merge(
                    annual_indicators[['报告期', '年度利润增长率']], 
                    on='报告期', 
                    how='left'
                )
                combined_annual_net_profit = combined_annual_net_profit.rename(columns={'年度利润增长率': '年度利润增长率(%)'})
            else:
                combined_annual_net_profit = annual_net_profit.copy()
            html_content.append(self._df_to_html_table(combined_annual_net_profit))
            html_content.append('        </div>')
        
        # Quarterly income statement - Revenue
        quarterly_revenue = data_extractor_result.get('quarterly_revenue', pd.DataFrame())
        quarterly_indicators = data_extractor_result.get('quarterly_indicators', pd.DataFrame())
        if not quarterly_revenue.empty:
            html_content.append('        <div class="subsection">')
            html_content.append('            <h3>季度营业收入与营收增长率数据</h3>')

            
            # Combine quarterly revenue and growth data in the same table
            if not quarterly_indicators.empty and '营收同比增长率' in quarterly_indicators.columns and '营收环比增长率' in quarterly_indicators.columns:
                # Merge quarterly revenue and growth data
                combined_quarterly_revenue = quarterly_revenue.merge(
                    quarterly_indicators[['报告期', '营收同比增长率', '营收环比增长率']], 
                    on='报告期', 
                    how='left'
                )
                combined_quarterly_revenue = combined_quarterly_revenue.rename(columns={
                    '营收同比增长率': '季度营收同比增长率(%)',
                    '营收环比增长率': '季度营收环比增长率(%)'
                })
            else:
                combined_quarterly_revenue = quarterly_revenue.copy()
            html_content.append(self._df_to_html_table(combined_quarterly_revenue))
            html_content.append('        </div>')
        
        # Quarterly income statement - Net Profit
        quarterly_net_profit = data_extractor_result.get('quarterly_net_profit', pd.DataFrame())
        quarterly_indicators = data_extractor_result.get('quarterly_indicators', pd.DataFrame())
        if not quarterly_net_profit.empty:
            html_content.append('        <div class="subsection">')
            html_content.append('            <h3>季度归母净利润与利润增长率数据</h3>')

            
            # Combine quarterly net profit and growth data in the same table
            if not quarterly_indicators.empty and '利润同比增长率' in quarterly_indicators.columns and '利润环比增长率' in quarterly_indicators.columns:
                # Merge quarterly net profit and growth data
                combined_quarterly_net_profit = quarterly_net_profit.merge(
                    quarterly_indicators[['报告期', '利润同比增长率', '利润环比增长率']], 
                    on='报告期', 
                    how='left'
                )
                combined_quarterly_net_profit = combined_quarterly_net_profit.rename(columns={
                    '利润同比增长率': '季度利润同比增长率(%)',
                    '利润环比增长率': '季度利润环比增长率(%)'
                })
            else:
                combined_quarterly_net_profit = quarterly_net_profit.copy()
            html_content.append(self._df_to_html_table(combined_quarterly_net_profit))
            html_content.append('        </div>')
        
        # Annual cash flow statement
        annual_cashflow = data_extractor_result.get('annual_cashflow', pd.DataFrame())
        if not annual_cashflow.empty:
            html_content.append('        <div class="subsection">')
            html_content.append('            <h3>年度现金流量表数据</h3>')

            html_content.append(self._df_to_html_table(annual_cashflow))
            html_content.append('        </div>')
        
        # Quarterly cash flow statement
        quarterly_cashflow = data_extractor_result.get('quarterly_cashflow', pd.DataFrame())
        if not quarterly_cashflow.empty:
            html_content.append('        <div class="subsection">')
            html_content.append('            <h3>季度现金流量表数据</h3>')

            html_content.append(self._df_to_html_table(quarterly_cashflow))
            html_content.append('        </div>')
        
        # Annual financial indicators
        annual_indicators = data_extractor_result.get('annual_indicators', pd.DataFrame())
        if not annual_indicators.empty:
            html_content.append('        <div class="subsection">')
            html_content.append('            <h3>年度财务指标数据</h3>')

            html_content.append(self._df_to_html_table(annual_indicators))
            html_content.append('        </div>')
        
        # Quarterly financial indicators
        quarterly_indicators = data_extractor_result.get('quarterly_indicators', pd.DataFrame())
        if not quarterly_indicators.empty:
            html_content.append('        <div class="subsection">')
            html_content.append('            <h3>季度财务指标数据</h3>')

            html_content.append(self._df_to_html_table(quarterly_indicators))
            html_content.append('        </div>')
        
        html_content.append('    </div>')

        # 5. Fifth section: Market valuation metrics
        html_content.append('    <div class="section">')
        html_content.append('        <h2>市场估值指标</h2>')
        
        daily_market_data = data_extractor_result.get('daily_market_data', {})
        pe_ttm = daily_market_data.get('pe_ttm', 'N/A')
        pb = daily_market_data.get('pb', 'N/A')
        total_mv = daily_market_data.get('total_mv', 'N/A')
        trade_date = daily_market_data.get('trade_date', 'N/A')
        
        # 显示实际提取数据的日期
        if trade_date != 'N/A' and trade_date is not None:
            html_content.append(f'        <p>数据提取日期: {trade_date}</p>')
        else:
            html_content.append(f'        <p>数据提取日期: 无数据</p>')
        
        # Format market valuation metrics to one decimal place
        pe_ttm_formatted = f"{pe_ttm:.1f}" if pe_ttm is not None else 'N/A'
        pb_formatted = f"{pb:.1f}" if pb is not None else 'N/A'
        total_mv_formatted = f"{total_mv:.1f}" if total_mv is not None else 'N/A'
        
        html_content.append(f'        <p>公司当前市盈率（TTM）为 {pe_ttm_formatted}</p>')
        html_content.append(f'        <p>市净率为 {pb_formatted}</p>')
        html_content.append(f'        <p>总市值为 {total_mv_formatted} 亿元</p>')
        html_content.append('    </div>')

        # 6. Additional information
        html_content.append('    <div class="section">')
        html_content.append('        <h2>其他信息</h2>')
        
        city = company_info.get('city', 'N/A')
        website = company_info.get('website', 'N/A')
        
        html_content.append(f'        <ul>')
        html_content.append(f'            <li><strong>公司所在城市：</strong> {city}</li>')
        html_content.append(f'            <li><strong>公司网址：</strong> {website}</li>')
        html_content.append(f'        </ul>')
        html_content.append('    </div>')


        
        # Annual revenue chart (combine revenue and growth rate on dual y-axes)
        if not annual_revenue.empty and not annual_indicators.empty:
            # Prepare data for annual revenue chart
            annual_years = annual_revenue['报告期'].tolist()
            annual_revenue_values = annual_revenue['年度营业收入'].tolist() if '年度营业收入' in annual_revenue.columns else []
            
            # Prepare data for annual growth rate
            annual_tr_yoy_values = annual_indicators['年度营收增长率'].tolist() if '年度营收增长率' in annual_indicators.columns else []


        
        # Annual net profit chart (combine net profit and growth rate on dual y-axes)
        if not annual_net_profit.empty and not annual_indicators.empty:
            # Prepare data for annual net profit chart
            annual_net_profit_years = annual_net_profit['报告期'].tolist()
            annual_net_profit_values = annual_net_profit['年度归母净利润'].tolist() if '年度归母净利润' in annual_net_profit.columns else []
            
            # Prepare data for annual growth rate
            annual_netprofit_yoy_values = annual_indicators['年度利润增长率'].tolist() if '年度利润增长率' in annual_indicators.columns else []


        
        # Quarterly revenue chart (combine revenue and growth rates on dual y-axes)
        if not quarterly_revenue.empty and not quarterly_indicators.empty:
            # Prepare data for quarterly revenue chart
            quarterly_periods = quarterly_revenue['报告期'].tolist()
            quarterly_revenue_values = quarterly_revenue['季度营业收入'].tolist() if '季度营业收入' in quarterly_revenue.columns else []
            
            # Prepare data for quarterly growth rates
            quarterly_gr_yoy_values = quarterly_indicators['营收同比增长率'].tolist() if '营收同比增长率' in quarterly_indicators.columns else []
            quarterly_gr_qoq_values = quarterly_indicators['营收环比增长率'].tolist() if '营收环比增长率' in quarterly_indicators.columns else []


        
        # Quarterly net profit chart (combine net profit and growth rates on dual y-axes)
        if not quarterly_net_profit.empty and not quarterly_indicators.empty:
            # Prepare data for quarterly net profit chart
            quarterly_net_profit_periods = quarterly_net_profit['报告期'].tolist()
            quarterly_net_profit_values = quarterly_net_profit['季度归母净利润'].tolist() if '季度归母净利润' in quarterly_net_profit.columns else []
            
            # Prepare data for quarterly growth rates
            quarterly_profit_yoy_values = quarterly_indicators['利润同比增长率'].tolist() if '利润同比增长率' in quarterly_indicators.columns else []
            quarterly_profit_qoq_values = quarterly_indicators['利润环比增长率'].tolist() if '利润环比增长率' in quarterly_indicators.columns else []


        
        # Annual cash flow chart
        if not annual_cashflow.empty:
            annual_cashflow_periods = annual_cashflow['报告期'].tolist()
            annual_cashflow_values = annual_cashflow['年度经营现金流净额'].tolist() if '年度经营现金流净额' in annual_cashflow.columns else []
            

        
        # Quarterly cash flow chart
        if not quarterly_cashflow.empty:
            quarterly_cashflow_periods = quarterly_cashflow['报告期'].tolist()
            quarterly_cashflow_values = quarterly_cashflow['季度经营现金流净额'].tolist() if '季度经营现金流净额' in quarterly_cashflow.columns else []
            

        
        # Annual margins chart
        if not annual_indicators.empty and '年度净利率' in annual_indicators.columns and '年度毛利率' in annual_indicators.columns:
            annual_margin_periods = annual_indicators['报告期'].tolist()
            annual_netprofit_margin_values = annual_indicators['年度净利率'].tolist()
            annual_grossprofit_margin_values = annual_indicators['年度毛利率'].tolist()
            

        
        # Annual ROE chart
        if not annual_indicators.empty and '年度净资产收益率' in annual_indicators.columns and '年度总资产报酬率' in annual_indicators.columns and '年度投入资本回报率' in annual_indicators.columns:
            annual_roe_periods = annual_indicators['报告期'].tolist()
            annual_roe_waa_values = annual_indicators['年度净资产收益率'].tolist()
            annual_roa_values = annual_indicators['年度总资产报酬率'].tolist()
            annual_roic_values = annual_indicators['年度投入资本回报率'].tolist()
            

        
        
        # Quarterly margins chart
        if not quarterly_indicators.empty and '单季度销售净利率' in quarterly_indicators.columns and '单季度销售毛利率' in quarterly_indicators.columns:
            quarterly_margin_periods = quarterly_indicators['报告期'].tolist()
            quarterly_netprofit_margin_values = quarterly_indicators['单季度销售净利率'].tolist()
            quarterly_grossprofit_margin_values = quarterly_indicators['单季度销售毛利率'].tolist()
            

        
        
        

        
        # Close HTML tags
        html_content.append('</body>')
        html_content.append('</html>')

        # Join all content
        final_content = "\n".join(html_content)
        
        # Save to file
        filename = f"{company_name}_{stock_code}_{today.replace('年', '').replace('月', '').replace('日', '')}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"整合报告已保存到: {filepath}")
        return filepath

    def _df_to_html_table(self, df: pd.DataFrame) -> str:
        """
        将DataFrame转换为HTML表格格式
        """
        if df.empty:
            return "<p>暂无数据</p>"
        
        # Start the table
        html_table = ["    <table>"]
        
        # Add header
        html_table.append("        <thead>")
        html_table.append("            <tr>")
        for col in df.columns:
            html_table.append(f"                <th>{col}</th>")
        html_table.append("            </tr>")
        html_table.append("        </thead>")
        
        # Add body
        html_table.append("        <tbody>")
        for _, row in df.iterrows():
            html_table.append("            <tr>")
            for cell in row:
                cell_value = str(cell) if pd.notna(cell) else 'N/A'
                html_table.append(f"                <td>{cell_value}</td>")
            html_table.append("            </tr>")
        html_table.append("        </tbody>")
        
        # Close the table
        html_table.append("    </table>")
        
        return "\n".join(html_table)


def main():
    """
    主函数，演示内容整合功能
    """
    # This is a placeholder - in a real scenario, this would receive actual data from the other modules
    print("内容整合模块已准备就绪。需要从数据提取模块和文本生成模块接收数据以生成最终报告。")


if __name__ == "__main__":
    main()