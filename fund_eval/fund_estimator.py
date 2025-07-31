"""
基金净值估算数据更新工具
用于获取基金的实时估算净值并更新基金信息文件
"""

import pandas as pd
import akshare as ak
import time
from datetime import datetime
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from dotenv import load_dotenv

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 加载环境变量
load_dotenv()  # 从 .env 文件加载环境变量

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(current_dir, 'fund_estimator.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FundEstimator:
    def __init__(self, fund_info_path, output_path):
        """
        初始化基金估算器
        
        Args:
            fund_info_path (str): 基金信息文件路径
            output_path (str): 输出文件路径
        """
        self.fund_info_path = fund_info_path
        self.output_path = output_path
        # 邮件配置
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
        self.sender_password = os.getenv("SENDER_PASSWORD", "your_password")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL", "recipient@example.com")
        
    def load_fund_data(self):
        """加载基金信息数据"""
        try:
            fund_df = pd.read_csv(self.fund_info_path, dtype={'基金代码': str})
            logger.info(f"成功加载基金信息文件，共 {len(fund_df)} 只基金")
            return fund_df
        except Exception as e:
            logger.error(f"加载基金信息文件失败: {e}")
            raise
            
    def get_fund_estimation_data(self):
        """获取基金净值估算数据"""
        max_retries = 3
        retry_interval = 5
        
        for attempt in range(max_retries):
            try:
                logger.info(f"正在获取基金净值估算数据... (尝试 {attempt + 1}/{max_retries})")
                fund_estimation_df = ak.fund_value_estimation_em(symbol="全部")
                fund_estimation_df['基金代码'] = fund_estimation_df['基金代码'].astype(str)
                logger.info(f"成功获取基金估算数据，共 {len(fund_estimation_df)} 条记录")
                return fund_estimation_df
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"获取基金估算数据失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                    logger.info(f"等待 {retry_interval} 秒后重试...")
                    time.sleep(retry_interval)
                else:
                    logger.error(f"获取基金估算数据失败，已达到最大重试次数: {e}")
                    raise

    def get_fund_historical_growth_data(self):
        """获取基金历史增长率数据"""
        max_retries = 3
        retry_interval = 5
        
        for attempt in range(max_retries):
            try:
                logger.info(f"正在获取基金历史增长率数据... (尝试 {attempt + 1}/{max_retries})")
                fund_rank_df = ak.fund_open_fund_rank_em(symbol="全部")
                fund_rank_df['基金代码'] = fund_rank_df['基金代码'].astype(str)
                logger.info(f"成功获取基金历史增长率数据，共 {len(fund_rank_df)} 条记录")
                return fund_rank_df
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"获取基金历史增长率数据失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                    logger.info(f"等待 {retry_interval} 秒后重试...")
                    time.sleep(retry_interval)
                else:
                    logger.error(f"获取基金历史增长率数据失败，已达到最大重试次数: {e}")
                    raise

    def get_fund_achievement_data(self, fund_codes):
        """获取基金业绩数据（雪球接口）
        
        Args:
            fund_codes (list): 基金代码列表
            
        Returns:
            dict: 基金代码到最大回撤数据的映射
        """
        max_retries = 3
        retry_interval = 5
        result = {}
        
        # 定义需要保留的周期
        target_periods = ['成立以来', '今年以来', '近1月', '近3月', '近6月', '近1年', '近3年', '近5年']
        
        for fund_code in fund_codes:
            for attempt in range(max_retries):
                try:
                    logger.info(f"正在获取基金 {fund_code} 的业绩数据... (尝试 {attempt + 1}/{max_retries})")
                    fund_achievement_df = ak.fund_individual_achievement_xq(symbol=fund_code)
                    
                    # 只保留指定周期的数据，并提取最大回撤
                    filtered_data = fund_achievement_df[
                        (fund_achievement_df['周期'].isin(target_periods)) & 
                        (fund_achievement_df['本产品最大回撒'].notna())
                    ][['周期', '本产品最大回撒']].copy()
                    
                    # 转换为字典格式方便后续处理
                    result[fund_code] = {}
                    for _, row in filtered_data.iterrows():
                        result[fund_code][row['周期']] = row['本产品最大回撒']
                    
                    logger.info(f"成功获取基金 {fund_code} 的业绩数据")
                    break  # 成功获取后跳出重试循环
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"获取基金 {fund_code} 业绩数据失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                        logger.info(f"等待 {retry_interval} 秒后重试...")
                        time.sleep(retry_interval)
                    else:
                        logger.error(f"获取基金 {fund_code} 业绩数据失败，已达到最大重试次数: {e}")
                        result[fund_code] = {}  # 添加空字典避免后续处理出错
                        
        return result

    def get_column_names(self, fund_estimation_df):
        """
        获取估算数据的列名
        
        Args:
            fund_estimation_df (pd.DataFrame): 基金估算数据
            
        Returns:
            dict: 包含各列名的字典
        """
        actual_columns = fund_estimation_df.columns.tolist() if fund_estimation_df is not None else []
        
        # 获取估算数据列名
        est_value_col = next((col for col in actual_columns if '估算数据-估算值' in col), None)
        est_growth_col = next((col for col in actual_columns if '估算数据-估算增长率' in col), None)
        pub_value_col = next((col for col in actual_columns if '公布数据-单位净值' in col), None)
        pub_growth_col = next((col for col in actual_columns if '公布数据-日增长率' in col), None)
        
        columns = {
            'est_value': est_value_col,
            'est_growth': est_growth_col,
            'pub_value': pub_value_col,
            'pub_growth': pub_growth_col
        }
        
        logger.info("使用的列名:")
        for key, value in columns.items():
            logger.info(f"{key}: {value}")
            
        return columns
        
    def update_fund_data(self, fund_df, fund_estimation_df=None, fund_rank_df=None, fund_achievement_data=None):
        """
        更新基金数据，添加估算信息、历史增长率数据和业绩数据
        
        Args:
            fund_df (pd.DataFrame): 基金信息数据
            fund_estimation_df (pd.DataFrame, optional): 基金估算数据
            fund_rank_df (pd.DataFrame, optional): 基金历史增长率数据
            fund_achievement_data (dict, optional): 基金业绩数据
            
        Returns:
            pd.DataFrame: 更新后的基金数据
        """
        # 创建结果DataFrame
        result_df = fund_df.copy()
        
        # 添加新列用于存储净值估算数据
        result_df['估算值'] = None
        result_df['估算增长率'] = None
        result_df['公布单位净值'] = None
        result_df['公布日增长率'] = None
        
        # 添加新列用于存储历史增长率数据
        result_df['近1周'] = None
        result_df['近1月'] = None
        result_df['近3月'] = None
        result_df['近6月'] = None
        result_df['近1年'] = None
        result_df['近2年'] = None
        result_df['近3年'] = None
        result_df['今年来'] = None
        result_df['成立来'] = None
        
        # 添加新列用于存储基金基本信息
        result_df['日期'] = None
        result_df['单位净值'] = None
        result_df['累计净值'] = None
        result_df['日增长率'] = None
        
        # 添加新列用于存储基金最大回撤数据
        result_df['成立以来_最大回撤'] = None
        result_df['今年以来_最大回撤'] = None
        result_df['近1月_最大回撤'] = None
        result_df['近3月_最大回撤'] = None
        result_df['近6月_最大回撤'] = None
        result_df['近1年_最大回撤'] = None
        result_df['近3年_最大回撤'] = None
        result_df['近5年_最大回撤'] = None

        # 获取列名
        columns = self.get_column_names(fund_estimation_df)
        
        # 为每个基金查找对应的估算数据
        found_count = 0
        for index, row in fund_df.iterrows():
            fund_code = row['基金代码']
            
            # 在估算数据中查找匹配的基金
            if fund_estimation_df is not None:
                estimation_row = fund_estimation_df[fund_estimation_df['基金代码'] == fund_code]

                if not estimation_row.empty:
                    # 提取估算数据
                    if columns['est_value']:
                        result_df.at[index, '估算值'] = estimation_row[columns['est_value']].values[0]
                    if columns['est_growth']:
                        result_df.at[index, '估算增长率'] = estimation_row[columns['est_growth']].values[0]
                    if columns['pub_value']:
                        result_df.at[index, '公布单位净值'] = estimation_row[columns['pub_value']].values[0]
                    if columns['pub_growth']:
                        result_df.at[index, '公布日增长率'] = estimation_row[columns['pub_growth']].values[0]

                    found_count += 1
                else:
                    logger.info(f"未找到基金 {fund_code} 的估算数据")
            
            # 如果提供了历史增长率数据，查找对应的历史增长率信息
            if fund_rank_df is not None:
                rank_row = fund_rank_df[fund_rank_df['基金代码'] == fund_code]
                if not rank_row.empty:
                    # 提取历史增长率数据
                    historical_columns = ['近1周', '近1月', '近3月', '近6月', '近1年', '近2年', '近3年', '今年来', '成立来']
                    for col in historical_columns:
                        if col in rank_row.columns:
                            result_df.at[index, col] = rank_row[col].values[0]
                    
                    # 提取基金基本信息
                    basic_columns = ['日期', '单位净值', '累计净值', '日增长率']
                    for col in basic_columns:
                        if col in rank_row.columns:
                            result_df.at[index, col] = rank_row[col].values[0]
                else:
                    logger.info(f"未找到基金 {fund_code} 的历史增长率数据")
                    
            # 如果提供了基金业绩数据，查找对应的最大回撤信息
            if fund_achievement_data is not None and fund_code in fund_achievement_data:
                achievement_data = fund_achievement_data[fund_code]
                # 提取最大回撤数据
                max_drawdown_columns = ['成立以来', '今年以来', '近1月', '近3月', '近6月', '近1年', '近3年', '近5年']
                for col in max_drawdown_columns:
                    if col in achievement_data:
                        result_df.at[index, f'{col}_最大回撤'] = achievement_data[col]
            
            # 添加短暂延迟以避免请求过于频繁
            time.sleep(0.01)
            
        logger.info(f"总共找到了 {found_count} 个基金的估算数据")
        return result_df
        
    def save_data(self, result_df):
        """
        保存更新后的数据到文件
        
        Args:
            result_df (pd.DataFrame): 更新后的基金数据
        """
        try:
            result_df.to_csv(self.output_path, index=False)
            logger.info(f"数据已保存到 {self.output_path}")
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            raise
            
    def format_email_content(self, result_df):
        """
        格式化邮件内容
        
        Args:
            result_df (pd.DataFrame): 基金数据
            
        Returns:
            str: 格式化的HTML邮件内容
        """
        # 创建结果副本并处理估算增长率排序
        result_df_sorted = result_df.copy()
        
        # 将估算增长率转换为数值用于排序
        def extract_growth_rate(value):
            if pd.isna(value) or value == '---':
                return float('-inf')  # 将空值排在最后
            try:
                return float(str(value).rstrip('%'))
            except:
                return float('-inf')
        
        result_df_sorted['估算增长率数值'] = result_df_sorted['估算增长率'].apply(extract_growth_rate)
        result_df_sorted = result_df_sorted.sort_values('估算增长率数值', ascending=False)
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .positive {{ color: #ff0000; }}
                .negative {{ color: #008000; }}
                .historical-table {{ margin-top: 30px; }}
            </style>
        </head>
        <body>
            <h1>基金净值估算数据更新报告</h1>
            <p>更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <h2>基金估算增长率排行</h2>
            <table>
                <tr>
                    <th>基金代码</th>
                    <th>基金名称</th>
                    <th>板块</th>
                    <th>估算值</th>
                    <th>估算增长率</th>
                    <th>公布单位净值</th>
                    <th>公布日增长率</th>
                </tr>
        """
        
        for _, row in result_df_sorted.iterrows():
            # 处理增长率的显示颜色
            est_growth = row['估算增长率'] if pd.notna(row['估算增长率']) else '---'
            pub_growth = row['公布日增长率'] if pd.notna(row['公布日增长率']) else '---'
            
            est_growth_class = ""
            pub_growth_class = ""
            
            if est_growth != '---':
                try:
                    est_val = float(est_growth.rstrip('%'))
                    est_growth_class = "positive" if est_val > 0 else "negative"
                except:
                    pass
                    
            if pub_growth != '---':
                try:
                    pub_val = float(pub_growth.rstrip('%'))
                    pub_growth_class = "positive" if pub_val > 0 else "negative"
                except:
                    pass
            
            html_content += f"""
                <tr>
                    <td>{row['基金代码']}</td>
                    <td>{row['基金名称']}</td>
                    <td>{row['板块']}</td>
                    <td>{row['估算值'] if pd.notna(row['估算值']) else '---'}</td>
                    <td class="{est_growth_class}">{est_growth}</td>
                    <td>{row['公布单位净值'] if pd.notna(row['公布单位净值']) else '---'}</td>
                    <td class="{pub_growth_class}">{pub_growth}</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <h2 class="historical-table">基金历史增长率数据</h2>
            <table>
                <tr>
                    <th>基金代码</th>
                    <th>基金名称</th>
                    <th>日期</th>
                    <th>单位净值</th>
                    <th>累计净值</th>
                    <th>日增长率</th>
                    <th>近1周</th>
                    <th>近1月</th>
                    <th>近3月</th>
                    <th>近6月</th>
                    <th>近1年</th>
                    <th>近3年</th>
                    <th>今年来</th>
                    <th>成立来</th>
                </tr>
        """
        
        # 添加历史增长率数据
        for _, row in result_df_sorted.iterrows():
            # 获取基金基本信息
            basic_info = []
            for col in ['日期', '单位净值', '累计净值', '日增长率']:
                value = row[col] if pd.notna(row[col]) else '---'
                # 为日增长率添加颜色样式
                value_class = ""
                if col == '日增长率' and value != '---':
                    try:
                        val = float(str(value).rstrip('%'))
                        value_class = "positive" if val > 0 else "negative"
                    except:
                        pass
                basic_info.append((value, value_class))
            
            # 获取历史增长率数据
            historical_cols = ['近1周', '近1月', '近3月', '近6月', '近1年', '近3年', '今年来', '成立来']
            historical_data = []
            
            for col in historical_cols:
                value = row[col] if pd.notna(row[col]) else '---'
                # 为历史增长率数据添加颜色样式
                value_class = ""
                if value != '---':
                    try:
                        val = float(str(value).rstrip('%'))
                        value_class = "positive" if val > 0 else "negative"
                    except:
                        pass
                historical_data.append((value, value_class))
            
            html_content += f"""
                <tr>
                    <td>{row['基金代码']}</td>
                    <td>{row['基金名称']}</td>
            """
            
            # 添加基本信息列
            for value, value_class in basic_info:
                if value_class:
                    html_content += f'<td class="{value_class}">{value}</td>'
                else:
                    html_content += f'<td>{value}</td>'
            
            # 添加历史增长率列
            for value, value_class in historical_data:
                if value_class:
                    html_content += f'<td class="{value_class}">{value}</td>'
                else:
                    html_content += f'<td>{value}</td>'
            
            html_content += '</tr>'
        
        html_content += """
            </table>
            
            <h2 class="historical-table">基金最大回撤数据</h2>
            <table>
                <tr>
                    <th>基金代码</th>
                    <th>基金名称</th>
                    <th>成立以来_最大回撤</th>
                    <th>今年以来_最大回撤</th>
                    <th>近1月_最大回撤</th>
                    <th>近3月_最大回撤</th>
                    <th>近6月_最大回撤</th>
                    <th>近1年_最大回撤</th>
                    <th>近3年_最大回撤</th>
                    <th>近5年_最大回撤</th>
                </tr>
        """
        
        # 添加最大回撤数据
        for _, row in result_df_sorted.iterrows():
            html_content += f"""
                <tr>
                    <td>{row['基金代码']}</td>
                    <td>{row['基金名称']}</td>
            """
            
            # 获取最大回撤数据
            max_drawdown_cols = ['成立以来_最大回撤', '今年以来_最大回撤', '近1月_最大回撤', 
                                '近3月_最大回撤', '近6月_最大回撤', '近1年_最大回撤', 
                                '近3年_最大回撤', '近5年_最大回撤']
            
            for col in max_drawdown_cols:
                value = row[col] if pd.notna(row[col]) else '---'
                # 为最大回撤数据添加颜色样式（回撤越小越好，所以负值显示为绿色）
                value_class = ""
                if value != '---':
                    try:
                        val = float(str(value).rstrip('%'))
                        value_class = "negative" if val < 0 else "positive"
                    except:
                        pass
                if value_class:
                    html_content += f'<td class="{value_class}">{value}</td>'
                else:
                    html_content += f'<td>{value}</td>'
            
            html_content += '</tr>'
        
        html_content += """
            </table>
        </body>
        </html>
        """
        
        return html_content
        
    def send_email(self, result_df):
        """
        发送邮件
        
        Args:
            result_df (pd.DataFrame): 基金数据
        """
        try:
            # 创建邮件对象
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            message["Subject"] = Header(f"基金净值估算数据更新报告 - {datetime.now().strftime('%Y-%m-%d')}", "utf-8")
            
            # 格式化邮件内容
            html_content = self.format_email_content(result_df)
            
            # 添加HTML内容
            message.attach(MIMEText(html_content, "html", "utf-8"))
            
            # 发送邮件
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, self.recipient_email, message.as_string())
            server.quit()
            
            logger.info("邮件发送成功")
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"邮件发送失败 - 身份验证错误: {e}")
            logger.error("请检查邮箱地址和密码是否正确，如果使用Gmail，请使用应用专用密码")
        except smtplib.SMTPConnectError as e:
            logger.error(f"邮件发送失败 - 连接错误: {e}")
            logger.error("请检查SMTP服务器地址和端口设置是否正确")
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            
    def run(self):
        """运行基金估算更新流程"""
        try:
            # 加载基金数据
            fund_df = self.load_fund_data()
            
            # 获取估算数据
            fund_estimation_df = self.get_fund_estimation_data()
            
            # 获取历史增长率数据
            fund_rank_df = self.get_fund_historical_growth_data()

            # 获取基金最大回撤数据
            fund_codes = fund_df['基金代码'].tolist()
            fund_achievement_data = self.get_fund_achievement_data(fund_codes)
            
            # 更新基金数据
            result_df = self.update_fund_data(fund_df, fund_estimation_df, fund_rank_df, fund_achievement_data)
            
            # 保存数据
            self.save_data(result_df)
            
            # 发送邮件
            self.send_email(result_df)
            
            logger.info("基金指标数据更新完成")
            return True
        except Exception as e:
            logger.error(f"基金指标数据更新失败: {e}")
            return False

def main():
    """主函数"""
    fund_info_path = os.path.join(current_dir, 'fund_info.csv')
    output_path = os.path.join(current_dir, 'fund_info_with_indicator.csv')
    
    estimator = FundEstimator(fund_info_path, output_path)
    success = estimator.run()
    
    if success:
        logger.info("基金指标数据更新成功")
    else:
        logger.error("基金指标数据更新失败")

if __name__ == "__main__":
    main()