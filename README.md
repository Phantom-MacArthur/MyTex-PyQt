# MyTex-PyQt

公式识别软件 - PyQt6 版本

## 功能特性
- 基于 SimpleTex API 的公式识别
- PyQt6 现代化界面
- 支持选择图片文件、截图识别、Ctrl+V 粘贴
- App Secret 明文显示（便于核对）
- 自动复制 LaTeX 结果到剪贴板

## API 配置
当前支持的 API 服务：
- **SimpleTex** (默认)

API 配置管理位于 `api_config.py` 文件中，未来可轻松扩展其他 API 服务。

## 测试配置
项目包含测试配置（App ID: XvEdRCIKdRFlkSEdp28q3Ep4, Secret: TtssQ12JCv6IrkUTqGYwuYFJkszCAAFk），
**在提交代码前请记得删除测试配置！**

## 安装依赖
```bash
pip install -r requirements.txt
```

## 运行程序
```bash
python main_pyqt.py
```