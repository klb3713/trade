#!/bin/bash
# 基金估算数据更新脚本
# 用于设置定时任务，每天下午2点执行基金数据更新

# 获取当前脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
echo "Project directory: $PROJECT_DIR"

# 设置Python环境
export PYTHONPATH="$PROJECT_DIR"
source "$PROJECT_DIR/venv/bin/activate"

# 执行基金估算数据更新
python "$PROJECT_DIR/fund_eval/fund_estimator.py"