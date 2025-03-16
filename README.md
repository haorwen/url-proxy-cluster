# URL请求转发工具

## 项目简介

本工具是一个基于Flask和Socket.IO实现的分布式URL请求转发系统，支持通过管理页面向多个客户端批量发送URL请求指令，并自动保存获取到的网络资源到本地。

## 主要功能

✅ 多客户端实时状态监控  
✅ 批量/定向URL请求分发  
✅ 自动重命名避免文件冲突  
✅ 下载内容持久化存储  
✅ WebSocket实时通信  

## 技术栈

- 后端：Python/Flask + Flask-SocketIO
- 前端：HTML5 + Socket.IO客户端
- 存储：本地文件系统

## 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/haorwen/url-proxy-cluster.git
```
2. 安装依赖
```bash
pip install -r requirements.txt
```

## 快速开始

1. 启动服务
```bash
python app.py
```
2. 访问客户端界面：`http://localhost:5000`  
3. 访问管理界面：`http://localhost:5000/static/admin.html`

## 使用说明

### 客户端
- 自动连接服务端并显示连接状态
- 接收URL请求指令后自动获取网络内容
- 下载文件保存在`downloads`目录

### 管理端
- 实时显示在线客户端列表
- 支持向全部或指定客户端发送请求
- 显示最近操作结果

## 文件存储策略

1. 自动从URL或响应头解析文件名
2. 特殊字符自动替换为下划线
3. 重复文件自动添加序号（例：file(1).txt）
4. 所有文件保存在`downloads`目录

## 项目结构
```
├── app.py            # 服务端主程序
├── requirements.txt  # 依赖文件
├── templates
│   └── index.html    # 客户端界面
└── static
    ├── admin.html    # 管理端界面
    ├── socket.io.js  # Socket.IO客户端库
    └── eruda.js  # eruda调试工具
```

## 注意事项

1. 确保5000端口未被占用
2. 客户端需要保持页面打开状态
3. 下载目录会自动创建
4. 支持HTTP/HTTPS协议URL

## 许可证

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

本项目采用 Apache License 2.0 许可证。完整的许可证文本请参见 [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)。

Copyright 2025 URL请求转发工具

根据 Apache License Version 2.0 的规定，在未经事先书面许可的情况下，本软件仅可用于非商业用途，详细信息请参阅许可证全文。