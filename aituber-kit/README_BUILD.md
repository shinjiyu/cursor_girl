# 构建和打包快速参考

## Electron 打包

```bash
# 完整流程
npm run build:electron

# 分步执行
npm run build:static    # 构建静态文件
npm run pack:electron   # 打包 Electron
```

## Web/移动端访问

应用已支持响应式设计，可在以下环境访问：

- **PC 浏览器**: `http://localhost:3000/assistant`
- **移动设备**: `http://your-ip:3000/assistant`
- **Electron**: 桌面应用

## 多终端访问

所有设备连接到同一个中央服务器，实现会话同步。

配置中央服务器地址：
```bash
NEXT_PUBLIC_ORTENSIA_SERVER=wss://your-server.trycloudflare.com/
```

详细文档请参考 [BUILD.md](./BUILD.md)
