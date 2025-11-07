import tushare as ts
import pandas as pd
import datetime
import os


class DataExtractor:
    def __init__(self):
        # 从环境变量获取tushare token
        token = os.environ.get('TUSHARE_TOKEN')
        if not token:
            raise ValueError("TUSHARE_TOKEN环境变量未设置")
        
        ts.set_token(token)
        self.pro = ts.pro_api()
        
        # 计算时间范围
        self.current_date = datetime.datetime.now()
        self.five_years_ago = self.current_date - datetime.timedelta(days=5*365)
        self.ten_quarters_ago = self.current_date - datetime.timedelta(days=10*91)  # 10个季度大约是10*91天
        
        # 格式化日期字符串
        self.five_years_ago_str = self.five_years_ago.strftime('%Y%m%d')
        self.ten_quarters_ago_str = self.ten_quarters_ago.strftime('%Y%m%d')
        self.current_date_str = self.current_date.strftime('%Y%m%d')
        
        print(f"当前日期: {self.current_date_str}")
        print(f"过去五年起始日期: {self.five_years_ago_str}")
        print(f"过去十个季度起始日期: {self.ten_quarters_ago_str}")

    def extract_income_data(self, stock_code):
        """提取利润表数据"""
        # 1. 获取过去五年的年度数据
        annual_income = self.pro.income(ts_code=stock_code, 
                                      start_date=self.five_years_ago_str, 
                                      end_date=self.current_date_str)
        
        # 只保留年度数据（end_type='4' 表示年报，注意是字符串类型）
        annual_income = annual_income[annual_income['end_type'] == '4']
        
        # 筛选最新更新的数据（update_flag=1表示最新数据）
        if 'update_flag' in annual_income.columns:
            annual_income = annual_income[annual_income['update_flag'] == '1']
        #将数据升序排列
        annual_income = annual_income.sort_values(by='end_date', ascending=True).reset_index(drop=True)
        # 提取过去五年的营业收入和归母净利润
        annual_revenue = annual_income[['end_date', 'total_revenue']].rename(columns={'total_revenue': 'annual_total_revenue'})
        annual_net_profit = annual_income[['end_date', 'n_income_attr_p']].rename(columns={'n_income_attr_p': 'annual_n_income_attr_p'})
        
        # 转换为亿元，并保留一位小数
        annual_revenue['annual_total_revenue'] = pd.to_numeric(annual_revenue['annual_total_revenue'], errors='coerce') / 100000000
        annual_revenue['annual_total_revenue'] = annual_revenue['annual_total_revenue'].round(1)
        annual_net_profit['annual_n_income_attr_p'] = pd.to_numeric(annual_net_profit['annual_n_income_attr_p'], errors='coerce') / 100000000
        annual_net_profit['annual_n_income_attr_p'] = annual_net_profit['annual_n_income_attr_p'].round(1)
        
        # 2. 获取过去十个季度的数据 (report_type=2)
        quarterly_income = self.pro.income(ts_code=stock_code, 
                                         start_date=self.ten_quarters_ago_str, 
                                         end_date=self.current_date_str, 
                                         report_type=2)
        # 筛选最新更新的数据（update_flag=1表示最新数据）季度数据update_flag规则还不清楚
        #if 'update_flag' in quarterly_income.columns:
        #    quarterly_income = quarterly_income[quarterly_income['update_flag'] == '1']
        
        #将数据升序排列
        quarterly_income = quarterly_income.sort_values(by='end_date', ascending=True).reset_index(drop=True)

        # 提取过去十个季度的营业收入和归母净利润
        quarterly_revenue = quarterly_income[['end_date', 'total_revenue']].rename(columns={'total_revenue': 'quarterly_total_revenue'})
        quarterly_net_profit = quarterly_income[['end_date', 'n_income_attr_p']].rename(columns={'n_income_attr_p': 'quarterly_n_income_attr_p'})
        
        # 转换为亿元，并保留一位小数
        quarterly_revenue['quarterly_total_revenue'] = pd.to_numeric(quarterly_revenue['quarterly_total_revenue'], errors='coerce') / 100000000
        quarterly_revenue['quarterly_total_revenue'] = quarterly_revenue['quarterly_total_revenue'].round(1)
        quarterly_net_profit['quarterly_n_income_attr_p'] = pd.to_numeric(quarterly_net_profit['quarterly_n_income_attr_p'], errors='coerce') / 100000000
        quarterly_net_profit['quarterly_n_income_attr_p'] = quarterly_net_profit['quarterly_n_income_attr_p'].round(1)
        
        print("提取利润表数据完成")
        return {
            'annual_revenue': annual_revenue,
            'annual_net_profit': annual_net_profit,
            'quarterly_revenue': quarterly_revenue,
            'quarterly_net_profit': quarterly_net_profit
        }

    def extract_cashflow_data(self, stock_code):
        """提取现金流量表数据"""
        # 3. 获取过去五年的年度现金流量数据
        annual_cashflow = self.pro.cashflow(ts_code=stock_code, 
                                          start_date=self.five_years_ago_str, 
                                          end_date=self.current_date_str)
        
        # 只保留年度数据（end_type='4' 表示年报，注意是字符串类型）
        annual_cashflow = annual_cashflow[annual_cashflow['end_type'] == '4']
        
        # 筛选最新更新的数据（update_flag=1表示最新数据）
        if 'update_flag' in annual_cashflow.columns:
            annual_cashflow = annual_cashflow[annual_cashflow['update_flag'] == '1']
        #将数据升序排列
        annual_cashflow = annual_cashflow.sort_values(by='end_date', ascending=True).reset_index(drop=True)

        # 提取过去五年的经营现金流净额和现金净增加额
        # 检查数据是否存在必要的列
        required_cols = ['n_cashflow_act', 'im_n_incr_cash_equ']
        available_cols = ['end_date'] + [col for col in required_cols if col in annual_cashflow.columns]
        annual_cashflow_data = annual_cashflow[available_cols].copy()
        
        rename_dict = {'n_cashflow_act': 'annual_n_cashflow_act'}
        if 'im_n_incr_cash_equ' in annual_cashflow_data.columns:
            rename_dict['im_n_incr_cash_equ'] = 'annual_im_n_incr_cash_equ'
            
        annual_cashflow_data = annual_cashflow_data.rename(columns=rename_dict)
        
        # 转换为亿元，并保留一位小数
        if 'annual_n_cashflow_act' in annual_cashflow_data.columns:
            annual_cashflow_data['annual_n_cashflow_act'] = pd.to_numeric(annual_cashflow_data['annual_n_cashflow_act'], errors='coerce') / 100000000
            annual_cashflow_data['annual_n_cashflow_act'] = annual_cashflow_data['annual_n_cashflow_act'].round(1)
            
        if 'annual_im_n_incr_cash_equ' in annual_cashflow_data.columns:
            annual_cashflow_data['annual_im_n_incr_cash_equ'] = pd.to_numeric(annual_cashflow_data['annual_im_n_incr_cash_equ'], errors='coerce') / 100000000
            annual_cashflow_data['annual_im_n_incr_cash_equ'] = annual_cashflow_data['annual_im_n_incr_cash_equ'].round(1)
        
        # 4. 获取过去十个季度的现金流量数据 (report_type=2)
        quarterly_cashflow = self.pro.cashflow(ts_code=stock_code, 
                                             start_date=self.ten_quarters_ago_str, 
                                             end_date=self.current_date_str, 
                                             report_type=2)
        
        # 筛选最新更新的数据（update_flag=1表示最新数据）季度数据update_flag规则还不清楚
        #if 'update_flag' in quarterly_cashflow.columns:
        #    quarterly_cashflow = quarterly_cashflow[quarterly_cashflow['update_flag'] == '1']
        #将数据升序排列
        quarterly_cashflow = quarterly_cashflow.sort_values(by='end_date', ascending=True).reset_index(drop=True)

        # 提取过去十个季度的经营现金流净额（不再提取现金净增加额）
        # 首先检查数据是否存在必要的列
        if 'n_cashflow_act' not in quarterly_cashflow.columns:
            print(f"警告: 股票{stock_code}的季度现金流量表中缺少n_cashflow_act列")
            quarterly_cashflow_data = pd.DataFrame(columns=['end_date', 'quarterly_n_cashflow_act'])
        else:
            # 仅提取存在的列
            cols_to_extract = ['end_date', 'n_cashflow_act']
            available_cols = [col for col in cols_to_extract if col in quarterly_cashflow.columns]
            quarterly_cashflow_data = quarterly_cashflow[available_cols].copy()
            quarterly_cashflow_data = quarterly_cashflow_data.rename(columns={
                'n_cashflow_act': 'quarterly_n_cashflow_act'
            })
            
            # 转换为亿元，并保留一位小数
            quarterly_cashflow_data['quarterly_n_cashflow_act'] = pd.to_numeric(quarterly_cashflow_data['quarterly_n_cashflow_act'], errors='coerce') / 100000000
            quarterly_cashflow_data['quarterly_n_cashflow_act'] = quarterly_cashflow_data['quarterly_n_cashflow_act'].round(1)
        
        print("提取现金流量表数据完成")
        return {
            'annual_cashflow': annual_cashflow_data,
            'quarterly_cashflow': quarterly_cashflow_data
        }

    def extract_financial_indicators(self, stock_code):
        """提取财务指标数据"""
        # 5. 获取过去五年的年度财务指标
        # 使用fields参数指定需要的字段
        annual_fields = [
            'end_date', 
            'netprofit_margin',      # 净利率
            'grossprofit_margin',    # 毛利率
            'roe_waa',              # 净资产收益率
            'roa',                  # 总资产报酬率
            'roic',                 # 投入资本回报率
            'tr_yoy',               # 营收增长率
            'netprofit_yoy',         # 利润增长率
            'update_flag'            # 更新标志
        ]
        annual_indicators = self.pro.fina_indicator(
            ts_code=stock_code, 
            start_date=self.five_years_ago_str, 
            end_date=self.current_date_str,
            fields=','.join(annual_fields)
        )
        
        # 筛选年度报告（end_date以1231结尾，即每年12月31日）
        annual_indicators = annual_indicators[annual_indicators['end_date'].str.endswith('1231')]
        
        # 筛选最新更新的数据（update_flag=1表示最新数据）
        if 'update_flag' in annual_indicators.columns:
            annual_indicators = annual_indicators[annual_indicators['update_flag'] == '1']
        #将数据升序排列
        annual_indicators = annual_indicators.sort_values(by='end_date', ascending=True).reset_index(drop=True)
        # Remove update_flag column from the final result since we only used it for filtering
        annual_indicators_for_rename = annual_indicators.drop(columns=['update_flag']) if 'update_flag' in annual_indicators.columns else annual_indicators
        annual_indicators_data = annual_indicators_for_rename.rename(columns={
            'netprofit_margin': 'annual_netprofit_margin',
            'grossprofit_margin': 'annual_grossprofit_margin',
            'roe_waa': 'annual_roe_waa',
            'roa': 'annual_roa',
            'roic': 'annual_roic',
            'tr_yoy': 'annual_tr_yoy',
            'netprofit_yoy': 'annual_netprofit_yoy'
        })
        
        # 将比率类数据转换为百分比格式，并保留一位小数
        ratio_columns = [
            'annual_netprofit_margin', 'annual_grossprofit_margin', 
            'annual_roe_waa', 'annual_roa', 'annual_roic', 
            'annual_tr_yoy', 'annual_netprofit_yoy'
        ]
        for col in ratio_columns:
            if col in annual_indicators_data.columns:
                annual_indicators_data[col] = pd.to_numeric(annual_indicators_data[col], errors='coerce').round(1)  # 保留一位小数

        # 6. 获取过去十个季度的财务指标
        # 使用fields参数指定需要的字段，根据您提供的正确字段名
        quarterly_fields = [
            'end_date', 
            'q_netprofit_margin',   # 单季度销售净利率
            'q_gsprofit_margin',    # 单季度销售毛利率
            'q_gr_yoy',             # 营收同比增长率
            'q_gr_qoq',             # 营收环比增长率
            'q_netprofit_yoy',      # 利润同比增长率
            'q_netprofit_qoq',      # 利润环比增长率
            'update_flag'           # 更新标志
        ]
        quarterly_indicators = self.pro.fina_indicator(
            ts_code=stock_code, 
            start_date=self.ten_quarters_ago_str, 
            end_date=self.current_date_str,
            fields=','.join(quarterly_fields)
        )
        
        # 筛选最新更新的数据（update_flag=1表示最新数据） 季度财报指标中update_flag规则还不清楚
        if 'update_flag' in quarterly_indicators.columns:
            quarterly_indicators = quarterly_indicators[quarterly_indicators['update_flag'] == '1']
        #将数据升序排列
        quarterly_indicators = quarterly_indicators.sort_values(by='end_date', ascending=True).reset_index(drop=True)
        # Remove update_flag column from the final result since we only used it for filtering
        quarterly_indicators_for_rename = quarterly_indicators.drop(columns=['update_flag']) if 'update_flag' in quarterly_indicators.columns else quarterly_indicators
        quarterly_indicators_data = quarterly_indicators_for_rename.rename(columns={
            'q_netprofit_margin': 'quarterly_netprofit_margin',  # 单季度销售净利率
            'q_gsprofit_margin': 'quarterly_grossprofit_margin', # 单季度销售毛利率
            'q_gr_yoy': 'quarterly_gr_yoy',                      # 营收同比增长率
            'q_gr_qoq': 'quarterly_gr_qoq',                      # 营收环比增长率
            'q_netprofit_yoy': 'quarterly_profit_yoy',           # 利润同比增长率
            'q_netprofit_qoq': 'quarterly_profit_qoq'            # 利润环比增长率
        })
        
        # 将比率类数据转换为百分比格式，并保留一位小数
        quarterly_ratio_columns = [
            'quarterly_netprofit_margin', 'quarterly_grossprofit_margin',
            'quarterly_gr_yoy', 'quarterly_gr_qoq',
            'quarterly_profit_yoy', 'quarterly_profit_qoq'
        ]
        for col in quarterly_ratio_columns:
            if col in quarterly_indicators_data.columns:
                quarterly_indicators_data[col] = pd.to_numeric(quarterly_indicators_data[col], errors='coerce').round(1)  # 保留1位小数

        print("提取财务指标数据完成")
        return {
            'annual_indicators': annual_indicators_data,
            'quarterly_indicators': quarterly_indicators_data
        }

    def extract_main_business_composition(self, stock_code, annual_revenue=None):
        """提取主营业务构成数据"""
        # 通过fina_mainbz接口获取数据，type选择P
        main_bz_data = self.pro.fina_mainbz(ts_code=stock_code, type='P')
        # 只保留最近五年的数据，删除多余的数据（如果提取的数据不足5年则全部保留）
        if 'end_date' in main_bz_data.columns:
            # Extract the year from end_date and get the 5 most recent years
            main_bz_data['year'] = main_bz_data['end_date'].astype(str).str[:4].astype(int)
            recent_years = sorted(main_bz_data['year'].unique(), reverse=True)[:5]  # Get the 5 most recent years
            main_bz_data = main_bz_data[main_bz_data['year'].isin(recent_years)]
            # Drop the temporary year column
            main_bz_data = main_bz_data.drop(columns=['year'])
        
        # 增加筛选：只保留年度数据或最新数据
        # 1）end_date最后四位以1231结尾，或
        # 2）开头四位与今年的年份相等
        current_year = self.current_date.year
        if 'end_date' in main_bz_data.columns:
            # Condition 1: end_date ends with '1231' (annual data)
            annual_condition = main_bz_data['end_date'].astype(str).str.endswith('1231')
            # Condition 2: year matches current year
            current_year_condition = main_bz_data['end_date'].astype(str).str[:4].astype(int) == current_year
            # Keep records that satisfy either condition
            main_bz_data = main_bz_data[annual_condition | current_year_condition]
        #去掉重复记录
        main_bz_data = main_bz_data.drop_duplicates(subset=['end_date', 'bz_item'])
        #按收入规模降序排列
        main_bz_data = main_bz_data.sort_values(by=['end_date', 'bz_sales'], ascending=[False, False])
        #删去bz_cost、bz_code、curr_type这三列
        main_bz_data = main_bz_data.drop(columns=['bz_cost', 'bz_code', 'curr_type'], errors='ignore')
        
        # 1）通过Tushare的income接口提取报告期和总收入的数据（total_revenue），假如命名为income_data
        income_data = self.pro.income(ts_code=stock_code, 
                                     start_date=self.five_years_ago_str, 
                                     end_date=self.current_date_str,
                                     fields='end_date,total_revenue')
        
        # 筛选最新更新的数据（update_flag=1表示最新数据）
        if 'update_flag' in income_data.columns:
            income_data = income_data[income_data['update_flag'] == '1']
        
        # Convert total_revenue to billions and round to 1 decimal place
        income_data['total_revenue'] = pd.to_numeric(income_data['total_revenue'], errors='coerce') / 100000000
        income_data['total_revenue'] = income_data['total_revenue'].round(1)
        
        # 计算毛利率 (bz_profit/bz_sales)
        if 'bz_profit' in main_bz_data.columns and 'bz_sales' in main_bz_data.columns:
            # Convert to numeric and handle potential division by zero
            main_bz_data['bz_profit'] = pd.to_numeric(main_bz_data['bz_profit'], errors='coerce')
            main_bz_data['bz_sales'] = pd.to_numeric(main_bz_data['bz_sales'], errors='coerce')
            
            # Calculate gross margin percentage before converting to billions
            main_bz_data['gross_margin'] = (main_bz_data['bz_profit'] / main_bz_data['bz_sales']) * 100
            # Replace infinity values with NaN for division by zero
            main_bz_data['gross_margin'] = main_bz_data['gross_margin'].replace([float('inf'), float('-inf')], pd.NA)
        
        # 将单位修改为亿元，保留一位小数 (before calculating revenue proportion)
        if 'bz_sales' in main_bz_data.columns:
            main_bz_data['bz_sales'] = pd.to_numeric(main_bz_data['bz_sales'], errors='coerce') / 100000000
            main_bz_data['bz_sales'] = main_bz_data['bz_sales'].round(1)
        
        if 'bz_profit' in main_bz_data.columns:
            main_bz_data['bz_profit'] = pd.to_numeric(main_bz_data['bz_profit'], errors='coerce') / 100000000
            main_bz_data['bz_profit'] = main_bz_data['bz_profit'].round(1)
        
        # 为了确保没有重复数据，在merge前也对income_data进行去重（按end_date去重，取第一条）
        if 'total_revenue' in income_data.columns:
            # 对income_data按end_date去重，保留第一条记录
            income_data = income_data.drop_duplicates(subset=['end_date'], keep='first')
            
            # Rename total_revenue column to avoid confusion
            income_data_renamed = income_data.rename(columns={'total_revenue': 'total_income'})
            main_bz_data = main_bz_data.merge(income_data_renamed[['end_date', 'total_income']], on='end_date', how='left')
            
            # 3) 用bz_sales/total_income得到收入占比
            if 'bz_sales' in main_bz_data.columns and 'total_income' in main_bz_data.columns:
                main_bz_data['revenue_proportion'] = (main_bz_data['bz_sales'] / main_bz_data['total_income']) * 100
                # Replace infinity values with NaN for division by zero
                main_bz_data['revenue_proportion'] = main_bz_data['revenue_proportion'].replace([float('inf'), float('-inf')], pd.NA)
            
            # 4) 将并进来的total_income列删除
            main_bz_data = main_bz_data.drop(columns=['total_income'])
        
        # 毛利率和收入占比改为百分比的表示格式，保留一位小数
        if 'gross_margin' in main_bz_data.columns:
            main_bz_data['gross_margin'] = pd.to_numeric(main_bz_data['gross_margin'], errors='coerce')
            main_bz_data['gross_margin'] = main_bz_data['gross_margin'].round(1)
        
        if 'revenue_proportion' in main_bz_data.columns:
            main_bz_data['revenue_proportion'] = pd.to_numeric(main_bz_data['revenue_proportion'], errors='coerce')
            main_bz_data['revenue_proportion'] = main_bz_data['revenue_proportion'].round(1)
        
        # 在所有处理完成后，再次执行去重操作，以确保没有重复记录
        main_bz_data = main_bz_data.drop_duplicates(subset=['end_date', 'bz_item'])
        
        print(f"提取主营业务构成数据完成，共{len(main_bz_data)}条记录")
        return main_bz_data

    def get_all_data(self, stock_code):
        """获取所有需要的数据"""
        print(f"开始提取股票 {stock_code} 的数据...")
        
        # 提取各类数据
        income_data = self.extract_income_data(stock_code)
        cashflow_data = self.extract_cashflow_data(stock_code)
        fina_data = self.extract_financial_indicators(stock_code)
        
        # 合并所有数据
        all_data = {}
        all_data.update(income_data)
        all_data.update(cashflow_data)
        all_data.update(fina_data)
        
        # 打印变量（仅用于测试）
        print("\n--- 年度利润表数据 ---")
        print("年度营业收入:")
        print(income_data['annual_revenue'])
        print("年度归母净利润:")
        print(income_data['annual_net_profit'])
        
        print("\n--- 季度利润表数据 ---")
        print("季度营业收入:")
        print(income_data['quarterly_revenue'])
        print("季度归母净利润:")
        print(income_data['quarterly_net_profit'])
        
        print("\n--- 年度现金流量表数据 ---")
        print("年度经营现金流净额:")
        print(cashflow_data['annual_cashflow'][['end_date', 'annual_n_cashflow_act']])
        print("年度现金净增加额:")
        print(cashflow_data['annual_cashflow'][['end_date', 'annual_im_n_incr_cash_equ']])
        
        print("\n--- 季度现金流量表数据 ---")
        print("季度经营现金流净额:")
        print(cashflow_data['quarterly_cashflow'][['end_date', 'quarterly_n_cashflow_act']])
        
        print("\n--- 年度财务指标数据 ---")
        print("年度财务指标:")
        print(fina_data['annual_indicators'])
        
        print("\n--- 季度财务指标数据 ---")
        print("季度财务指标:")
        print(fina_data['quarterly_indicators'])
        
        # Extract main business composition data
        main_bz_data = self.extract_main_business_composition(stock_code, income_data['annual_revenue'])
        all_data['main_business_composition'] = main_bz_data
        
        print("\n--- 主营业务构成数据 ---")
        print("主营业务构成:")
        print(main_bz_data)
        
        # Extract company information
        company_info = self.extract_company_information(stock_code)
        all_data['company_info'] = company_info
        
        print("\n--- 公司信息 ---")
        print(f"所在城市: {company_info['city']}")
        print(f"公司介绍: {company_info['introduction']}")
        print(f"公司主页: {company_info['website']}")
        print(f"主要业务和产品: {company_info['main_business']}")
        
        # Extract daily market data
        daily_data = self.extract_daily_market_data(stock_code)
        all_data['daily_market_data'] = daily_data
        
        print("\n--- 当日市场数据 ---")
        print(f"市盈率(TTM): {daily_data['pe_ttm']}")
        print(f"市净率: {daily_data['pb']}")
        print(f"总市值(亿元): {daily_data['total_mv']}")
        
        # Extract management information
        management_info = self.extract_management_information(stock_code)
        all_data['management_info'] = management_info
        
        print("\n--- 管理层信息 ---")
        print(f"管理层信息: {management_info}")
        
        print("\n数据提取完成！")
        return all_data

    def extract_company_information(self, stock_code):
        """提取公司信息"""
        # 使用stock_company接口获取公司信息
        company_info = self.pro.stock_company(ts_code=stock_code)
        
        if company_info.empty:
            print(f"警告: 未找到股票 {stock_code} 的公司信息")
            return {
                'city': None,
                'introduction': None,
                'website': None,
                'main_business': None
            }
        
        # 取第一条记录（如果有多条记录的话）
        company_row = company_info.iloc[0]
        
        # 提取所需字段并以合适的变量名保存
        company_data = {
            'city': company_row.get('city', None),  # 公司所在城市
            'introduction': company_row.get('introduction', None),  # 公司介绍
            'website': company_row.get('website', None),  # 公司主页
            'main_business': company_row.get('main_business', None)  # 主要业务和产品
        }
        
        print("提取公司信息完成")
        return company_data

    def extract_management_information(self, stock_code):
        """提取管理层信息"""
        try:
            # 使用stk_managers接口获取管理层信息，通过fields参数控制输出字段
            fields = ['name', 'gender', 'lev', 'title', 'edu', 'national', 'birthday', 'begin_date', 'end_date', 'resume']
            management_data = self.pro.stk_managers(ts_code=stock_code, fields=','.join(fields))
            #去掉重复项，姓名职务简历全部一样的删去
            management_data = management_data.drop_duplicates(subset=['name', 'title', 'resume'])
            if management_data.empty:
                print(f"警告: 未找到股票 {stock_code} 的管理层信息")
                return None
            
            print("提取管理层信息完成")
            # 直接返回原始的DataFrame，包含所有管理层信息
            return management_data
        except Exception as e:
            print(f"提取管理层信息时发生错误: {e}")
            return None

    def extract_daily_market_data(self, stock_code):
        """提取当日市场数据"""
        from datetime import datetime, timedelta
        
        # 从当前日期开始尝试提取数据
        current_date = datetime.strptime(self.current_date_str, '%Y%m%d')
        
        # 尝试最多向前查找30天的数据
        for i in range(31):  # 包含当天，所以是31天
            current_trade_date = current_date - timedelta(days=i)
            current_trade_date_str = current_trade_date.strftime('%Y%m%d')
            
            # 使用daily_basic接口获取指定日期的市场数据
            daily_data = self.pro.daily_basic(ts_code=stock_code, trade_date=current_trade_date_str)
            
            if not daily_data.empty:
                print(f"成功提取股票 {stock_code} 在 {current_trade_date_str} 的市场数据")
                
                # 取第一条记录
                daily_row = daily_data.iloc[0]
                
                # 提取所需字段并以合适的变量名保存
                market_data = {
                    'pe_ttm': pd.to_numeric(daily_row.get('pe_ttm', None), errors='coerce'),  # 市盈率(TTM)
                    'pb': pd.to_numeric(daily_row.get('pb', None), errors='coerce'),  # 市净率
                    'total_mv': pd.to_numeric(daily_row.get('total_mv', None), errors='coerce'),  # 总市值(元)
                    'trade_date': current_trade_date_str  # 添加实际提取数据的日期
                }
                
                # 将总市值转换为亿元单位，并保留一位小数
                if market_data['total_mv'] is not None:
                    market_data['total_mv'] = round(market_data['total_mv'] / 10000, 1)  # 万元转亿元
                
                print(f"数据提取自日期: {current_trade_date_str}")
                return market_data
        
        # 如果30天内都没有数据，返回空值
        print(f"警告: 在过去30天内未找到股票 {stock_code} 的市场数据")
        return {
            'pe_ttm': None,
            'pb': None,
            'total_mv': None,
            'trade_date': None
        }


def main():
    # 这是一个示例，实际使用时需要传入正确的股票代码
    try:
        extractor = DataExtractor()
        
        # 示例股票代码，实际使用时应该从stock_code_matcher获取
        # 这里使用一个示例代码进行测试
        sample_stock_code = "600376.SH"  # 首开股份
        all_data = extractor.get_all_data(sample_stock_code)
        
        # Print sample of new data to confirm functionality
        print("\n=== 新增功能测试结果 ===")
        print("公司信息:")
        print(f"  - 城市: {all_data['company_info']['city']}")
        print(f"  - 介绍: {all_data['company_info']['introduction']}")
        print(f"  - 网站: {all_data['company_info']['website']}")
        print(f"  - 主营业务: {all_data['company_info']['main_business']}")
        
        print("\n当日市场数据:")
        print(f"  - 市盈率(TTM): {all_data['daily_market_data']['pe_ttm'],1}")
        print(f"  - 市净率: {all_data['daily_market_data']['pb']}")
        print(f"  - 总市值(亿元): {all_data['daily_market_data']['total_mv']}")
        
    except Exception as e:
        print(f"数据提取失败: {e}")
        print("请确保已正确设置TUSHARE_TOKEN环境变量，且token有效")


if __name__ == "__main__":
    main()