# 基金净值估算数据更新工具

## 功能说明

该工具用于获取基金的实时估算净值数据，并将其添加到基金信息文件中。主要功能包括：

1. 从AKShare获取基金净值估算数据
2. 将估算数据与现有基金信息进行匹配
3. 更新基金信息文件，添加以下字段：
   - 估算值：基金的估算净值
   - 估算增长率：基于估算净值计算的增长率
   - 公布单位净值：最近公布的单位净值
   - 公布日增长率：最近公布的日增长率
4. 定时执行：每个工作日下午2点自动更新数据
5. 邮件通知：更新完成后发送格式化的邮件报告

## 文件说明

- `fund_estimator.py`：主要的Python脚本，包含基金估算数据更新的逻辑
- `schedule_estimator.sh`：用于设置定时任务的shell脚本
- `.env`：环境变量配置文件，包含邮件配置信息
- `fund_info_with_estimation.csv`：更新后的基金信息文件，包含估算数据
- `fund_estimator.log`：运行日志文件

## 使用方法

### 手动执行

```bash
cd /Users/klb3713/work/trade
python fund_eval/fund_estimator.py
```

### 定时执行

工具已设置为每个工作日下午2点自动执行，无需手动干预。

定时任务设置命令：
```bash
0 14 * * 1-5 /Users/klb3713/work/trade/fund_eval/schedule_estimator.sh
```

## 邮件配置

在 `.env` 文件中配置邮件相关信息：

```bash
# 邮件配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient@example.com
```

### Gmail配置说明

1. 如果使用Gmail，需要使用应用专用密码而不是账户密码：
   - 登录Google账户
   - 进入"安全性"设置
   - 启用"两步验证"
   - 生成应用专用密码
   - 在`SENDER_PASSWORD`中使用应用专用密码

2. 确保Gmail已启用IMAP/SMTP访问

### 其他邮箱服务商

对于其他邮箱服务商，需要修改`SMTP_SERVER`和`SMTP_PORT`：

```bash
# QQ邮箱示例
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587

# 163邮箱示例
SMTP_SERVER=smtp.163.com
SMTP_PORT=25

# Outlook邮箱示例
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

多个收件人可以用逗号分隔：
```bash
RECIPIENT_EMAIL=recipient1@example.com,recipient2@example.com
```

## 代码结构

### FundEstimator类

主要的功能类，包含以下方法：

- `__init__()`：初始化方法
- `load_fund_data()`：加载基金信息数据
- `get_fund_estimation_data()`：获取基金净值估算数据
- `standardize_fund_codes()`：标准化基金代码格式
- `get_column_names()`：获取估算数据的列名
- `update_fund_data()`：更新基金数据，添加估算信息
- `save_data()`：保存更新后的数据到文件
- `format_email_content()`：格式化邮件内容
- `send_email()`：发送邮件
- `run()`：运行基金估算更新流程

### 主函数

`main()`函数创建FundEstimator实例并执行更新流程。

## 注意事项

1. 确保系统已安装AKShare库
2. 确保基金信息文件`fund_info.csv`存在于指定路径
3. 估算数据仅在交易日更新，非交易日可能无数据
4. 部分基金可能无法匹配到估算数据，会在日志中显示
5. 邮件发送可能受网络或邮件服务器限制影响
6. 应用专用密码仅适用于启用了两步验证的Google账户