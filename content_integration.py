import os
import datetime
import pandas as pd
from typing import Dict, Any
import markdown
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
                         text_generator_result: Dict[str, str],
                         abnormal_info: str = None,
                         index: int = None) -> str:
        """
        整合所有内容并生成HTML格式的报告
        """
        # Get today's date
        today = datetime.datetime.now().strftime('%Y年%m月%d日')

        # Convert stock code for East Money URL (e.g., '000572.SZ' -> 'sz000572')
        east_money_stock_code = self._convert_stock_code_for_east_money(stock_code)

        # Create HTML content
        html_content = []

        # HTML Header with basic styling
        html_content.append('<!DOCTYPE html>')
        html_content.append('<html lang="zh-CN">')
        html_content.append('<head>')
        html_content.append('    <meta charset="UTF-8">')
        html_content.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html_content.append('    <title>{}（{}）公司分析报告</title>'.format(company_name, stock_code))
        html_content.append('    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>')
        html_content.append('    <style>')
        html_content.append('        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }')
        html_content.append('        h1, h2, h3 { color: #333; }')
        html_content.append('        h1 { border-bottom: 2px solid #333; padding-bottom: 10px; }')
        html_content.append('        table { border-collapse: collapse; width: 100%; margin: 10px 0; }')
        html_content.append('        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }')
        html_content.append('        th { background-color: #f2f2f2; }')
        html_content.append('        .section { margin: 20px 0; }')
        html_content.append('        .subsection { margin: 15px 0; }')
        html_content.append('        .chart-container { position: relative; height: 400px; width: 100%; margin: 20px 0; }')

        html_content.append('        .kline-image { width: 100%; max-width: 1000px; height: auto; margin: 20px 0; }')
        html_content.append('        strong { color: #444; }')
        html_content.append('    </style>')
        html_content.append('</head>')
        html_content.append('<body>')

        # 1. Title and subtitle
        html_content.append(f'    <h1>{company_name}（{stock_code}）</h1>')
        html_content.append(f'    <h2>{today}</h2>')

        # 2. Add abnormal stock information if available
        if abnormal_info:
            # Convert markdown to HTML for proper rendering, similar to how shareholders_info and income_structure_info are handled
            html_abnormal_info = markdown.markdown(abnormal_info, extensions=['extra', 'codehilite', 'toc', 'tables', 'fenced_code'])
            html_content.append('    <div class="section">')
            html_content.append('        <h2>股价异动分析</h2>')
            html_content.append(f'        <div>{html_abnormal_info}</div>')
            html_content.append('    </div>')

        # 3. Generate and add K-line chart
        try:
            kline_generator = KLineGenerator()
            kline_base64 = kline_generator.plot_kline(stock_code, company_name)
            if kline_base64:
                html_content.append(f'    <div class="section">')
                html_content.append(f'        <h2>K线图分析</h2>')
                html_content.append(f'        <img src="{kline_base64}" class="kline-image" alt="K线图">')
                html_content.append(f'        <a href="https://quote.eastmoney.com/concept/{east_money_stock_code}.html" target="_blank" style="display:inline-block; padding: 8px 16px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; margin-top: 10px;">K线图详情</a>')
                html_content.append(f'    </div>')
        except Exception as e:
            print(f"生成K线图时出错: {e}")
            html_content.append(f'    <div class="section">')
            html_content.append(f'        <h2>K线图分析</h2>')
            html_content.append(f'        <p>无法生成K线图: {e}</p>')
            html_content.append(f'        <a href="https://quote.eastmoney.com/concept/{east_money_stock_code}.html" target="_blank" style="display:inline-block; padding: 8px 16px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; margin-top: 10px;">K线图详情</a>')
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
        
        # Get shareholders info from text generator
        shareholders_info = text_generator_result.get('shareholders_info', 'N/A')
        html_content.append('        <div class="subsection">')
        html_content.append('            <h3>前十大股东信息：</h3>')
        html_content.append(f'            {shareholders_info}')
        html_content.append('        </div>')
        
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

            # Add chart for annual revenue and growth rate
            if not annual_indicators.empty and '年度营收增长率' in annual_indicators.columns:
                # Merge revenue and growth data for the chart
                combined_annual_revenue_df = annual_revenue.merge(
                    annual_indicators[['报告期', '年度营收增长率']],
                    on='报告期',
                    how='left'
                )
                combined_annual_revenue_df = combined_annual_revenue_df.rename(columns={'年度营收增长率': '年度营收增长率(%)'})
                
                # Prepare chart data
                years = combined_annual_revenue_df['报告期'].tolist()
                revenues = combined_annual_revenue_df['年度营业收入'].tolist() if '年度营业收入' in combined_annual_revenue_df.columns else []
                growth_rates = combined_annual_revenue_df['年度营收增长率(%)'].tolist() if '年度营收增长率(%)' in combined_annual_revenue_df.columns else []
                
                # Filter out null values for chart
                valid_data = [(year, rev, growth) for year, rev, growth in zip(years, revenues, growth_rates) 
                             if pd.notna(rev) and pd.notna(growth)]
                if valid_data:
                    chart_years, chart_revenues, chart_growth_rates = zip(*valid_data)
                else:
                    chart_years, chart_revenues, chart_growth_rates = years, revenues, growth_rates
                
                # Create chart container
                html_content.append('        <div class="chart-container">')
                html_content.append('            <canvas id="annualRevenueChart"></canvas>')
                html_content.append('        </div>')
                
                # Add JavaScript for the chart
                html_content.append('        <script>')
                html_content.append('            document.addEventListener("DOMContentLoaded", function() {')
                html_content.append('                const ctx = document.getElementById("annualRevenueChart").getContext("2d");')
                html_content.append('                const annualRevenueChart = new Chart(ctx, {')
                html_content.append('                    type: "bar",')
                html_content.append('                    data: {')
                html_content.append('                        labels: [' + ', '.join([f'"{year}"' for year in chart_years]) + '],')
                html_content.append('                        datasets: [')
                html_content.append('                            {')
                html_content.append('                                label: "年度营业收入 (亿元)",')
                html_content.append('                                data: [' + ', '.join([str(rev) if pd.notna(rev) else 'null' for rev in chart_revenues]) + '],')
                html_content.append('                                backgroundColor: "rgba(87, 160, 229, 1)",  // 淡蓝色，透明度100%')
                html_content.append('                                borderColor: "rgba(87, 160, 229, 1)",   // 与填充色相同')
                html_content.append('                                borderWidth: 2,')
                html_content.append('                                yAxisID: "y-axis-revenue",')
                html_content.append('                                order: 2')
                html_content.append('                            },')
                html_content.append('                            {')
                html_content.append('                                label: "年度营收增长率 (%)",')
                html_content.append('                                data: [' + ', '.join([str(growth) if pd.notna(growth) else 'null' for growth in chart_growth_rates]) + '],')
                html_content.append('                                borderColor: "rgba(249, 217, 137, 1)",      // 黄色，透明度100%')
                html_content.append('                                backgroundColor: "rgba(249, 217, 137, 1)",  // 与线条同色')
                html_content.append('                                borderWidth: 3,')
                html_content.append('                                pointBackgroundColor: "rgba(255, 152, 0, 1)",')
                html_content.append('                                pointBorderColor: "rgba(255, 255, 255, 0)",  // 透明点')
                html_content.append('                                pointRadius: 5,')
                html_content.append('                                fill: false,')
                html_content.append('                                type: "line",')
                html_content.append('                                tension: 0.4, // for smooth curves')
                html_content.append('                                yAxisID: "y-axis-growth",')
                html_content.append('                                order: 1')
                html_content.append('                            }')
                html_content.append('                        ]')
                html_content.append('                    },')
                html_content.append('                    options: {')
                html_content.append('                        responsive: true,')
                html_content.append('                        scales: {')
                html_content.append('                            x: {')
                html_content.append('                                grid: {')
                html_content.append('                                    display: false  // 禁用x轴网格线（纵向线不显示）')
                html_content.append('                                }')
                html_content.append('                            },')
                html_content.append('                            "y-axis-revenue": {')
                html_content.append('                                position: "left",')
                html_content.append('                                title: {')
                html_content.append('                                    display: true,')
                html_content.append('                                    text: "营业收入 (亿元)"')
                html_content.append('                                }')
                html_content.append('                            },')
                html_content.append('                            "y-axis-growth": {')
                html_content.append('                                position: "right",')
                html_content.append('                                title: {')
                html_content.append('                                    display: true,')
                html_content.append('                                    text: "营收增长率 (%)"')
                html_content.append('                                },')
                html_content.append('                                grid: {')
                html_content.append('                                    drawOnChartArea: false')
                html_content.append('                                }')
                html_content.append('                            }')
                html_content.append('                        },')
                html_content.append('                        plugins: {')
                html_content.append('                            title: {')
                html_content.append('                                display: true,')
                html_content.append('                                text: "年度营业收入与营收增长率趋势"')
                html_content.append('                            },')
                html_content.append('                            legend: {')
                html_content.append('                                display: true,')
                html_content.append('                                position: "top"')
                html_content.append('                            }')
                html_content.append('                        }')
                html_content.append('                    }')
                html_content.append('                });')
                html_content.append('            });')
                html_content.append('        </script>')

                # Use the merged dataframe for the table
                combined_annual_revenue = combined_annual_revenue_df
            else:
                combined_annual_revenue = annual_revenue.copy()

            # Combine revenue and growth data in the same table
            html_content.append(self._df_to_html_table(combined_annual_revenue))
            html_content.append('        </div>')

        # Annual income statement - Net Profit
        annual_net_profit = data_extractor_result.get('annual_net_profit', pd.DataFrame())
        annual_indicators = data_extractor_result.get('annual_indicators', pd.DataFrame())
        if not annual_net_profit.empty:
            html_content.append('        <div class="subsection">')
            html_content.append('            <h3>年度归母净利润与利润增长率数据</h3>')

            # Add chart for annual net profit and growth rate
            if not annual_indicators.empty and '年度利润增长率' in annual_indicators.columns:
                # Merge net profit and growth data for the chart
                combined_annual_net_profit_df = annual_net_profit.merge(
                    annual_indicators[['报告期', '年度利润增长率']],
                    on='报告期',
                    how='left'
                )
                combined_annual_net_profit_df = combined_annual_net_profit_df.rename(columns={'年度利润增长率': '年度利润增长率(%)'})

                # Prepare chart data
                years = combined_annual_net_profit_df['报告期'].tolist()
                net_profits = combined_annual_net_profit_df['年度归母净利润'].tolist() if '年度归母净利润' in combined_annual_net_profit_df.columns else []
                growth_rates = combined_annual_net_profit_df['年度利润增长率(%)'].tolist() if '年度利润增长率(%)' in combined_annual_net_profit_df.columns else []

                # Filter out null values for chart
                valid_data = [(year, profit, growth) for year, profit, growth in zip(years, net_profits, growth_rates)
                             if pd.notna(profit) and pd.notna(growth)]
                if valid_data:
                    chart_years, chart_net_profits, chart_growth_rates = zip(*valid_data)
                else:
                    chart_years, chart_net_profits, chart_growth_rates = years, net_profits, growth_rates

                # Create chart container
                html_content.append('        <div class="chart-container">')
                html_content.append('            <canvas id="annualNetProfitChart"></canvas>')
                html_content.append('        </div>')

                # Add JavaScript for the chart
                html_content.append('        <script>')
                html_content.append('            document.addEventListener("DOMContentLoaded", function() {')
                html_content.append('                const ctx = document.getElementById("annualNetProfitChart").getContext("2d");')
                html_content.append('                const annualNetProfitChart = new Chart(ctx, {')
                html_content.append('                    type: "bar",')
                html_content.append('                    data: {')
                html_content.append('                        labels: [' + ', '.join([f'"{year}"' for year in chart_years]) + '],')
                html_content.append('                        datasets: [')
                html_content.append('                            {')
                html_content.append('                                label: "年度归母净利润 (亿元)",')
                html_content.append('                                data: [' + ', '.join([str(profit) if pd.notna(profit) else 'null' for profit in chart_net_profits]) + '],')
                html_content.append('                                backgroundColor: "rgba(87, 160, 229, 1)",  // 淡蓝色，透明度100%')
                html_content.append('                                borderColor: "rgba(87, 160, 229, 1)",   // 与填充色相同')
                html_content.append('                                borderWidth: 2,')
                html_content.append('                                yAxisID: "y-axis-net-profit",')
                html_content.append('                                order: 2')
                html_content.append('                            },')
                html_content.append('                            {')
                html_content.append('                                label: "年度利润增长率 (%)",')
                html_content.append('                                data: [' + ', '.join([str(growth) if pd.notna(growth) else 'null' for growth in chart_growth_rates]) + '],')
                html_content.append('                                borderColor: "rgba(249, 217, 137, 1)",      // 黄色，透明度100%')
                html_content.append('                                backgroundColor: "rgba(249, 217, 137, 1)",  // 与线条同色')
                html_content.append('                                borderWidth: 3,')
                html_content.append('                                pointBackgroundColor: "rgba(255, 152, 0, 1)",')
                html_content.append('                                pointBorderColor: "rgba(255, 255, 255, 0)",  // 透明点')
                html_content.append('                                pointRadius: 5,')
                html_content.append('                                fill: false,')
                html_content.append('                                type: "line",')
                html_content.append('                                tension: 0.4, // for smooth curves')
                html_content.append('                                yAxisID: "y-axis-growth",')
                html_content.append('                                order: 1')
                html_content.append('                            }')
                html_content.append('                        ]')
                html_content.append('                    },')
                html_content.append('                    options: {')
                html_content.append('                        responsive: true,')
                html_content.append('                        scales: {')
                html_content.append('                            x: {')
                html_content.append('                                grid: {')
                html_content.append('                                    display: false  // 禁用x轴网格线（纵向线不显示）')
                html_content.append('                                }')
                html_content.append('                            },')
                html_content.append('                            "y-axis-net-profit": {')
                html_content.append('                                position: "left",')
                html_content.append('                                title: {')
                html_content.append('                                    display: true,')
                html_content.append('                                    text: "归母净利润 (亿元)"')
                html_content.append('                                }')
                html_content.append('                            },')
                html_content.append('                            "y-axis-growth": {')
                html_content.append('                                position: "right",')
                html_content.append('                                title: {')
                html_content.append('                                    display: true,')
                html_content.append('                                    text: "利润增长率 (%)"')
                html_content.append('                                },')
                html_content.append('                                grid: {')
                html_content.append('                                    drawOnChartArea: false')
                html_content.append('                                }')
                html_content.append('                            }')
                html_content.append('                        },')
                html_content.append('                        plugins: {')
                html_content.append('                            title: {')
                html_content.append('                                display: true,')
                html_content.append('                                text: "年度归母净利润与利润增长率趋势"')
                html_content.append('                            },')
                html_content.append('                            legend: {')
                html_content.append('                                display: true,')
                html_content.append('                                position: "top"')
                html_content.append('                            }')
                html_content.append('                        }')
                html_content.append('                    }')
                html_content.append('                });')
                html_content.append('            });')
                html_content.append('        </script>')

            # Use the merged dataframe for the table
            if not annual_indicators.empty and '年度利润增长率' in annual_indicators.columns:
                combined_annual_net_profit_df = annual_net_profit.merge(
                    annual_indicators[['报告期', '年度利润增长率']],
                    on='报告期',
                    how='left'
                )
                combined_annual_net_profit_df = combined_annual_net_profit_df.rename(columns={'年度利润增长率': '年度利润增长率(%)'})
                combined_annual_net_profit = combined_annual_net_profit_df
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

            # Add chart for quarterly revenue and growth rates
            if not quarterly_indicators.empty and '营收同比增长率' in quarterly_indicators.columns and '营收环比增长率' in quarterly_indicators.columns:
                # Merge quarterly revenue and growth data for the chart
                combined_quarterly_revenue_df = quarterly_revenue.merge(
                    quarterly_indicators[['报告期', '营收同比增长率', '营收环比增长率']],
                    on='报告期',
                    how='left'
                )
                combined_quarterly_revenue_df = combined_quarterly_revenue_df.rename(columns={
                    '营收同比增长率': '季度营收同比增长率(%)',
                    '营收环比增长率': '季度营收环比增长率(%)'
                })

                # Prepare chart data
                q_periods = combined_quarterly_revenue_df['报告期'].tolist()
                q_revenues = combined_quarterly_revenue_df['季度营业收入'].tolist() if '季度营业收入' in combined_quarterly_revenue_df.columns else []
                q_gr_yoy = combined_quarterly_revenue_df['季度营收同比增长率(%)'].tolist() if '季度营收同比增长率(%)' in combined_quarterly_revenue_df.columns else []
                q_gr_qoq = combined_quarterly_revenue_df['季度营收环比增长率(%)'].tolist() if '季度营收环比增长率(%)' in combined_quarterly_revenue_df.columns else []

                # Filter out null values for chart
                valid_data = [(period, revenue, yoy, qoq) for period, revenue, yoy, qoq in zip(q_periods, q_revenues, q_gr_yoy, q_gr_qoq)
                             if pd.notna(revenue) and pd.notna(yoy) and pd.notna(qoq)]
                if valid_data:
                    chart_periods, chart_revenues, chart_yoy, chart_qoq = zip(*valid_data)
                else:
                    chart_periods, chart_revenues, chart_yoy, chart_qoq = q_periods, q_revenues, q_gr_yoy, q_gr_qoq

                # Create chart container
                html_content.append('        <div class="chart-container">')
                html_content.append('            <canvas id="quarterlyRevenueChart"></canvas>')
                html_content.append('        </div>')

                # Add JavaScript for the chart
                html_content.append('        <script>')
                html_content.append('            document.addEventListener("DOMContentLoaded", function() {')
                html_content.append('                const ctx = document.getElementById("quarterlyRevenueChart").getContext("2d");')
                html_content.append('                const quarterlyRevenueChart = new Chart(ctx, {')
                html_content.append('                    type: "bar",')
                html_content.append('                    data: {')
                html_content.append('                        labels: [' + ', '.join([f'"{period}"' for period in chart_periods]) + '],')
                html_content.append('                        datasets: [')
                html_content.append('                            {')
                html_content.append('                                label: "季度营业收入 (亿元)",')
                html_content.append('                                data: [' + ', '.join([str(rev) if pd.notna(rev) else 'null' for rev in chart_revenues]) + '],')
                html_content.append('                                backgroundColor: "rgba(87, 160, 229, 1)",  // 淡蓝色，透明度100%')
                html_content.append('                                borderColor: "rgba(87, 160, 229, 1)",   // 与填充色相同')
                html_content.append('                                borderWidth: 2,')
                html_content.append('                                order: 3,')
                html_content.append('                                yAxisID: "y-axis-revenue",')
            html_content.append('                            },')
            html_content.append('                            {')
            html_content.append('                                label: "季度营收同比增长率 (%)",')
            html_content.append('                                data: [' + ', '.join([str(yoy) if pd.notna(yoy) else 'null' for yoy in chart_yoy]) + '],')
            html_content.append('                                borderColor: "rgba(249, 217, 137, 1)",      // 黄色，透明度100%')
            html_content.append('                                backgroundColor: "rgba(249, 217, 137, 1)",  // 与线条同色')
            html_content.append('                                borderWidth: 3,')
            html_content.append('                                pointBackgroundColor: "rgba(255, 152, 0, 1)",')
            html_content.append('                                pointBorderColor: "rgba(255, 255, 255, 0)",  // 透明点')
            html_content.append('                                pointRadius: 5,')
            html_content.append('                                fill: false,')
            html_content.append('                                type: "line",')
            html_content.append('                                order: 1,')
            html_content.append('                                tension: 0.4, // for smooth curves')
            html_content.append('                                yAxisID: "y-axis-growth",')
            html_content.append('                            },')
            html_content.append('                            {')
            html_content.append('                                label: "季度营收环比增长率 (%)",')
            html_content.append('                                data: [' + ', '.join([str(qoq) if pd.notna(qoq) else 'null' for qoq in chart_qoq]) + '],')
            html_content.append('                                borderColor: "rgba(241, 138, 158, 1)",      // 指定颜色')
            html_content.append('                                backgroundColor: "rgba(241, 138, 158, 1)",  // 与线条同色')
            html_content.append('                                borderWidth: 2,')
            html_content.append('                                pointBackgroundColor: "rgba(241, 138, 158, 1)",')
            html_content.append('                                pointBorderColor: "rgba(255, 255, 255, 0)",  // 透明点')
            html_content.append('                                pointRadius: 4,')
            html_content.append('                                fill: false,')
            html_content.append('                                type: "line",')
            html_content.append('                                order: 2,')
            html_content.append('                                tension: 0.4, // for smooth curves')
            html_content.append('                                yAxisID: "y-axis-growth",')
            html_content.append('                            }')
            html_content.append('                        ]')
            html_content.append('                    },')
            html_content.append('                    options: {')
            html_content.append('                        responsive: true,')
            html_content.append('                        scales: {')
            html_content.append('                            x: {')
            html_content.append('                                grid: {')
            html_content.append('                                    display: false  // 禁用x轴网格线（纵向线不显示）')
            html_content.append('                                }')
            html_content.append('                            },')
            html_content.append('                            "y-axis-revenue": {')
            html_content.append('                                position: "left",')
            html_content.append('                                title: {')
            html_content.append('                                    display: true,')
            html_content.append('                                    text: "季度营业收入 (亿元)"')
            html_content.append('                                }')
            html_content.append('                            },')
            html_content.append('                            "y-axis-growth": {')
            html_content.append('                                position: "right",')
            html_content.append('                                title: {')
            html_content.append('                                    display: true,')
            html_content.append('                                    text: "营收增长率 (%)"')
            html_content.append('                                },')
            html_content.append('                                grid: {')
            html_content.append('                                    drawOnChartArea: false')
            html_content.append('                                }')
            html_content.append('                            }')
            html_content.append('                        },')
            html_content.append('                        plugins: {')
            html_content.append('                            title: {')
            html_content.append('                                display: true,')
            html_content.append('                                text: "季度营业收入与营收增长率趋势"')
            html_content.append('                            },')
            html_content.append('                            legend: {')
            html_content.append('                                display: true,')
            html_content.append('                                position: "top"')
            html_content.append('                            }')
            html_content.append('                        }')
            html_content.append('                    }')
            html_content.append('                });')
            html_content.append('            });')
            html_content.append('        </script>')

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

            # Add chart for quarterly net profit and growth rates
            if not quarterly_indicators.empty and '利润同比增长率' in quarterly_indicators.columns and '利润环比增长率' in quarterly_indicators.columns:
                # Merge quarterly net profit and growth data for the chart
                combined_quarterly_net_profit_df = quarterly_net_profit.merge(
                    quarterly_indicators[['报告期', '利润同比增长率', '利润环比增长率']],
                    on='报告期',
                    how='left'
                )
                combined_quarterly_net_profit_df = combined_quarterly_net_profit_df.rename(columns={
                    '利润同比增长率': '季度利润同比增长率(%)',
                    '利润环比增长率': '季度利润环比增长率(%)'
                })

                # Prepare chart data
                q_np_periods = combined_quarterly_net_profit_df['报告期'].tolist()
                q_np_profits = combined_quarterly_net_profit_df['季度归母净利润'].tolist() if '季度归母净利润' in combined_quarterly_net_profit_df.columns else []
                q_np_yoy = combined_quarterly_net_profit_df['季度利润同比增长率(%)'].tolist() if '季度利润同比增长率(%)' in combined_quarterly_net_profit_df.columns else []
                q_np_qoq = combined_quarterly_net_profit_df['季度利润环比增长率(%)'].tolist() if '季度利润环比增长率(%)' in combined_quarterly_net_profit_df.columns else []

                # Filter out null values for chart
                valid_data = [(period, profit, yoy, qoq) for period, profit, yoy, qoq in zip(q_np_periods, q_np_profits, q_np_yoy, q_np_qoq)
                             if pd.notna(profit) and pd.notna(yoy) and pd.notna(qoq)]
                if valid_data:
                    chart_np_periods, chart_np_profits, chart_np_yoy, chart_np_qoq = zip(*valid_data)
                else:
                    chart_np_periods, chart_np_profits, chart_np_yoy, chart_np_qoq = q_np_periods, q_np_profits, q_np_yoy, q_np_qoq

                # Create chart container
                html_content.append('        <div class="chart-container">')
                html_content.append('            <canvas id="quarterlyNetProfitChart"></canvas>')
                html_content.append('        </div>')

                # Add JavaScript for the chart
                html_content.append('        <script>')
                html_content.append('            document.addEventListener("DOMContentLoaded", function() {')
                html_content.append('                const ctx = document.getElementById("quarterlyNetProfitChart").getContext("2d");')
                html_content.append('                const quarterlyNetProfitChart = new Chart(ctx, {')
                html_content.append('                    type: "bar",')
                html_content.append('                    data: {')
                html_content.append('                        labels: [' + ', '.join([f'"{period}"' for period in chart_np_periods]) + '],')
                html_content.append('                        datasets: [')
                html_content.append('                            {')
                html_content.append('                                label: "季度归母净利润 (亿元)",')
                html_content.append('                                data: [' + ', '.join([str(profit) if pd.notna(profit) else 'null' for profit in chart_np_profits]) + '],')
                html_content.append('                                backgroundColor: "rgba(87, 160, 229, 1)",  // 淡蓝色，透明度100%')
                html_content.append('                                borderColor: "rgba(87, 160, 229, 1)",   // 与填充色相同')
                html_content.append('                                borderWidth: 2,')
                html_content.append('                                order: 3,')
                html_content.append('                                yAxisID: "y-axis-net-profit",')
            html_content.append('                            },')
            html_content.append('                            {')
            html_content.append('                                label: "季度利润同比增长率 (%)",')
            html_content.append('                                data: [' + ', '.join([str(yoy) if pd.notna(yoy) else 'null' for yoy in chart_np_yoy]) + '],')
            html_content.append('                                borderColor: "rgba(249, 217, 137, 1)",      // 黄色，透明度100%')
            html_content.append('                                backgroundColor: "rgba(249, 217, 137, 1)",  // 与线条同色')
            html_content.append('                                borderWidth: 3,')
            html_content.append('                                pointBackgroundColor: "rgba(255, 152, 0, 1)",')
            html_content.append('                                pointBorderColor: "rgba(255, 255, 255, 0)",  // 透明点')
            html_content.append('                                pointRadius: 5,')
            html_content.append('                                fill: false,')
            html_content.append('                                type: "line",')
            html_content.append('                                order: 1,')
            html_content.append('                                tension: 0.4, // for smooth curves')
            html_content.append('                                yAxisID: "y-axis-growth",')
            html_content.append('                            },')
            html_content.append('                            {')
            html_content.append('                                label: "季度利润环比增长率 (%)",')
            html_content.append('                                data: [' + ', '.join([str(qoq) if pd.notna(qoq) else 'null' for qoq in chart_np_qoq]) + '],')
            html_content.append('                                borderColor: "rgba(241, 138, 158, 1)",      // 指定颜色')
            html_content.append('                                backgroundColor: "rgba(241, 138, 158, 1)",  // 与线条同色')
            html_content.append('                                borderWidth: 2,')
            html_content.append('                                pointBackgroundColor: "rgba(241, 138, 158, 1)",')
            html_content.append('                                pointBorderColor: "rgba(255, 255, 255, 0)",  // 透明点')
            html_content.append('                                pointRadius: 4,')
            html_content.append('                                fill: false,')
            html_content.append('                                type: "line",')
            html_content.append('                                order: 2,')
            html_content.append('                                tension: 0.4, // for smooth curves')
            html_content.append('                                yAxisID: "y-axis-growth",')
            html_content.append('                            }')
            html_content.append('                        ]')
            html_content.append('                    },')
            html_content.append('                    options: {')
            html_content.append('                        responsive: true,')
            html_content.append('                        scales: {')
            html_content.append('                            x: {')
            html_content.append('                                grid: {')
            html_content.append('                                    display: false  // 禁用x轴网格线（纵向线不显示）')
            html_content.append('                                }')
            html_content.append('                            },')
            html_content.append('                            "y-axis-net-profit": {')
            html_content.append('                                position: "left",')
            html_content.append('                                title: {')
            html_content.append('                                    display: true,')
            html_content.append('                                    text: "季度归母净利润 (亿元)"')
            html_content.append('                                }')
            html_content.append('                            },')
            html_content.append('                            "y-axis-growth": {')
            html_content.append('                                position: "right",')
            html_content.append('                                title: {')
            html_content.append('                                    display: true,')
            html_content.append('                                    text: "利润增长率 (%)"')
            html_content.append('                                },')
            html_content.append('                                grid: {')
            html_content.append('                                    drawOnChartArea: false')
            html_content.append('                                }')
            html_content.append('                            }')
            html_content.append('                        },')
            html_content.append('                        plugins: {')
            html_content.append('                            title: {')
            html_content.append('                                display: true,')
            html_content.append('                                text: "季度归母净利润与利润增长率趋势"')
            html_content.append('                            },')
            html_content.append('                            legend: {')
            html_content.append('                                display: true,')
            html_content.append('                                position: "top"')
            html_content.append('                            }')
            html_content.append('                        }')
            html_content.append('                    }')
            html_content.append('                });')
            html_content.append('            });')
            html_content.append('        </script>')

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

            # Add chart for annual cash flow
            annual_cashflow_periods = annual_cashflow['报告期'].tolist()
            annual_cashflow_values = annual_cashflow['年度经营现金流净额'].tolist() if '年度经营现金流净额' in annual_cashflow.columns else []

            # Prepare chart data
            cashflow_periods = annual_cashflow['报告期'].tolist()
            cashflow_values = annual_cashflow['年度经营现金流净额'].tolist() if '年度经营现金流净额' in annual_cashflow.columns else []

            # Filter out null values for chart
            valid_data = [(period, cashflow) for period, cashflow in zip(cashflow_periods, cashflow_values)
                         if pd.notna(cashflow)]
            if valid_data:
                chart_periods, chart_cashflows = zip(*valid_data)
            else:
                chart_periods, chart_cashflows = cashflow_periods, cashflow_values

            # Create chart container
            html_content.append('        <div class="chart-container">')
            html_content.append('            <canvas id="annualCashflowChart"></canvas>')
            html_content.append('        </div>')

            # Add JavaScript for the chart
            html_content.append('        <script>')
            html_content.append('            document.addEventListener("DOMContentLoaded", function() {')
            html_content.append('                const ctx = document.getElementById("annualCashflowChart").getContext("2d");')
            html_content.append('                const annualCashflowChart = new Chart(ctx, {')
            html_content.append('                    type: "bar",')
            html_content.append('                    data: {')
            html_content.append('                        labels: [' + ', '.join([f'"{period}"' for period in chart_periods]) + '],')
            html_content.append('                        datasets: [')
            html_content.append('                            {')
            html_content.append('                                label: "年度经营现金流净额 (亿元)",')
            html_content.append('                                data: [' + ', '.join([str(cashflow) if pd.notna(cashflow) else 'null' for cashflow in chart_cashflows]) + '],')
            html_content.append('                                backgroundColor: "rgba(87, 160, 229, 1)",  // 淡蓝色，透明度100%')
            html_content.append('                                borderColor: "rgba(87, 160, 229, 1)",   // 与填充色相同')
            html_content.append('                                borderWidth: 2,')
            html_content.append('                            }')
            html_content.append('                        ]')
            html_content.append('                    },')
            html_content.append('                    options: {')
            html_content.append('                        responsive: true,')
            html_content.append('                        scales: {')
            html_content.append('                            x: {')
            html_content.append('                                grid: {')
            html_content.append('                                    display: false  // 禁用x轴网格线（纵向线不显示）')
            html_content.append('                                }')
            html_content.append('                            },')
            html_content.append('                            y: {')
            html_content.append('                                title: {')
            html_content.append('                                    display: true,')
            html_content.append('                                    text: "经营现金流净额 (亿元)"')
            html_content.append('                                }')
            html_content.append('                            }')
            html_content.append('                        },')
            html_content.append('                        plugins: {')
            html_content.append('                            title: {')
            html_content.append('                                display: true,')
            html_content.append('                                text: "年度经营现金流净额趋势"')
            html_content.append('                            },')
            html_content.append('                            legend: {')
            html_content.append('                                display: true,')
            html_content.append('                                position: "top"')
            html_content.append('                            }')
            html_content.append('                        }')
            html_content.append('                    }')
            html_content.append('                });')
            html_content.append('            });')
            html_content.append('        </script>')

            html_content.append(self._df_to_html_table(annual_cashflow))
            html_content.append('        </div>')

        # Quarterly cash flow statement
        quarterly_cashflow = data_extractor_result.get('quarterly_cashflow', pd.DataFrame())
        if not quarterly_cashflow.empty:
            html_content.append('        <div class="subsection">')
            html_content.append('            <h3>季度现金流量表数据</h3>')

            # Add chart for quarterly cash flow
            quarterly_cashflow_periods = quarterly_cashflow['报告期'].tolist()
            quarterly_cashflow_values = quarterly_cashflow['季度经营现金流净额'].tolist() if '季度经营现金流净额' in quarterly_cashflow.columns else []

            # Prepare chart data
            q_cashflow_periods = quarterly_cashflow['报告期'].tolist()
            q_cashflow_values = quarterly_cashflow['季度经营现金流净额'].tolist() if '季度经营现金流净额' in quarterly_cashflow.columns else []

            # Filter out null values for chart
            valid_data = [(period, cashflow) for period, cashflow in zip(q_cashflow_periods, q_cashflow_values)
                         if pd.notna(cashflow)]
            if valid_data:
                chart_q_periods, chart_q_cashflows = zip(*valid_data)
            else:
                chart_q_periods, chart_q_cashflows = q_cashflow_periods, q_cashflow_values

            # Create chart container
            html_content.append('        <div class="chart-container">')
            html_content.append('            <canvas id="quarterlyCashflowChart"></canvas>')
            html_content.append('        </div>')

            # Add JavaScript for the chart
            html_content.append('        <script>')
            html_content.append('            document.addEventListener("DOMContentLoaded", function() {')
            html_content.append('                const ctx = document.getElementById("quarterlyCashflowChart").getContext("2d");')
            html_content.append('                const quarterlyCashflowChart = new Chart(ctx, {')
            html_content.append('                    type: "bar",')
            html_content.append('                    data: {')
            html_content.append('                        labels: [' + ', '.join([f'"{period}"' for period in chart_q_periods]) + '],')
            html_content.append('                        datasets: [')
            html_content.append('                            {')
            html_content.append('                                label: "季度经营现金流净额 (亿元)",')
            html_content.append('                                data: [' + ', '.join([str(cashflow) if pd.notna(cashflow) else 'null' for cashflow in chart_q_cashflows]) + '],')
            html_content.append('                                backgroundColor: "rgba(87, 160, 229, 1)",  // 淡蓝色，透明度100%')
            html_content.append('                                borderColor: "rgba(87, 160, 229, 1)",   // 与填充色相同')
            html_content.append('                                borderWidth: 2,')
            html_content.append('                            }')
            html_content.append('                        ]')
            html_content.append('                    },')
            html_content.append('                    options: {')
            html_content.append('                        responsive: true,')
            html_content.append('                        scales: {')
            html_content.append('                            x: {')
            html_content.append('                                grid: {')
            html_content.append('                                    display: false  // 禁用x轴网格线（纵向线不显示）')
            html_content.append('                                }')
            html_content.append('                            },')
            html_content.append('                            y: {')
            html_content.append('                                title: {')
            html_content.append('                                    display: true,')
            html_content.append('                                    text: "经营现金流净额 (亿元)"')
            html_content.append('                                }')
            html_content.append('                            }')
            html_content.append('                        },')
            html_content.append('                        plugins: {')
            html_content.append('                            title: {')
            html_content.append('                                display: true,')
            html_content.append('                                text: "季度经营现金流净额趋势"')
            html_content.append('                            },')
            html_content.append('                            legend: {')
            html_content.append('                                display: true,')
            html_content.append('                                position: "top"')
            html_content.append('                            }')
            html_content.append('                        }')
            html_content.append('                    }')
            html_content.append('                });')
            html_content.append('            });')
            html_content.append('        </script>')

            html_content.append(self._df_to_html_table(quarterly_cashflow))
            html_content.append('        </div>')

        # Annual financial indicators
        annual_indicators = data_extractor_result.get('annual_indicators', pd.DataFrame())
        if not annual_indicators.empty:
            html_content.append('        <div class="subsection">')
            html_content.append('            <h3>年度财务指标数据</h3>')

            # Add chart for annual margins (net profit margin and gross profit margin)
            if '年度净利率' in annual_indicators.columns and '年度毛利率' in annual_indicators.columns:
                # Prepare chart data
                margin_periods = annual_indicators['报告期'].tolist()
                netprofit_margins = annual_indicators['年度净利率'].tolist() if '年度净利率' in annual_indicators.columns else []
                grossprofit_margins = annual_indicators['年度毛利率'].tolist() if '年度毛利率' in annual_indicators.columns else []

                # Filter out null values for chart
                valid_data = [(period, net_margin, gross_margin) for period, net_margin, gross_margin in zip(margin_periods, netprofit_margins, grossprofit_margins)
                             if pd.notna(net_margin) and pd.notna(gross_margin)]
                if valid_data:
                    chart_periods, chart_net_margins, chart_gross_margins = zip(*valid_data)
                else:
                    chart_periods, chart_net_margins, chart_gross_margins = margin_periods, netprofit_margins, grossprofit_margins

                # Create chart container
                html_content.append('        <div class="chart-container">')
                html_content.append('            <canvas id="annualMarginsChart"></canvas>')
                html_content.append('        </div>')

                # Add JavaScript for the chart
                html_content.append('        <script>')
                html_content.append('            document.addEventListener("DOMContentLoaded", function() {')
                html_content.append('                const ctx = document.getElementById("annualMarginsChart").getContext("2d");')
                html_content.append('                const annualMarginsChart = new Chart(ctx, {')
                html_content.append('                    type: "line",')
                html_content.append('                    data: {')
                html_content.append('                        labels: [' + ', '.join([f'"{period}"' for period in chart_periods]) + '],')
                html_content.append('                        datasets: [')
                html_content.append('                            {')
                html_content.append('                                label: "年度净利率 (%)",')
                html_content.append('                                data: [' + ', '.join([str(net_margin) if pd.notna(net_margin) else 'null' for net_margin in chart_net_margins]) + '],')
                html_content.append('                                borderColor: "rgba(87, 160, 229, 1)",      // 蓝色')
                html_content.append('                                backgroundColor: "rgba(87, 160, 229, 1)",  // 与线条同色')
                html_content.append('                                borderWidth: 3,')
                html_content.append('                                pointBackgroundColor: "rgba(87, 160, 229, 1)",')
                html_content.append('                                pointBorderColor: "rgba(255, 255, 255, 0)",  // 透明点')
                html_content.append('                                pointRadius: 5,')
                html_content.append('                                fill: false,')
                html_content.append('                                tension: 0.4, // for smooth curves')
                html_content.append('                                yAxisID: "y-axis-margin",')
                html_content.append('                            },')
                html_content.append('                            {')
                html_content.append('                                label: "年度毛利率 (%)",')
                html_content.append('                                data: [' + ', '.join([str(gross_margin) if pd.notna(gross_margin) else 'null' for gross_margin in chart_gross_margins]) + '],')
                html_content.append('                                borderColor: "rgba(241, 138, 158, 1)",      // 指定颜色')
                html_content.append('                                backgroundColor: "rgba(241, 138, 158, 1)",  // 与线条同色')
                html_content.append('                                borderWidth: 2,')
                html_content.append('                                pointBackgroundColor: "rgba(241, 138, 158, 1)",')
                html_content.append('                                pointBorderColor: "rgba(255, 255, 255, 0)",  // 透明点')
                html_content.append('                                pointRadius: 4,')
                html_content.append('                                fill: false,')
                html_content.append('                                type: "line",')
                html_content.append('                                tension: 0.4, // for smooth curves')
                html_content.append('                                yAxisID: "y-axis-margin",')
                html_content.append('                            }')
                html_content.append('                        ]')
                html_content.append('                    },')
                html_content.append('                    options: {')
                html_content.append('                        responsive: true,')
                html_content.append('                        scales: {')
                html_content.append('                            x: {')
                html_content.append('                                grid: {')
                html_content.append('                                    display: false  // 禁用x轴网格线（纵向线不显示）')
                html_content.append('                                }')
                html_content.append('                            },')
                html_content.append('                            "y-axis-margin": {')
                html_content.append('                                title: {')
                html_content.append('                                    display: true,')
                html_content.append('                                    text: "利润率 (%)"')
                html_content.append('                                }')
                html_content.append('                            }')
                html_content.append('                        },')
                html_content.append('                        plugins: {')
                html_content.append('                            title: {')
                html_content.append('                                display: true,')
                html_content.append('                                text: "年度净利率与毛利率趋势"')
                html_content.append('                            },')
                html_content.append('                            legend: {')
                html_content.append('                                display: true,')
                html_content.append('                                position: "top"')
                html_content.append('                            }')
                html_content.append('                        }')
                html_content.append('                    }')
                html_content.append('                });')
                html_content.append('            });')
                html_content.append('        </script>')

            # Add chart for annual ROE (ROE, ROA, ROIC)
            if '年度净资产收益率' in annual_indicators.columns and '年度总资产报酬率' in annual_indicators.columns and '年度投入资本回报率' in annual_indicators.columns:
                # Prepare chart data
                roe_periods = annual_indicators['报告期'].tolist()
                roe_values = annual_indicators['年度净资产收益率'].tolist() if '年度净资产收益率' in annual_indicators.columns else []
                roa_values = annual_indicators['年度总资产报酬率'].tolist() if '年度总资产报酬率' in annual_indicators.columns else []
                roic_values = annual_indicators['年度投入资本回报率'].tolist() if '年度投入资本回报率' in annual_indicators.columns else []

                # Filter out null values for chart
                valid_data = [(period, roe, roa, roic) for period, roe, roa, roic in zip(roe_periods, roe_values, roa_values, roic_values)
                             if pd.notna(roe) and pd.notna(roa) and pd.notna(roic)]
                if valid_data:
                    chart_periods, chart_roe, chart_roa, chart_roic = zip(*valid_data)
                else:
                    chart_periods, chart_roe, chart_roa, chart_roic = roe_periods, roe_values, roa_values, roic_values

                # Create chart container
                html_content.append('        <div class="chart-container">')
                html_content.append('            <canvas id="annualROEChart"></canvas>')
                html_content.append('        </div>')

                # Add JavaScript for the chart
                html_content.append('        <script>')
                html_content.append('            document.addEventListener("DOMContentLoaded", function() {')
                html_content.append('                const ctx = document.getElementById("annualROEChart").getContext("2d");')
                html_content.append('                const annualROEChart = new Chart(ctx, {')
                html_content.append('                    type: "line",')
                html_content.append('                    data: {')
                html_content.append('                        labels: [' + ', '.join([f'"{period}"' for period in chart_periods]) + '],')
                html_content.append('                        datasets: [')
                html_content.append('                            {')
                html_content.append('                                label: "年度净资产收益率 (%)",')
                html_content.append('                                data: [' + ', '.join([str(roe) if pd.notna(roe) else 'null' for roe in chart_roe]) + '],')
                html_content.append('                                borderColor: "rgba(87, 160, 229, 1)",      // 蓝色')
                html_content.append('                                backgroundColor: "rgba(87, 160, 229, 1)",  // 与线条同色')
                html_content.append('                                borderWidth: 3,')
                html_content.append('                                pointBackgroundColor: "rgba(87, 160, 229, 1)",')
                html_content.append('                                pointBorderColor: "rgba(255, 255, 255, 0)",  // 透明点')
                html_content.append('                                pointRadius: 5,')
                html_content.append('                                fill: false,')
                html_content.append('                                tension: 0.4, // for smooth curves')
                html_content.append('                                yAxisID: "y-axis-roe",')
                html_content.append('                            },')
                html_content.append('                            {')
                html_content.append('                                label: "年度总资产报酬率 (%)",')
                html_content.append('                                data: [' + ', '.join([str(roa) if pd.notna(roa) else 'null' for roa in chart_roa]) + '],')
                html_content.append('                                borderColor: "rgba(249, 217, 137, 1)",      // 黄色')
                html_content.append('                                backgroundColor: "rgba(249, 217, 137, 1)",  // 与线条同色')
                html_content.append('                                borderWidth: 3,')
                html_content.append('                                pointBackgroundColor: "rgba(249, 217, 137, 1)",')
                html_content.append('                                pointBorderColor: "rgba(255, 255, 255, 0)",  // 透明点')
                html_content.append('                                pointRadius: 5,')
                html_content.append('                                fill: false,')
                html_content.append('                                tension: 0.4, // for smooth curves')
                html_content.append('                                yAxisID: "y-axis-roe",')
                html_content.append('                            },')
                html_content.append('                            {')
                html_content.append('                                label: "年度投入资本回报率 (%)",')
                html_content.append('                                data: [' + ', '.join([str(roic) if pd.notna(roic) else 'null' for roic in chart_roic]) + '],')
                html_content.append('                                borderColor: "rgba(241, 138, 158, 1)",      // 指定颜色')
                html_content.append('                                backgroundColor: "rgba(241, 138, 158, 1)",  // 与线条同色')
                html_content.append('                                borderWidth: 2,')
                html_content.append('                                pointBackgroundColor: "rgba(241, 138, 158, 1)",')
                html_content.append('                                pointBorderColor: "rgba(255, 255, 255, 0)",  // 透明点')
                html_content.append('                                pointRadius: 4,')
                html_content.append('                                fill: false,')
                html_content.append('                                type: "line",')
                html_content.append('                                tension: 0.4, // for smooth curves')
                html_content.append('                                yAxisID: "y-axis-roe",')
                html_content.append('                            }')
                html_content.append('                        ]')
                html_content.append('                    },')
                html_content.append('                    options: {')
                html_content.append('                        responsive: true,')
                html_content.append('                        scales: {')
                html_content.append('                            x: {')
                html_content.append('                                grid: {')
                html_content.append('                                    display: false  // 禁用x轴网格线（纵向线不显示）')
                html_content.append('                                }')
                html_content.append('                            },')
                html_content.append('                            "y-axis-roe": {')
                html_content.append('                                title: {')
                html_content.append('                                    display: true,')
                html_content.append('                                    text: "回报率 (%)"')
                html_content.append('                                }')
                html_content.append('                            }')
                html_content.append('                        },')
                html_content.append('                        plugins: {')
                html_content.append('                            title: {')
                html_content.append('                                display: true,')
                html_content.append('                                text: "年度净资产收益率、总资产报酬率与投入资本回报率趋势"')
                html_content.append('                            },')
                html_content.append('                            legend: {')
                html_content.append('                                display: true,')
                html_content.append('                                position: "top"')
                html_content.append('                            }')
                html_content.append('                        }')
                html_content.append('                    }')
                html_content.append('                });')
                html_content.append('            });')
                html_content.append('        </script>')

            # Remove "年度营收增长率" and "年度利润增长率" columns if they exist
            annual_indicators_filtered = annual_indicators.copy()
            columns_to_remove = ['年度营收增长率', '年度利润增长率']
            for col in columns_to_remove:
                if col in annual_indicators_filtered.columns:
                    annual_indicators_filtered = annual_indicators_filtered.drop(columns=[col])

            html_content.append(self._df_to_html_table(annual_indicators_filtered))
            html_content.append('        </div>')

        # Quarterly financial indicators
        quarterly_indicators = data_extractor_result.get('quarterly_indicators', pd.DataFrame())
        if not quarterly_indicators.empty:
            html_content.append('        <div class="subsection">')
            html_content.append('            <h3>季度财务指标数据</h3>')

            # Add chart for quarterly margins (net profit margin and gross profit margin)
            if '单季度销售净利率' in quarterly_indicators.columns and '单季度销售毛利率' in quarterly_indicators.columns:
                # Prepare chart data
                q_margin_periods = quarterly_indicators['报告期'].tolist()
                q_netprofit_margins = quarterly_indicators['单季度销售净利率'].tolist() if '单季度销售净利率' in quarterly_indicators.columns else []
                q_grossprofit_margins = quarterly_indicators['单季度销售毛利率'].tolist() if '单季度销售毛利率' in quarterly_indicators.columns else []

                # Filter out null values for chart
                valid_data = [(period, net_margin, gross_margin) for period, net_margin, gross_margin in zip(q_margin_periods, q_netprofit_margins, q_grossprofit_margins)
                             if pd.notna(net_margin) and pd.notna(gross_margin)]
                if valid_data:
                    chart_q_periods, chart_q_net_margins, chart_q_gross_margins = zip(*valid_data)
                else:
                    chart_q_periods, chart_q_net_margins, chart_q_gross_margins = q_margin_periods, q_netprofit_margins, q_grossprofit_margins

                # Create chart container
                html_content.append('        <div class="chart-container">')
                html_content.append('            <canvas id="quarterlyMarginsChart"></canvas>')
                html_content.append('        </div>')

                # Add JavaScript for the chart
                html_content.append('        <script>')
                html_content.append('            document.addEventListener("DOMContentLoaded", function() {')
                html_content.append('                const ctx = document.getElementById("quarterlyMarginsChart").getContext("2d");')
                html_content.append('                const quarterlyMarginsChart = new Chart(ctx, {')
                html_content.append('                    type: "line",')
                html_content.append('                    data: {')
                html_content.append('                        labels: [' + ', '.join([f'"{period}"' for period in chart_q_periods]) + '],')
                html_content.append('                        datasets: [')
                html_content.append('                            {')
                html_content.append('                                label: "单季度销售净利率 (%)",')
                html_content.append('                                data: [' + ', '.join([str(net_margin) if pd.notna(net_margin) else 'null' for net_margin in chart_q_net_margins]) + '],')
                html_content.append('                                borderColor: "rgba(87, 160, 229, 1)",      // 蓝色')
                html_content.append('                                backgroundColor: "rgba(87, 160, 229, 1)",  // 与线条同色')
                html_content.append('                                borderWidth: 3,')
                html_content.append('                                pointBackgroundColor: "rgba(87, 160, 229, 1)",')
                html_content.append('                                pointBorderColor: "rgba(255, 255, 255, 0)",  // 透明点')
                html_content.append('                                pointRadius: 5,')
                html_content.append('                                fill: false,')
                html_content.append('                                tension: 0.4, // for smooth curves')
                html_content.append('                                yAxisID: "y-axis-q-margin",')
                html_content.append('                            },')
                html_content.append('                            {')
                html_content.append('                                label: "单季度销售毛利率 (%)",')
                html_content.append('                                data: [' + ', '.join([str(gross_margin) if pd.notna(gross_margin) else 'null' for gross_margin in chart_q_gross_margins]) + '],')
                html_content.append('                                borderColor: "rgba(241, 138, 158, 1)",      // 指定颜色')
                html_content.append('                                backgroundColor: "rgba(241, 138, 158, 1)",  // 与线条同色')
                html_content.append('                                borderWidth: 2,')
                html_content.append('                                pointBackgroundColor: "rgba(241, 138, 158, 1)",')
                html_content.append('                                pointBorderColor: "rgba(255, 255, 255, 0)",  // 透明点')
                html_content.append('                                pointRadius: 4,')
                html_content.append('                                fill: false,')
                html_content.append('                                type: "line",')
                html_content.append('                                tension: 0.4, // for smooth curves')
                html_content.append('                                yAxisID: "y-axis-q-margin",')
                html_content.append('                            }')
                html_content.append('                        ]')
                html_content.append('                    },')
                html_content.append('                    options: {')
                html_content.append('                        responsive: true,')
                html_content.append('                        scales: {')
                html_content.append('                            x: {')
                html_content.append('                                grid: {')
                html_content.append('                                    display: false  // 禁用x轴网格线（纵向线不显示）')
                html_content.append('                                }')
                html_content.append('                            },')
                html_content.append('                            "y-axis-q-margin": {')
                html_content.append('                                title: {')
                html_content.append('                                    display: true,')
                html_content.append('                                    text: "利润率 (%)"')
                html_content.append('                                }')
                html_content.append('                            }')
                html_content.append('                        },')
                html_content.append('                        plugins: {')
                html_content.append('                            title: {')
                html_content.append('                                display: true,')
                html_content.append('                                text: "单季度销售净利率与毛利率趋势"')
                html_content.append('                            },')
                html_content.append('                            legend: {')
                html_content.append('                                display: true,')
                html_content.append('                                position: "top"')
                html_content.append('                            }')
                html_content.append('                        }')
                html_content.append('                    }')
                html_content.append('                });')
                html_content.append('            });')
                html_content.append('        </script>')

            # Remove quarterly growth rate columns if they exist
            quarterly_indicators_filtered = quarterly_indicators.copy()
            columns_to_remove = ['营收同比增长率', '营收环比增长率', '利润同比增长率', '利润环比增长率']
            for col in columns_to_remove:
                if col in quarterly_indicators_filtered.columns:
                    quarterly_indicators_filtered = quarterly_indicators_filtered.drop(columns=[col])

            html_content.append(self._df_to_html_table(quarterly_indicators_filtered))
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
        if pe_ttm is not None and pe_ttm != 'N/A':
            try:
                pe_ttm_formatted = f"{float(pe_ttm):.1f}"
            except (ValueError, TypeError):
                pe_ttm_formatted = 'N/A'
        else:
            pe_ttm_formatted = 'N/A'

        if pb is not None and pb != 'N/A':
            try:
                pb_formatted = f"{float(pb):.1f}"
            except (ValueError, TypeError):
                pb_formatted = 'N/A'
        else:
            pb_formatted = 'N/A'

        if total_mv is not None and total_mv != 'N/A':
            try:
                total_mv_formatted = f"{float(total_mv):.1f}"
            except (ValueError, TypeError):
                total_mv_formatted = 'N/A'
        else:
            total_mv_formatted = 'N/A'

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
        if website != 'N/A' and website.startswith(('http://', 'https://')):
            html_content.append(f'            <li><strong>公司网址：</strong> <a href="{website}" target="_blank">{website}</a></li>')
        else:
            html_content.append(f'            <li><strong>公司网址：</strong> {website}</li>')
        html_content.append(f'        </ul>')
        html_content.append('    </div>')
        














        # Close HTML tags
        html_content.append('</body>')
        html_content.append('</html>')

        # Join all content
        final_content = "\n".join(html_content)

        # Save to file
        if index is not None:
            filename = f"{index}.{company_name}_{stock_code}_{today.replace('年', '').replace('月', '').replace('日', '')}.html"
        else:
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

    def _convert_stock_code_for_east_money(self, stock_code: str) -> str:
        """
        将股票代码转换为东方财富网格式
        e.g., '000572.SZ' -> 'sz000572', '600000.SH' -> 'sh600000'
        """
        if '.' in stock_code:
            code, exchange = stock_code.split('.', 1)
            exchange = exchange.lower()
            return f"{exchange}{code}"
        else:
            # 如果没有交易所后缀，则默认使用原始代码
            return stock_code


def main():
    """
    主函数，演示内容整合功能
    """
    # This is a placeholder - in a real scenario, this would receive actual data from the other modules
    print("内容整合模块已准备就绪。需要从数据提取模块和文本生成模块接收数据以生成最终报告。")


if __name__ == "__main__":
    main()