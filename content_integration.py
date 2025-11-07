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
        
        # HTML Header with basic styling and Chart.js
        html_content.append('<!DOCTYPE html>')
        html_content.append('<html lang="zh-CN">')
        html_content.append('<head>')
        html_content.append('    <meta charset="UTF-8">')
        html_content.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html_content.append('    <title>{}（{}）公司分析报告</title>'.format(company_name, stock_code))
        html_content.append('    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>')
        html_content.append('    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>')
        html_content.append('    <script>')
        html_content.append('        // Register the datalabels plugin globally')
        html_content.append('        if (typeof Chart !== "undefined" && typeof ChartDataLabels !== "undefined") {')
        html_content.append('            Chart.register(ChartDataLabels);')
        html_content.append('        }')
        html_content.append('    </script>')
        html_content.append('    <style>')
        html_content.append('        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }')
        html_content.append('        h1, h2, h3 { color: #333; }')
        html_content.append('        h1 { border-bottom: 2px solid #333; padding-bottom: 10px; }')
        html_content.append('        table { border-collapse: collapse; width: 100%; margin: 10px 0; }')
        html_content.append('        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }')
        html_content.append('        th { background-color: #f2f2f2; }')
        html_content.append('        .section { margin: 20px 0; }')
        html_content.append('        .subsection { margin: 15px 0; }')
        html_content.append('        .chart-container { width: 100%; height: 400px; margin: 20px 0; }')
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
            # Add visualization for annual revenue with growth rate
            html_content.append('            <div class="chart-container">')
            html_content.append('                <canvas id="annualRevenueChart"></canvas>')
            html_content.append('            </div>')
            
            # Combine revenue and growth data in the same table
            if not annual_indicators.empty and 'annual_tr_yoy' in annual_indicators.columns:
                # Merge revenue and growth data
                combined_annual_revenue = annual_revenue.merge(
                    annual_indicators[['end_date', 'annual_tr_yoy']], 
                    on='end_date', 
                    how='left'
                )
                combined_annual_revenue = combined_annual_revenue.rename(columns={'annual_tr_yoy': '年度营收增长率(%)'})
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
            # Add visualization for annual net profit with growth rate
            html_content.append('            <div class="chart-container">')
            html_content.append('                <canvas id="annualNetProfitChart"></canvas>')
            html_content.append('            </div>')
            
            # Combine net profit and growth data in the same table
            if not annual_indicators.empty and 'annual_netprofit_yoy' in annual_indicators.columns:
                # Merge net profit and growth data
                combined_annual_net_profit = annual_net_profit.merge(
                    annual_indicators[['end_date', 'annual_netprofit_yoy']], 
                    on='end_date', 
                    how='left'
                )
                combined_annual_net_profit = combined_annual_net_profit.rename(columns={'annual_netprofit_yoy': '年度利润增长率(%)'})
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
            # Add visualization for quarterly revenue with growth rates
            html_content.append('            <div class="chart-container">')
            html_content.append('                <canvas id="quarterlyRevenueChart"></canvas>')
            html_content.append('            </div>')
            
            # Combine quarterly revenue and growth data in the same table
            if not quarterly_indicators.empty and 'quarterly_gr_yoy' in quarterly_indicators.columns and 'quarterly_gr_qoq' in quarterly_indicators.columns:
                # Merge quarterly revenue and growth data
                combined_quarterly_revenue = quarterly_revenue.merge(
                    quarterly_indicators[['end_date', 'quarterly_gr_yoy', 'quarterly_gr_qoq']], 
                    on='end_date', 
                    how='left'
                )
                combined_quarterly_revenue = combined_quarterly_revenue.rename(columns={
                    'quarterly_gr_yoy': '季度营收同比增长率(%)',
                    'quarterly_gr_qoq': '季度营收环比增长率(%)'
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
            # Add visualization for quarterly net profit with growth rates
            html_content.append('            <div class="chart-container">')
            html_content.append('                <canvas id="quarterlyNetProfitChart"></canvas>')
            html_content.append('            </div>')
            
            # Combine quarterly net profit and growth data in the same table
            if not quarterly_indicators.empty and 'quarterly_profit_yoy' in quarterly_indicators.columns and 'quarterly_profit_qoq' in quarterly_indicators.columns:
                # Merge quarterly net profit and growth data
                combined_quarterly_net_profit = quarterly_net_profit.merge(
                    quarterly_indicators[['end_date', 'quarterly_profit_yoy', 'quarterly_profit_qoq']], 
                    on='end_date', 
                    how='left'
                )
                combined_quarterly_net_profit = combined_quarterly_net_profit.rename(columns={
                    'quarterly_profit_yoy': '季度利润同比增长率(%)',
                    'quarterly_profit_qoq': '季度利润环比增长率(%)'
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
            # Add visualization for annual cash flow
            html_content.append('            <div class="chart-container">')
            html_content.append('                <canvas id="annualCashFlowChart"></canvas>')
            html_content.append('            </div>')
            html_content.append(self._df_to_html_table(annual_cashflow))
            html_content.append('        </div>')
        
        # Quarterly cash flow statement
        quarterly_cashflow = data_extractor_result.get('quarterly_cashflow', pd.DataFrame())
        if not quarterly_cashflow.empty:
            html_content.append('        <div class="subsection">')
            html_content.append('            <h3>季度现金流量表数据</h3>')
            # Add visualization for quarterly cash flow
            html_content.append('            <div class="chart-container">')
            html_content.append('                <canvas id="quarterlyCashFlowChart"></canvas>')
            html_content.append('            </div>')
            html_content.append(self._df_to_html_table(quarterly_cashflow))
            html_content.append('        </div>')
        
        # Annual financial indicators
        annual_indicators = data_extractor_result.get('annual_indicators', pd.DataFrame())
        if not annual_indicators.empty:
            html_content.append('        <div class="subsection">')
            html_content.append('            <h3>年度财务指标数据</h3>')
            # Add visualizations for annual financial indicators
            html_content.append('            <div class="chart-container">')
            html_content.append('                <canvas id="annualMarginsChart"></canvas>')
            html_content.append('            </div>')
            html_content.append('            <div class="chart-container">')
            html_content.append('                <canvas id="annualROEChart"></canvas>')
            html_content.append('            </div>')
            html_content.append('            <div class="chart-container">')
            html_content.append('                <canvas id="annualGrowthChart"></canvas>')
            html_content.append('            </div>')
            html_content.append(self._df_to_html_table(annual_indicators))
            html_content.append('        </div>')
        
        # Quarterly financial indicators
        quarterly_indicators = data_extractor_result.get('quarterly_indicators', pd.DataFrame())
        if not quarterly_indicators.empty:
            html_content.append('        <div class="subsection">')
            html_content.append('            <h3>季度财务指标数据</h3>')
            # Add visualizations for quarterly financial indicators
            html_content.append('            <div class="chart-container">')
            html_content.append('                <canvas id="quarterlyMarginsChart"></canvas>')
            html_content.append('            </div>')
            html_content.append('            <div class="chart-container">')
            html_content.append('                <canvas id="quarterlyGrowthYoYChart"></canvas>')
            html_content.append('            </div>')
            html_content.append('            <div class="chart-container">')
            html_content.append('                <canvas id="quarterlyGrowthQoQChart"></canvas>')
            html_content.append('            </div>')
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

        # Add script for chart initialization
        html_content.append('    <script>')
        html_content.append('        // Helper function to safely convert data values to avoid NaN issues')
        html_content.append('        function safeDataConvert(data) {')
        html_content.append('            return data.map(value => {')
        html_content.append('                if (value === null || value === undefined || isNaN(value)) {')
        html_content.append('                    return null;')
        html_content.append('                }')
        html_content.append('                return value;')
        html_content.append('            });')
        html_content.append('        }')
        
        # Annual revenue chart (combine revenue and growth rate on dual y-axes)
        if not annual_revenue.empty and not annual_indicators.empty:
            # Prepare data for annual revenue chart
            annual_years = annual_revenue['end_date'].tolist()
            annual_revenue_values = annual_revenue['annual_total_revenue'].tolist() if 'annual_total_revenue' in annual_revenue.columns else []
            
            # Prepare data for annual growth rate
            annual_tr_yoy_values = annual_indicators['annual_tr_yoy'].tolist() if 'annual_tr_yoy' in annual_indicators.columns else []

            # Only create chart if at least one dataset has values
            if annual_revenue_values or annual_tr_yoy_values:
                html_content.append('        try {')
                html_content.append('            const annualRevenueCtx = document.getElementById("annualRevenueChart").getContext("2d");')
                html_content.append('            new Chart(annualRevenueCtx, {')
                html_content.append('                type: "bar",')
                html_content.append('                data: {')
                # Safely format labels to avoid issues with quotes
                safe_labels = [str(year).replace('"', '&quot;') for year in annual_years]
                html_content.append('                    labels: [{}],'.format(', '.join([f'"{label}"' for label in safe_labels])))
                html_content.append('                    datasets: [')
                if annual_revenue_values:
                    # Convert data to avoid NaN issues
                    safe_revenue_values = []
                    for val in annual_revenue_values:
                        if pd.isna(val) or val is None:
                            safe_revenue_values.append('null')
                        else:
                            safe_revenue_values.append(str(float(val)) if val is not None else 'null')
                    html_content.append('                    {')
                    html_content.append('                        label: "年度营业收入（亿元）",')
                    html_content.append('                        data: [{}],'.format(', '.join(safe_revenue_values)))
                    html_content.append('                        backgroundColor: "rgba(54, 162, 235, 0.5)",')
                    html_content.append('                        borderColor: "rgba(54, 162, 235, 1)",')
                    html_content.append('                        borderWidth: 1,')
                    html_content.append('                        yAxisID: "y"')
                    html_content.append('                    }')
                if annual_tr_yoy_values:
                    # Convert data to avoid NaN issues
                    safe_growth_values = []
                    for val in annual_tr_yoy_values:
                        if pd.isna(val) or val is None:
                            safe_growth_values.append('null')
                        else:
                            safe_growth_values.append(str(float(val)) if val is not None else 'null')
                    html_content.append('                    {')
                    html_content.append('                        label: "年度营收增长率(%)",')
                    html_content.append('                        data: [{}],'.format(', '.join(safe_growth_values)))
                    html_content.append('                        borderColor: "rgba(255, 205, 86, 1)",')
                    html_content.append('                        backgroundColor: "rgba(255, 205, 86, 0.2)",')
                    html_content.append('                        tension: 0.4,')
                    html_content.append('                        fill: false,')
                    html_content.append('                        type: "line",')
                    html_content.append('                        yAxisID: "y1"')
                    html_content.append('                    }')
                html_content.append('                ]')
                html_content.append('            },')
                html_content.append('            options: {')
                html_content.append('                responsive: true,')
                html_content.append('                maintainAspectRatio: false,')
                html_content.append('                scales: {')
                html_content.append('                    y: {')
                html_content.append('                        beginAtZero: true,')
                html_content.append('                        type: "linear",')
                html_content.append('                        display: true,')
                html_content.append('                        position: "left",')
                html_content.append('                        title: {')
                html_content.append('                            display: true,')
                html_content.append('                            text: "金额（亿元）"')
                html_content.append('                        }')
                html_content.append('                    },')
                html_content.append('                    y1: {')
                html_content.append('                        beginAtZero: false,')
                html_content.append('                        type: "linear",')
                html_content.append('                        display: true,')
                html_content.append('                        position: "right",')
                html_content.append('                        title: {')
                html_content.append('                            display: true,')
                html_content.append('                            text: "增长率(%)"')
                html_content.append('                        },')
                html_content.append('                        grid: {')
                html_content.append('                            drawOnChartArea: false')
                html_content.append('                        }')
                html_content.append('                    }')
                html_content.append('                },')
                html_content.append('                plugins: {')
                html_content.append('                    title: {')
                html_content.append('                        display: true,')
                html_content.append('                        text: "年度营业收入与营收增长率"')
                html_content.append('                    }')
                html_content.append('                }')
                html_content.append('            });')
                html_content.append('        } catch (error) {')
                html_content.append('            console.error("Annual revenue chart failed to render:", error);')
                html_content.append('        }')
        
        # Annual net profit chart (combine net profit and growth rate on dual y-axes)
        if not annual_net_profit.empty and not annual_indicators.empty:
            # Prepare data for annual net profit chart
            annual_net_profit_years = annual_net_profit['end_date'].tolist()
            annual_net_profit_values = annual_net_profit['annual_n_income_attr_p'].tolist() if 'annual_n_income_attr_p' in annual_net_profit.columns else []
            
            # Prepare data for annual growth rate
            annual_netprofit_yoy_values = annual_indicators['annual_netprofit_yoy'].tolist() if 'annual_netprofit_yoy' in annual_indicators.columns else []

            # Only create chart if at least one dataset has values
            if annual_net_profit_values or annual_netprofit_yoy_values:
                html_content.append('        try {')
                html_content.append('            const annualNetProfitCtx = document.getElementById("annualNetProfitChart").getContext("2d");')
                html_content.append('            new Chart(annualNetProfitCtx, {')
                html_content.append('                type: "bar",')
                html_content.append('                data: {')
                # Safely format labels to avoid issues with quotes
                safe_net_labels = [str(year).replace('"', '&quot;') for year in annual_net_profit_years]
                html_content.append('                    labels: [{}],'.format(', '.join([f'"{label}"' for label in safe_net_labels])))
                html_content.append('                    datasets: [')
                if annual_net_profit_values:
                    # Convert data to avoid NaN issues
                    safe_net_values = []
                    for val in annual_net_profit_values:
                        if pd.isna(val) or val is None:
                            safe_net_values.append('null')
                        else:
                            safe_net_values.append(str(float(val)) if val is not None else 'null')
                    html_content.append('                    {')
                    html_content.append('                        label: "年度归母净利润（亿元）",')
                    html_content.append('                        data: [{}],'.format(', '.join(safe_net_values)))
                    html_content.append('                        backgroundColor: "rgba(255, 99, 132, 0.5)",')
                    html_content.append('                        borderColor: "rgba(255, 99, 132, 1)",')
                    html_content.append('                        borderWidth: 1,')
                    html_content.append('                        yAxisID: "y"')
                    html_content.append('                    }')
                if annual_netprofit_yoy_values:
                    # Convert data to avoid NaN issues
                    safe_net_growth_values = []
                    for val in annual_netprofit_yoy_values:
                        if pd.isna(val) or val is None:
                            safe_net_growth_values.append('null')
                        else:
                            safe_net_growth_values.append(str(float(val)) if val is not None else 'null')
                    html_content.append('                    {')
                    html_content.append('                        label: "年度利润增长率(%)",')
                    html_content.append('                        data: [{}],'.format(', '.join(safe_net_growth_values)))
                    html_content.append('                        borderColor: "rgba(201, 203, 207, 1)",')
                    html_content.append('                        backgroundColor: "rgba(201, 203, 207, 0.2)",')
                    html_content.append('                        tension: 0.4,')
                    html_content.append('                        fill: false,')
                    html_content.append('                        type: "line",')
                    html_content.append('                        yAxisID: "y1"')
                    html_content.append('                    }')
                html_content.append('                ]')
                html_content.append('            },')
                html_content.append('            options: {')
                html_content.append('                responsive: true,')
                html_content.append('                maintainAspectRatio: false,')
                html_content.append('                scales: {')
                html_content.append('                    y: {')
                html_content.append('                        beginAtZero: true,')
                html_content.append('                        type: "linear",')
                html_content.append('                        display: true,')
                html_content.append('                        position: "left",')
                html_content.append('                        title: {')
                html_content.append('                            display: true,')
                html_content.append('                            text: "金额（亿元）"')
                html_content.append('                        }')
                html_content.append('                    },')
                html_content.append('                    y1: {')
                html_content.append('                        beginAtZero: false,')
                html_content.append('                        type: "linear",')
                html_content.append('                        display: true,')
                html_content.append('                        position: "right",')
                html_content.append('                        title: {')
                html_content.append('                            display: true,')
                html_content.append('                            text: "增长率(%)"')
                html_content.append('                        },')
                html_content.append('                        grid: {')
                html_content.append('                            drawOnChartArea: false')
                html_content.append('                        }')
                html_content.append('                    }')
                html_content.append('                },')
                html_content.append('                plugins: {')
                html_content.append('                    title: {')
                html_content.append('                        display: true,')
                html_content.append('                        text: "年度归母净利润与利润增长率"')
                html_content.append('                    }')
                html_content.append('                }')
                html_content.append('            });')
                html_content.append('        } catch (error) {')
                html_content.append('            console.error("Annual net profit chart failed to render:", error);')
                html_content.append('        }')
        
        # Quarterly revenue chart (combine revenue and growth rates on dual y-axes)
        if not quarterly_revenue.empty and not quarterly_indicators.empty:
            # Prepare data for quarterly revenue chart
            quarterly_periods = quarterly_revenue['end_date'].tolist()
            quarterly_revenue_values = quarterly_revenue['quarterly_total_revenue'].tolist() if 'quarterly_total_revenue' in quarterly_revenue.columns else []
            
            # Prepare data for quarterly growth rates
            quarterly_gr_yoy_values = quarterly_indicators['quarterly_gr_yoy'].tolist() if 'quarterly_gr_yoy' in quarterly_indicators.columns else []
            quarterly_gr_qoq_values = quarterly_indicators['quarterly_gr_qoq'].tolist() if 'quarterly_gr_qoq' in quarterly_indicators.columns else []

            # Only create chart if at least one dataset has values
            if quarterly_revenue_values or quarterly_gr_yoy_values or quarterly_gr_qoq_values:
                html_content.append('        try {')
                html_content.append('            const quarterlyRevenueCtx = document.getElementById("quarterlyRevenueChart").getContext("2d");')
                html_content.append('            new Chart(quarterlyRevenueCtx, {')
                html_content.append('                type: "bar",')
                html_content.append('                data: {')
                # Safely format labels to avoid issues with quotes
                safe_quarterly_labels = [str(period).replace('"', '&quot;') for period in quarterly_periods]
                html_content.append('                    labels: [{}],'.format(', '.join([f'"{label}"' for label in safe_quarterly_labels])))
                html_content.append('                    datasets: [')
                if quarterly_revenue_values:
                    # Convert data to avoid NaN issues
                    safe_quarterly_revenue_values = []
                    for val in quarterly_revenue_values:
                        if pd.isna(val) or val is None:
                            safe_quarterly_revenue_values.append('null')
                        else:
                            safe_quarterly_revenue_values.append(str(float(val)) if val is not None else 'null')
                    html_content.append('                    {')
                    html_content.append('                        label: "季度营业收入（亿元）",')
                    html_content.append('                        data: [{}],'.format(', '.join(safe_quarterly_revenue_values)))
                    html_content.append('                        backgroundColor: "rgba(75, 192, 192, 0.5)",')
                    html_content.append('                        borderColor: "rgba(75, 192, 192, 1)",')
                    html_content.append('                        borderWidth: 1,')
                    html_content.append('                        yAxisID: "y"')
                    html_content.append('                    }')
                if quarterly_gr_yoy_values:
                    # Convert data to avoid NaN issues
                    safe_quarterly_yoy_values = []
                    for val in quarterly_gr_yoy_values:
                        if pd.isna(val) or val is None:
                            safe_quarterly_yoy_values.append('null')
                        else:
                            safe_quarterly_yoy_values.append(str(float(val)) if val is not None else 'null')
                    html_content.append('                    {')
                    html_content.append('                        label: "季度营收同比增长率(%)",')
                    html_content.append('                        data: [{}],'.format(', '.join(safe_quarterly_yoy_values)))
                    html_content.append('                        borderColor: "rgba(75, 192, 192, 1)",')
                    html_content.append('                        backgroundColor: "rgba(75, 192, 192, 0.2)",')
                    html_content.append('                        tension: 0.4,')
                    html_content.append('                        fill: false,')
                    html_content.append('                        type: "line",')
                    html_content.append('                        yAxisID: "y1"')
                    html_content.append('                    }')
                if quarterly_gr_qoq_values:
                    # Convert data to avoid NaN issues
                    safe_quarterly_qoq_values = []
                    for val in quarterly_gr_qoq_values:
                        if pd.isna(val) or val is None:
                            safe_quarterly_qoq_values.append('null')
                        else:
                            safe_quarterly_qoq_values.append(str(float(val)) if val is not None else 'null')
                    html_content.append('                    {')
                    html_content.append('                        label: "季度营收环比增长率(%)",')
                    html_content.append('                        data: [{}],'.format(', '.join(safe_quarterly_qoq_values)))
                    html_content.append('                        borderColor: "rgba(153, 102, 255, 1)",')
                    html_content.append('                        backgroundColor: "rgba(153, 102, 255, 0.2)",')
                    html_content.append('                        tension: 0.4,')
                    html_content.append('                        fill: false,')
                    html_content.append('                        type: "line",')
                    html_content.append('                        yAxisID: "y1"')
                    html_content.append('                    }')
                html_content.append('                ]')
                html_content.append('            },')
                html_content.append('            options: {')
                html_content.append('                responsive: true,')
                html_content.append('                maintainAspectRatio: false,')
                html_content.append('                scales: {')
                html_content.append('                    y: {')
                html_content.append('                        beginAtZero: true,')
                html_content.append('                        type: "linear",')
                html_content.append('                        display: true,')
                html_content.append('                        position: "left",')
                html_content.append('                        title: {')
                html_content.append('                            display: true,')
                html_content.append('                            text: "金额（亿元）"')
                html_content.append('                        }')
                html_content.append('                    },')
                html_content.append('                    y1: {')
                html_content.append('                        beginAtZero: false,')
                html_content.append('                        type: "linear",')
                html_content.append('                        display: true,')
                html_content.append('                        position: "right",')
                html_content.append('                        title: {')
                html_content.append('                            display: true,')
                html_content.append('                            text: "增长率(%)"')
                html_content.append('                        },')
                html_content.append('                        grid: {')
                html_content.append('                            drawOnChartArea: false')
                html_content.append('                        }')
                html_content.append('                    }')
                html_content.append('                },')
                html_content.append('                plugins: {')
                html_content.append('                    title: {')
                html_content.append('                        display: true,')
                html_content.append('                        text: "季度营业收入与营收增长率"')
                html_content.append('                    }')
                html_content.append('                }')
                html_content.append('            });')
                html_content.append('        } catch (error) {')
                html_content.append('            console.error("Quarterly revenue chart failed to render:", error);')
                html_content.append('        }')
        
        # Quarterly net profit chart (combine net profit and growth rates on dual y-axes)
        if not quarterly_net_profit.empty and not quarterly_indicators.empty:
            # Prepare data for quarterly net profit chart
            quarterly_net_profit_periods = quarterly_net_profit['end_date'].tolist()
            quarterly_net_profit_values = quarterly_net_profit['quarterly_n_income_attr_p'].tolist() if 'quarterly_n_income_attr_p' in quarterly_net_profit.columns else []
            
            # Prepare data for quarterly growth rates
            quarterly_profit_yoy_values = quarterly_indicators['quarterly_profit_yoy'].tolist() if 'quarterly_profit_yoy' in quarterly_indicators.columns else []
            quarterly_profit_qoq_values = quarterly_indicators['quarterly_profit_qoq'].tolist() if 'quarterly_profit_qoq' in quarterly_indicators.columns else []

            # Only create chart if at least one dataset has values
            if quarterly_net_profit_values or quarterly_profit_yoy_values or quarterly_profit_qoq_values:
                html_content.append('        try {')
                html_content.append('            const quarterlyNetProfitCtx = document.getElementById("quarterlyNetProfitChart").getContext("2d");')
                html_content.append('            new Chart(quarterlyNetProfitCtx, {')
                html_content.append('                type: "bar",')
                html_content.append('                data: {')
                # Safely format labels to avoid issues with quotes
                safe_quarterly_net_labels = [str(period).replace('"', '&quot;') for period in quarterly_net_profit_periods]
                html_content.append('                    labels: [{}],'.format(', '.join([f'"{label}"' for label in safe_quarterly_net_labels])))
                html_content.append('                    datasets: [')
                if quarterly_net_profit_values:
                    # Convert data to avoid NaN issues
                    safe_quarterly_net_values = []
                    for val in quarterly_net_profit_values:
                        if pd.isna(val) or val is None:
                            safe_quarterly_net_values.append('null')
                        else:
                            safe_quarterly_net_values.append(str(float(val)) if val is not None else 'null')
                    html_content.append('                    {')
                    html_content.append('                        label: "季度归母净利润（亿元）",')
                    html_content.append('                        data: [{}],'.format(', '.join(safe_quarterly_net_values)))
                    html_content.append('                        backgroundColor: "rgba(153, 102, 255, 0.5)",')
                    html_content.append('                        borderColor: "rgba(153, 102, 255, 1)",')
                    html_content.append('                        borderWidth: 1,')
                    html_content.append('                        yAxisID: "y"')
                    html_content.append('                    }')
                if quarterly_profit_yoy_values:
                    # Convert data to avoid NaN issues
                    safe_quarterly_profit_yoy_values = []
                    for val in quarterly_profit_yoy_values:
                        if pd.isna(val) or val is None:
                            safe_quarterly_profit_yoy_values.append('null')
                        else:
                            safe_quarterly_profit_yoy_values.append(str(float(val)) if val is not None else 'null')
                    html_content.append('                    {')
                    html_content.append('                        label: "季度利润同比增长率(%)",')
                    html_content.append('                        data: [{}],'.format(', '.join(safe_quarterly_profit_yoy_values)))
                    html_content.append('                        borderColor: "rgba(75, 192, 192, 1)",')
                    html_content.append('                        backgroundColor: "rgba(75, 192, 192, 0.2)",')
                    html_content.append('                        tension: 0.4,')
                    html_content.append('                        fill: false,')
                    html_content.append('                        type: "line",')
                    html_content.append('                        yAxisID: "y1"')
                    html_content.append('                    }')
                if quarterly_profit_qoq_values:
                    # Convert data to avoid NaN issues
                    safe_quarterly_profit_qoq_values = []
                    for val in quarterly_profit_qoq_values:
                        if pd.isna(val) or val is None:
                            safe_quarterly_profit_qoq_values.append('null')
                        else:
                            safe_quarterly_profit_qoq_values.append(str(float(val)) if val is not None else 'null')
                    html_content.append('                    {')
                    html_content.append('                        label: "季度利润环比增长率(%)",')
                    html_content.append('                        data: [{}],'.format(', '.join(safe_quarterly_profit_qoq_values)))
                    html_content.append('                        borderColor: "rgba(201, 203, 207, 1)",')
                    html_content.append('                        backgroundColor: "rgba(201, 203, 207, 0.2)",')
                    html_content.append('                        tension: 0.4,')
                    html_content.append('                        fill: false,')
                    html_content.append('                        type: "line",')
                    html_content.append('                        yAxisID: "y1"')
                    html_content.append('                    }')
                html_content.append('                ]')
                html_content.append('            },')
                html_content.append('            options: {')
                html_content.append('                responsive: true,')
                html_content.append('                maintainAspectRatio: false,')
                html_content.append('                scales: {')
                html_content.append('                    y: {')
                html_content.append('                        beginAtZero: true,')
                html_content.append('                        type: "linear",')
                html_content.append('                        display: true,')
                html_content.append('                        position: "left",')
                html_content.append('                        title: {')
                html_content.append('                            display: true,')
                html_content.append('                            text: "金额（亿元）"')
                html_content.append('                        }')
                html_content.append('                    },')
                html_content.append('                    y1: {')
                html_content.append('                        beginAtZero: false,')
                html_content.append('                        type: "linear",')
                html_content.append('                        display: true,')
                html_content.append('                        position: "right",')
                html_content.append('                        title: {')
                html_content.append('                            display: true,')
                html_content.append('                            text: "增长率(%)"')
                html_content.append('                        },')
                html_content.append('                        grid: {')
                html_content.append('                            drawOnChartArea: false')
                html_content.append('                        }')
                html_content.append('                    }')
                html_content.append('                },')
                html_content.append('                plugins: {')
                html_content.append('                    title: {')
                html_content.append('                        display: true,')
                html_content.append('                        text: "季度归母净利润与利润增长率"')
                html_content.append('                    }')
                html_content.append('                }')
                html_content.append('            });')
                html_content.append('        } catch (error) {')
                html_content.append('            console.error("Quarterly net profit chart failed to render:", error);')
                html_content.append('        }')
        
        # Annual cash flow chart
        if not annual_cashflow.empty:
            annual_cashflow_periods = annual_cashflow['end_date'].tolist()
            annual_cashflow_values = annual_cashflow['annual_n_cashflow_act'].tolist() if 'annual_n_cashflow_act' in annual_cashflow.columns else []
            
            html_content.append('        const annualCashFlowCtx = document.getElementById("annualCashFlowChart").getContext("2d");')
            html_content.append('        new Chart(annualCashFlowCtx, {')
            html_content.append('            type: "bar",')
            html_content.append('            data: {')
            html_content.append('                labels: [{}],'.format(', '.join([f'"{period}"' for period in annual_cashflow_periods])))
            html_content.append('                datasets: [')
            if annual_cashflow_values:
                html_content.append('                    {')
                html_content.append('                        label: "年度经营现金流净额（亿元）",')
                html_content.append('                        data: [{}],'.format(', '.join([str(val) if pd.notna(val) else 'null' for val in annual_cashflow_values])))
                html_content.append('                        backgroundColor: "rgba(255, 159, 64, 0.5)",')
                html_content.append('                        borderColor: "rgba(255, 159, 64, 1)",')
                html_content.append('                        borderWidth: 1')
                html_content.append('                    }')
            html_content.append('                ]')
            html_content.append('            },')
            html_content.append('            options: {')
            html_content.append('                responsive: true,')
            html_content.append('                maintainAspectRatio: false,')
            html_content.append('                scales: {')
            html_content.append('                    y: {')
            html_content.append('                        title: {')
            html_content.append('                            display: true,')
            html_content.append('                            text: "金额（亿元）"')
            html_content.append('                        }')
            html_content.append('                    }')
            html_content.append('                },')
            html_content.append('                plugins: {')
            html_content.append('                    title: {')
            html_content.append('                        display: true,')
            html_content.append('                        text: "年度经营现金流净额"')
            html_content.append('                    }')
            html_content.append('                },')
            html_content.append('                annotation: {')
            html_content.append('                    annotations: []')
            html_content.append('                }')
            html_content.append('            }')
            html_content.append('        });')
        
        # Quarterly cash flow chart
        if not quarterly_cashflow.empty:
            quarterly_cashflow_periods = quarterly_cashflow['end_date'].tolist()
            quarterly_cashflow_values = quarterly_cashflow['quarterly_n_cashflow_act'].tolist() if 'quarterly_n_cashflow_act' in quarterly_cashflow.columns else []
            
            html_content.append('        const quarterlyCashFlowCtx = document.getElementById("quarterlyCashFlowChart").getContext("2d");')
            html_content.append('        new Chart(quarterlyCashFlowCtx, {')
            html_content.append('            type: "bar",')
            html_content.append('            data: {')
            html_content.append('                labels: [{}],'.format(', '.join([f'"{period}"' for period in quarterly_cashflow_periods])))
            html_content.append('                datasets: [')
            if quarterly_cashflow_values:
                html_content.append('                    {')
                html_content.append('                        label: "季度经营现金流净额（亿元）",')
                html_content.append('                        data: [{}],'.format(', '.join([str(val) if pd.notna(val) else 'null' for val in quarterly_cashflow_values])))
                html_content.append('                        backgroundColor: "rgba(255, 99, 132, 0.5)",')
                html_content.append('                        borderColor: "rgba(255, 99, 132, 1)",')
                html_content.append('                        borderWidth: 1')
                html_content.append('                    }')
            html_content.append('                ]')
            html_content.append('            },')
            html_content.append('            options: {')
            html_content.append('                responsive: true,')
            html_content.append('                maintainAspectRatio: false,')
            html_content.append('                scales: {')
            html_content.append('                    y: {')
            html_content.append('                        title: {')
            html_content.append('                            display: true,')
            html_content.append('                            text: "金额（亿元）"')
            html_content.append('                        }')
            html_content.append('                    }')
            html_content.append('                },')
            html_content.append('                plugins: {')
            html_content.append('                    title: {')
            html_content.append('                        display: true,')
            html_content.append('                        text: "季度经营现金流净额"')
            html_content.append('                    }')
            html_content.append('                },')
            html_content.append('                annotation: {')
            html_content.append('                    annotations: []')
            html_content.append('                }')
            html_content.append('            }')
            html_content.append('        });')
        
        # Annual margins chart
        if not annual_indicators.empty and 'annual_netprofit_margin' in annual_indicators.columns and 'annual_grossprofit_margin' in annual_indicators.columns:
            annual_margin_periods = annual_indicators['end_date'].tolist()
            annual_netprofit_margin_values = annual_indicators['annual_netprofit_margin'].tolist()
            annual_grossprofit_margin_values = annual_indicators['annual_grossprofit_margin'].tolist()
            
            html_content.append('        const annualMarginsCtx = document.getElementById("annualMarginsChart").getContext("2d");')
            html_content.append('        new Chart(annualMarginsCtx, {')
            html_content.append('            type: "line",')
            html_content.append('            data: {')
            html_content.append('                labels: [{}],'.format(', '.join([f'"{period}"' for period in annual_margin_periods])))
            html_content.append('                datasets: [')
            html_content.append('                    {')
            html_content.append('                        label: "年度净利率(%)",')
            html_content.append('                        data: [{}],'.format(', '.join([str(val) if pd.notna(val) else 'null' for val in annual_netprofit_margin_values])))
            html_content.append('                        borderColor: "rgba(255, 99, 132, 1)",')
            html_content.append('                        backgroundColor: "rgba(255, 99, 132, 0.2)",')
            html_content.append('                        tension: 0.4,')
            html_content.append('                        fill: false,')
            html_content.append('                        datalabels: {')
            html_content.append('                            anchor: "end",')
            html_content.append('                            align: "top",')
            html_content.append('                            formatter: function(value) {')
            html_content.append('                                return value != null ? value.toFixed(1) + "%" : "";')
            html_content.append('                            },')
            html_content.append('                            color: "rgba(255, 99, 132, 1)",')
            html_content.append('                            font: {')
            html_content.append('                                size: 10,')
            html_content.append('                                weight: "normal"')
            html_content.append('                            }')
            html_content.append('                        }')
            html_content.append('                    },')
            html_content.append('                    {')
            html_content.append('                        label: "年度毛利率(%)",')
            html_content.append('                        data: [{}],'.format(', '.join([str(val) if pd.notna(val) else 'null' for val in annual_grossprofit_margin_values])))
            html_content.append('                        borderColor: "rgba(54, 162, 235, 1)",')
            html_content.append('                        backgroundColor: "rgba(54, 162, 235, 0.2)",')
            html_content.append('                        tension: 0.4,')
            html_content.append('                        fill: false,')
            html_content.append('                        datalabels: {')
            html_content.append('                            anchor: "end",')
            html_content.append('                            align: "top",')
            html_content.append('                            formatter: function(value) {')
            html_content.append('                                return value != null ? value.toFixed(1) + "%" : "";')
            html_content.append('                            },')
            html_content.append('                            color: "rgba(54, 162, 235, 1)",')
            html_content.append('                            font: {')
            html_content.append('                                size: 10,')
            html_content.append('                                weight: "normal"')
            html_content.append('                            }')
            html_content.append('                        }')
            html_content.append('                    }')
            html_content.append('                ]')
            html_content.append('            },')
            html_content.append('            options: {')
            html_content.append('                responsive: true,')
            html_content.append('                maintainAspectRatio: false,')
            html_content.append('                scales: {')
            html_content.append('                    y: {')
            html_content.append('                        title: {')
            html_content.append('                            display: true,')
            html_content.append('                            text: "数值(%)"')
            html_content.append('                        }')
            html_content.append('                    }')
            html_content.append('                },')
            html_content.append('                plugins: {')
            html_content.append('                    title: {')
            html_content.append('                        display: true,')
            html_content.append('                        text: "年度净利率和毛利率"')
            html_content.append('                    },')
            html_content.append('                    datalabels: {')
            html_content.append('                        display: true')
            html_content.append('                    }')
            html_content.append('                }')
            html_content.append('            }')
            html_content.append('        });')
        
        # Annual ROE chart
        if not annual_indicators.empty and 'annual_roe_waa' in annual_indicators.columns and 'annual_roa' in annual_indicators.columns and 'annual_roic' in annual_indicators.columns:
            annual_roe_periods = annual_indicators['end_date'].tolist()
            annual_roe_waa_values = annual_indicators['annual_roe_waa'].tolist()
            annual_roa_values = annual_indicators['annual_roa'].tolist()
            annual_roic_values = annual_indicators['annual_roic'].tolist()
            
            html_content.append('        const annualROECtx = document.getElementById("annualROEChart").getContext("2d");')
            html_content.append('        new Chart(annualROECtx, {')
            html_content.append('            type: "line",')
            html_content.append('            data: {')
            html_content.append('                labels: [{}],'.format(', '.join([f'"{period}"' for period in annual_roe_periods])))
            html_content.append('                datasets: [')
            html_content.append('                    {')
            html_content.append('                        label: "年度净资产收益率(%)",')
            html_content.append('                        data: [{}],'.format(', '.join([str(val) if pd.notna(val) else 'null' for val in annual_roe_waa_values])))
            html_content.append('                        borderColor: "rgba(75, 192, 192, 1)",')
            html_content.append('                        backgroundColor: "rgba(75, 192, 192, 0.2)",')
            html_content.append('                        tension: 0.4,')
            html_content.append('                        fill: false,')
            html_content.append('                        datalabels: {')
            html_content.append('                            anchor: "end",')
            html_content.append('                            align: "top",')
            html_content.append('                            formatter: function(value) {')
            html_content.append('                                return value != null ? value.toFixed(1) + "%" : "";')
            html_content.append('                            },')
            html_content.append('                            color: "rgba(75, 192, 192, 1)",')
            html_content.append('                            font: {')
            html_content.append('                                size: 10,')
            html_content.append('                                weight: "normal"')
            html_content.append('                            }')
            html_content.append('                        }')
            html_content.append('                    },')
            html_content.append('                    {')
            html_content.append('                        label: "年度总资产报酬率(%)",')
            html_content.append('                        data: [{}],'.format(', '.join([str(val) if pd.notna(val) else 'null' for val in annual_roa_values])))
            html_content.append('                        borderColor: "rgba(153, 102, 255, 1)",')
            html_content.append('                        backgroundColor: "rgba(153, 102, 255, 0.2)",')
            html_content.append('                        tension: 0.4,')
            html_content.append('                        fill: false,')
            html_content.append('                        datalabels: {')
            html_content.append('                            anchor: "end",')
            html_content.append('                            align: "top",')
            html_content.append('                            formatter: function(value) {')
            html_content.append('                                return value != null ? value.toFixed(1) + "%" : "";')
            html_content.append('                            },')
            html_content.append('                            color: "rgba(153, 102, 255, 1)",')
            html_content.append('                            font: {')
            html_content.append('                                size: 10,')
            html_content.append('                                weight: "normal"')
            html_content.append('                            }')
            html_content.append('                        }')
            html_content.append('                    },')
            html_content.append('                    {')
            html_content.append('                        label: "年度投入资本回报率(%)",')
            html_content.append('                        data: [{}],'.format(', '.join([str(val) if pd.notna(val) else 'null' for val in annual_roic_values])))
            html_content.append('                        borderColor: "rgba(255, 159, 64, 1)",')
            html_content.append('                        backgroundColor: "rgba(255, 159, 64, 0.2)",')
            html_content.append('                        tension: 0.4,')
            html_content.append('                        fill: false,')
            html_content.append('                        datalabels: {')
            html_content.append('                            anchor: "end",')
            html_content.append('                            align: "top",')
            html_content.append('                            formatter: function(value) {')
            html_content.append('                                return value != null ? value.toFixed(1) + "%" : "";')
            html_content.append('                            },')
            html_content.append('                            color: "rgba(255, 159, 64, 1)",')
            html_content.append('                            font: {')
            html_content.append('                                size: 10,')
            html_content.append('                                weight: "normal"')
            html_content.append('                            }')
            html_content.append('                        }')
            html_content.append('                    }')
            html_content.append('                ]')
            html_content.append('            },')
            html_content.append('            options: {')
            html_content.append('                responsive: true,')
            html_content.append('                maintainAspectRatio: false,')
            html_content.append('                scales: {')
            html_content.append('                    y: {')
            html_content.append('                        title: {')
            html_content.append('                            display: true,')
            html_content.append('                            text: "数值(%)"')
            html_content.append('                        }')
            html_content.append('                    }')
            html_content.append('                },')
            html_content.append('                plugins: {')
            html_content.append('                    title: {')
            html_content.append('                        display: true,')
            html_content.append('                        text: "年度ROE、ROA、ROIC"')
            html_content.append('                    },')
            html_content.append('                    datalabels: {')
            html_content.append('                        display: true')
            html_content.append('                    }')
            html_content.append('                }')
            html_content.append('            }')
            html_content.append('        });')
        
        
        # Quarterly margins chart
        if not quarterly_indicators.empty and 'quarterly_netprofit_margin' in quarterly_indicators.columns and 'quarterly_grossprofit_margin' in quarterly_indicators.columns:
            quarterly_margin_periods = quarterly_indicators['end_date'].tolist()
            quarterly_netprofit_margin_values = quarterly_indicators['quarterly_netprofit_margin'].tolist()
            quarterly_grossprofit_margin_values = quarterly_indicators['quarterly_grossprofit_margin'].tolist()
            
            html_content.append('        const quarterlyMarginsCtx = document.getElementById("quarterlyMarginsChart").getContext("2d");')
            html_content.append('        new Chart(quarterlyMarginsCtx, {')
            html_content.append('            type: "line",')
            html_content.append('            data: {')
            html_content.append('                labels: [{}],'.format(', '.join([f'"{period}"' for period in quarterly_margin_periods])))
            html_content.append('                datasets: [')
            html_content.append('                    {')
            html_content.append('                        label: "季度净利率(%)",')
            html_content.append('                        data: [{}],'.format(', '.join([str(val) if pd.notna(val) else 'null' for val in quarterly_netprofit_margin_values])))
            html_content.append('                        borderColor: "rgba(255, 99, 132, 1)",')
            html_content.append('                        backgroundColor: "rgba(255, 99, 132, 0.2)",')
            html_content.append('                        tension: 0.4,')
            html_content.append('                        fill: false,')
            html_content.append('                        datalabels: {')
            html_content.append('                            anchor: "end",')
            html_content.append('                            align: "top",')
            html_content.append('                            formatter: function(value) {')
            html_content.append('                                return value != null ? value.toFixed(1) + "%" : "";')
            html_content.append('                            },')
            html_content.append('                            color: "rgba(255, 99, 132, 1)",')
            html_content.append('                            font: {')
            html_content.append('                                size: 10,')
            html_content.append('                                weight: "normal"')
            html_content.append('                            }')
            html_content.append('                        }')
            html_content.append('                    },')
            html_content.append('                    {')
            html_content.append('                        label: "季度毛利率(%)",')
            html_content.append('                        data: [{}],'.format(', '.join([str(val) if pd.notna(val) else 'null' for val in quarterly_grossprofit_margin_values])))
            html_content.append('                        borderColor: "rgba(54, 162, 235, 1)",')
            html_content.append('                        backgroundColor: "rgba(54, 162, 235, 0.2)",')
            html_content.append('                        tension: 0.4,')
            html_content.append('                        fill: false,')
            html_content.append('                        datalabels: {')
            html_content.append('                            anchor: "end",')
            html_content.append('                            align: "top",')
            html_content.append('                            formatter: function(value) {')
            html_content.append('                                return value != null ? value.toFixed(1) + "%" : "";')
            html_content.append('                            },')
            html_content.append('                            color: "rgba(54, 162, 235, 1)",')
            html_content.append('                            font: {')
            html_content.append('                                size: 10,')
            html_content.append('                                weight: "normal"')
            html_content.append('                            }')
            html_content.append('                        }')
            html_content.append('                    }')
            html_content.append('                ]')
            html_content.append('            },')
            html_content.append('            options: {')
            html_content.append('                responsive: true,')
            html_content.append('                maintainAspectRatio: false,')
            html_content.append('                scales: {')
            html_content.append('                    y: {')
            html_content.append('                        title: {')
            html_content.append('                            display: true,')
            html_content.append('                            text: "数值(%)"')
            html_content.append('                        }')
            html_content.append('                    }')
            html_content.append('                },')
            html_content.append('                plugins: {')
            html_content.append('                    title: {')
            html_content.append('                        display: true,')
            html_content.append('                        text: "季度净利率和毛利率"')
            html_content.append('                    },')
            html_content.append('                    datalabels: {')
            html_content.append('                        display: true')
            html_content.append('                    }')
            html_content.append('                }')
            html_content.append('            }')
            html_content.append('        });')
        
        
        
        html_content.append('    </script>')
        
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