FROM python:3.12-slim

# 安全与日志：不写 .pyc，stdout 不缓冲
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/bridge

# 先安装依赖（利用 Docker cache）
COPY requirements.txt /app/bridge/requirements.txt
RUN pip install --no-cache-dir -r /app/bridge/requirements.txt

# 只复制运行所需的最小代码（避免把大音频/测试文件打进镜像）
COPY protocol.py /app/bridge/protocol.py
COPY websocket_server.py /app/bridge/websocket_server.py
COPY __init__.py /app/bridge/__init__.py

# 默认端口（可通过 ORTENSIA_PORT 覆盖）
EXPOSE 8765

# 默认监听 0.0.0.0:8765（可通过环境变量覆盖）
ENV ORTENSIA_HOST=0.0.0.0 \
    ORTENSIA_PORT=8765

CMD ["python", "websocket_server.py"]
