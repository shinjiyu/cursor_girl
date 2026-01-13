# Next.js 服务器 Docker 部署指南

## 概述

Next.js 服务器已支持 Docker 容器化部署，支持生产模式和开发模式。

## 快速开始

### 生产模式部署

```bash
# 使用生产模式 Dockerfile
docker build -f Dockerfile.prod -t aituber-nextjs:latest .

# 运行容器
docker run -d \
  -p 3000:3000 \
  -e NEXT_PUBLIC_ORTENSIA_SERVER=ws://your-central-server:8765 \
  --name aituber-nextjs \
  aituber-nextjs:latest
```

### 使用 Docker Compose

```bash
# 方式 1: 仅部署 Next.js 服务器
cd aituber-kit
docker-compose -f docker-compose.prod.yml up -d

# 方式 2: 同时部署中央服务器和 Next.js 服务器（推荐）
cd ..  # 回到项目根目录
docker-compose -f docker-compose.full.yml up -d
```

## 环境变量配置

### 必需环境变量

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `NEXT_PUBLIC_ORTENSIA_SERVER` | 中央服务器 WebSocket 地址 | `ws://localhost:8765` | `wss://xxx.trycloudflare.com/` |

### 可选环境变量

| 变量名 | 说明 | 用途 |
|--------|------|------|
| `GOOGLE_TTS_KEY` | Google TTS API Key | TTS 服务 |
| `AZURE_TTS_KEY` | Azure TTS Key | TTS 服务 |
| `AZURE_TTS_REGION` | Azure TTS 区域 | TTS 服务 |
| `SUPABASE_URL` | Supabase URL | 数据存储 |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Service Role Key | 数据存储 |

### 配置方式

**方式 1: 环境变量文件（`.env`）**

```bash
# .env
NEXT_PUBLIC_ORTENSIA_SERVER=wss://your-server.trycloudflare.com/
GOOGLE_TTS_KEY=your_key_here
```

**方式 2: Docker Compose 环境变量**

```yaml
environment:
  - NEXT_PUBLIC_ORTENSIA_SERVER=wss://your-server.trycloudflare.com/
```

**方式 3: 运行时指定**

```bash
docker run -e NEXT_PUBLIC_ORTENSIA_SERVER=wss://xxx.trycloudflare.com/ ...
```

## 部署模式

### 1. 生产模式 - Standalone（推荐）

**特点：**
- 多阶段构建，镜像体积小
- 使用 Next.js standalone 输出（最小化运行时）
- 不包含开发依赖
- 适合生产环境

**构建：**
```bash
docker build -f Dockerfile.prod -t aituber-nextjs:latest .
```

**注意：** 需要确保 `next.config.js` 中启用了 `output: 'standalone'`（已配置）

### 2. 生产模式 - 标准（备选）

如果 standalone 模式有问题，可以使用标准模式：

**构建：**
```bash
docker build -f Dockerfile.prod.simple -t aituber-nextjs:latest .
```

**特点：**
- 包含完整的 node_modules
- 镜像体积较大
- 更稳定，兼容性更好

### 2. 开发模式

**特点：**
- 包含开发依赖
- 支持热重载
- 镜像体积较大
- 适合本地开发

**构建：**
```bash
docker build -f Dockerfile -t aituber-nextjs:dev .
```

## 完整部署示例

### 场景：同时部署中央服务器和 Next.js 服务器

```bash
# 1. 创建环境变量文件
cat > .env << EOF
NEXT_PUBLIC_ORTENSIA_SERVER=ws://ortensia-central:8765
GOOGLE_TTS_KEY=your_key_here
EOF

# 2. 启动所有服务
docker-compose -f docker-compose.full.yml up -d

# 3. 查看日志
docker-compose -f docker-compose.full.yml logs -f

# 4. 停止服务
docker-compose -f docker-compose.full.yml down
```

### 场景：仅部署 Next.js 服务器（中央服务器已部署）

```bash
# 1. 设置中央服务器地址
export NEXT_PUBLIC_ORTENSIA_SERVER=wss://your-central-server.trycloudflare.com/

# 2. 启动 Next.js 服务器
cd aituber-kit
docker-compose -f docker-compose.prod.yml up -d

# 3. 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

## 网络配置

### 容器间通信

如果中央服务器和 Next.js 服务器都在 Docker 网络中：

```yaml
# docker-compose.full.yml
services:
  ortensia-central:
    networks:
      - ortensia-network
  
  aituber-nextjs:
    environment:
      - NEXT_PUBLIC_ORTENSIA_SERVER=ws://ortensia-central:8765
    networks:
      - ortensia-network
```

### 外部访问

如果中央服务器在容器外（远程服务器）：

```yaml
environment:
  - NEXT_PUBLIC_ORTENSIA_SERVER=wss://remote-server.trycloudflare.com/
```

## 资源访问

### 静态资源（VRM、Live2D、图片）

Next.js 服务器需要访问 `public/` 目录中的资源文件。

**方式 1: 挂载卷（推荐）**

```yaml
volumes:
  - ./public:/app/public:ro
```

**方式 2: 构建时复制（资源固定）**

资源文件会在构建时复制到镜像中，无需挂载。

## 故障排查

### 1. 无法连接到中央服务器

**检查：**
```bash
# 查看环境变量
docker exec aituber-nextjs env | grep ORTENSIA

# 测试网络连接
docker exec aituber-nextjs wget -O- http://ortensia-central:8765
```

**解决：**
- 确认 `NEXT_PUBLIC_ORTENSIA_SERVER` 环境变量正确
- 确认中央服务器正在运行
- 确认网络配置正确（如果在同一 Docker 网络）

### 2. 静态资源无法加载

**检查：**
```bash
# 查看 public 目录
docker exec aituber-nextjs ls -la /app/public
```

**解决：**
- 确认 `public/` 目录已挂载或已复制到镜像
- 检查文件权限

### 3. 构建失败

**常见原因：**
- Canvas 依赖缺失（已包含在 Dockerfile 中）
- Node.js 版本不匹配（使用 Node 20）

**解决：**
```bash
# 清理构建缓存
docker builder prune

# 重新构建
docker build --no-cache -f Dockerfile.prod -t aituber-nextjs:latest .
```

## 性能优化

### 1. 使用多阶段构建

生产模式 Dockerfile 已使用多阶段构建，减小镜像体积。

### 2. 启用 Next.js Standalone

已在 `next.config.js` 中配置 standalone 输出模式。

### 3. 缓存优化

```dockerfile
# 先复制 package.json，利用 Docker 缓存
COPY package*.json ./
RUN npm ci
COPY . .
```

## 安全建议

1. **使用非 root 用户运行**（已在 Dockerfile.prod 中配置）
2. **只暴露必要端口**（3000）
3. **使用环境变量文件**（不要硬编码密钥）
4. **定期更新基础镜像**（`node:20-alpine`）

## 相关文档

- [中央服务器 Docker 部署](../bridge/README.md)
- [架构说明](./docs/ARCHITECTURE.md)
- [Next.js 官方 Docker 文档](https://nextjs.org/docs/deployment#docker-image)
