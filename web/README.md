# Spectrum 分析工具 - Web 版本

这是将原来的 tkinter 桌面应用程序转换为现代化 Web 应用的版本。

## 功能特性

- 🎵 音频文件上传和管理
- 🔄 实时处理进度显示
- ⏸️ 暂停/继续/停止控制
- 📊 CPU 使用率监控
- 📝 实时日志显示
- 🎛️ 多线程处理控制
- 📱 响应式设计，支持移动设备

## 文件结构

```
web/
├── index.html          # 主页面
├── style.css           # 样式文件
├── script.js           # 前端模拟版本
├── script_enhanced.js  # 增强版（支持后端）
├── app.py             # Flask 后端服务器
└── README.md          # 说明文档
```

## 运行方式

### 方式一：纯前端版本（简单）

1. 直接用浏览器打开 `index.html` 文件
2. 功能：模拟处理过程，不需要后端服务

### 方式二：完整版本（推荐）

1. **安装依赖**
   ```bash
   pip install flask flask-cors psutil
   ```

2. **修改 HTML 文件**
   将 `index.html` 中的脚本引用改为：
   ```html
   <script src="script_enhanced.js"></script>
   ```

3. **启动后端服务**
   ```bash
   cd web
   python app.py
   ```

4. **访问应用**
   打开浏览器访问：http://localhost:5000

## 使用说明

### 上传文件
- 点击上传区域选择文件
- 或直接拖拽音频文件到上传区域
- 支持的格式：MP3, WAV, FLAC, M4A, AAC, OGG

### 处理控制
- **开始处理**：点击"开始处理"按钮启动
- **暂停**：处理过程中可以暂停
- **停止**：完全停止处理，已处理的文件保留
- **线程数控制**：使用滑块调整并发处理线程数

### 文件夹快捷方式
- **音乐文件夹**：存放待处理的音频文件
- **数据文件夹**：存放处理结果
- **日志文件夹**：存放处理日志

### 处理类型
- **音乐文件类**：标准音频文件处理
- **数据文件类**：数据文件处理
- **日志文件类**：日志文件处理

## 技术栈

### 前端
- HTML5 + CSS3
- Vanilla JavaScript (ES6+)
- 响应式设计
- 文件拖拽上传
- 实时状态更新

### 后端 (可选)
- Flask Web 框架
- Python 多线程处理
- RESTful API
- 文件上传处理
- 系统监控

## API 接口

如果使用完整版本，后端提供以下 API：

- `POST /api/upload` - 文件上传
- `POST /api/start_processing` - 开始处理
- `GET /api/job_status/<job_id>` - 获取任务状态
- `POST /api/pause_job/<job_id>` - 暂停任务
- `POST /api/resume_job/<job_id>` - 恢复任务
- `POST /api/stop_job/<job_id>` - 停止任务
- `GET /api/system_info` - 获取系统信息

## 处理流程

1. **解密** - 对加密的音频文件进行解密
2. **格式化** - 统一音频文件格式
3. **STFT 分析**
   - STFT Unified - 统一 STFT 分析
   - STFT 3000 Detailed - 详细 3000Hz 分析
4. **功率分析**
   - Power CSV - 生成功率数据 CSV
   - Power PLT - 生成功率图表
   - Power A-Weighted - A 加权功率分析

## 特色功能

### 实时监控
- CPU 使用率实时显示
- 处理进度可视化
- 详细的处理日志

### 用户友好
- 拖拽上传
- 一键文件夹访问
- 键盘快捷键支持 (Ctrl+L 清空日志)

### 安全性
- 处理中断保护
- 文件处理状态保存
- 错误处理和恢复

## 浏览器兼容性

- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

## 开发说明

### 自定义处理模块
要集成实际的音频处理模块，需要修改 `app.py` 中的 `process_audio_files` 函数，调用您现有的处理模块：

```python
# 替换模拟处理为实际模块调用
import stft_unified
import stft_3000_detailed
import power
import power_plt
import power_aweighted

# 在处理循环中调用实际函数
stft_unified.main(file_path)
stft_3000_detailed.main(file_path)
power.main(file_path)
power_plt.main(file_path)
power_aweighted.main(file_path)
```

### 样式自定义
修改 `style.css` 文件可以自定义界面外观。

### 功能扩展
在 `script_enhanced.js` 中可以添加新的功能和交互。

## 故障排除

### 后端无法启动
- 检查 Python 依赖是否安装完整
- 确认端口 5000 没有被占用
- 查看控制台错误信息

### 文件上传失败
- 检查文件格式是否支持
- 确认文件大小没有超出限制
- 检查网络连接

### 处理过程中断
- 查看日志信息了解错误原因
- 检查磁盘空间是否充足
- 确认依赖的处理模块可用

## 许可证

本项目基于原 tkinter 应用转换而来，保持相同的许可证。
