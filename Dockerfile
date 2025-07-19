# 基础镜像
FROM python:3.10

# 设置工作目录
WORKDIR /app

# 复制当前目录内容到容器中
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirement.txt -i https://mirrors.aliyun.com/pypi/simple

# 运行应用
CMD ["python", "track_and_trade.py"]