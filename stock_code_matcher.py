import pandas as pd
import tkinter as tk
from tkinter import messagebox
import os


class StockCodeMatcher:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.stock_data = None
        self.load_stock_data()

    def load_stock_data(self):
        """加载股票代码映射表"""
        try:
            # 用UTF-8编码读取CSV文件
            self.stock_data = pd.read_csv(self.csv_file_path, encoding='utf-8')
            print("成功加载股票数据")
        except Exception as e:
            print(f"加载股票数据失败: {e}")
            raise

    def find_stock_code(self, company_name):
        """根据公司名称查找股票代码"""
        # 在证券名称列中查找匹配项（不区分大小写）
        matching_rows = self.stock_data[
            self.stock_data['证券名称'].str.contains(company_name, case=False, na=False)
        ]
        if not matching_rows.empty:
            # 返回第一个匹配的股票代码
            return matching_rows.iloc[0]['证券代码']
        return None

    def show_input_window(self):
        """显示输入窗口，实现您要求的功能"""
        def search_stock():
            company_name = entry.get().strip()
            if not company_name:
                messagebox.showwarning("警告", "请输入公司名称")
                return
            
            stock_code = self.find_stock_code(company_name)
            if stock_code:
                result_label.config(text=f"找到股票代码: {stock_code}")
                messagebox.showinfo("成功", f"公司: {company_name}\n股票代码: {stock_code}")
            else:
                result_label.config(text="未找到该公司，请检查名称是否正确")
                messagebox.showerror("错误", "未找到该公司，请检查名称是否正确")
                
                # 清空输入框并重新聚焦，让用户重新输入
                entry.delete(0, tk.END)
                entry.focus()
        
        # 创建GUI窗口
        root = tk.Tk()
        root.title("上市公司基本信息查询工具 - 股票代码匹配")
        root.geometry("400x200")
        
        # 标签 - 提示用户输入
        label = tk.Label(root, text="请输入要查询的公司名称：", font=("Arial", 12))
        label.pack(pady=20)
        
        # 输入框
        entry = tk.Entry(root, font=("Arial", 12), width=30)
        entry.pack(pady=10)
        entry.focus()  # 设置焦点
        
        # 查询按钮
        button = tk.Button(root, text="查询", command=search_stock, font=("Arial", 12))
        button.pack(pady=10)
        
        # 结果显示标签
        result_label = tk.Label(root, text="", font=("Arial", 12))
        result_label.pack(pady=10)
        
        # 运行主循环
        root.mainloop()


def main():
    # 获取当前工作目录下的stock_names.csv文件
    csv_file_path = os.path.join(os.getcwd(), 'stock_names.csv')
    
    if not os.path.exists(csv_file_path):
        print(f"错误: 找不到文件 {csv_file_path}")
        return
    
    try:
        matcher = StockCodeMatcher(csv_file_path)
        matcher.show_input_window()
    except Exception as e:
        print(f"程序运行出错: {e}")


if __name__ == "__main__":
    main()