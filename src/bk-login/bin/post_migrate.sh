#!/bin/bash

# 如果任何命令返回一个非零退出状态（错误），脚本将会立即终止执行
set -e

# 为脚本添加执行权限
chmod +x ./support-files/bin/sync-apigateway.sh

# 自动化同步网关
sh ./support-files/bin/sync-apigateway.sh

# 注册到蓝鲸通知中心
python manage.py register_application