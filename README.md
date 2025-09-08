# AI智能抠图工具

一行代码去除图片背景，专为电商和头像处理设计的专业抠图网站。

## ✨ 特性

- 🚀 **一键抠图**：使用先进的AI算法，自动识别并去除图片背景
- 🎯 **专业级效果**：基于 rembg 深度学习模型，效果媲美专业抠图软件
- 📱 **响应式设计**：完美适配桌面端和移动端
- ⚡ **快速处理**：几秒钟内完成抠图，无需等待
- 🎨 **现代化界面**：美观的用户界面，优秀的用户体验
- 📁 **批量处理**：支持拖拽上传，方便快捷

## 🛠️ 技术栈

- **后端**: Python Flask
- **AI引擎**: rembg (基于 u2net 深度学习模型)
- **前端**: HTML5, CSS3, JavaScript
- **图像处理**: Pillow, OpenCV

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
# 方法1：使用Python直接运行
python app.py

# 方法2：使用启动脚本
python run.py
```

### 3. 访问网站

打开浏览器访问：http://localhost:5000

## 📖 使用说明

1. **上传图片**：
   - 点击"选择图片"按钮选择文件
   - 或直接拖拽图片到上传区域
   - 支持 JPG、PNG、JPEG 格式，最大 16MB

2. **自动抠图**：
   - 系统会自动识别前景和背景
   - 使用AI算法精确抠取主体

3. **下载结果**：
   - 处理完成后自动显示对比效果
   - 点击"下载抠图结果"保存透明背景图片

4. **处理新图片**：
   - 点击"上传新图片"按钮重新开始

## 🎯 应用场景

- **电商产品图**：去除白色背景，突出产品主体
- **头像处理**：为社交媒体创建透明头像
- **设计素材**：快速获取无背景的图片素材
- **海报设计**：为设计作品准备透明元素

## 📁 项目结构

```
抠图/
├── app.py                 # Flask 主应用
├── run.py                 # 启动脚本
├── requirements.txt       # Python 依赖
├── templates/
│   └── index.html         # 前端页面
├── static/
│   ├── css/
│   │   └── style.css      # 样式文件
│   └── js/
│       └── main.js        # 前端逻辑
├── uploads/               # 上传的原始图片
└── processed/             # 处理后的图片
```

## 🔧 配置说明

- **端口**: 默认运行在 5000 端口
- **文件大小限制**: 最大 16MB
- **支持格式**: JPG, PNG, JPEG
- **输出格式**: PNG (支持透明背景)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📄 许可证

本项目基于 MIT 许可证开源。

## 🙏 致谢

- [rembg](https://github.com/danielgatis/rembg) - 优秀的抠图AI库
- [Flask](https://flask.palletsprojects.com/) - Python Web框架
- [u2net](https://github.com/xuebinqin/U-2-Net) - 底层深度学习模型
