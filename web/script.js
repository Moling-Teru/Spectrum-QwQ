// 全局变量
let isRunning = false;
let pauseProcessing = false;
let counter = 0;
let totalFiles = 0;
let maxWorkers = 4;
let uploadedFiles = [];
let processingInterval = null;
let cpuInterval = null;

// DOM 元素
const startBtn = document.getElementById('startBtn');
const pauseBtn = document.getElementById('pauseBtn');
const stopBtn = document.getElementById('stopBtn');
const statusLabel = document.getElementById('statusLabel');
const cpuLabel = document.getElementById('cpuLabel');
const threadCount = document.getElementById('threadCount');
const threadSlider = document.getElementById('threadSlider');
const progressFill = document.getElementById('progressFill');
const progressLabel = document.getElementById('progressLabel');
const processCount = document.getElementById('processCount');
const logContainer = document.getElementById('logContainer');
const clearLogBtn = document.getElementById('clearLogBtn');
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    updateProcessCount();
    startCPUMonitoring();
    addLogMessage('工具已启动，上传音频文件并点击"开始处理"按钮开始处理', 'info');
});

// 初始化事件监听器
function initializeEventListeners() {
    // 按钮事件
    startBtn.addEventListener('click', startProcessing);
    pauseBtn.addEventListener('click', togglePause);
    stopBtn.addEventListener('click', stopProcessing);
    clearLogBtn.addEventListener('click', clearLog);

    // 线程滑块事件
    threadSlider.addEventListener('input', function() {
        maxWorkers = parseInt(this.value);
        threadCount.textContent = maxWorkers;
        updateProcessCount();
    });

    // 文件类型按钮事件
    document.querySelectorAll('.file-type-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.file-type-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            addLogMessage(`切换到${this.textContent}处理模式`, 'info');
        });
    });

    // 文件夹按钮事件
    document.querySelectorAll('.folder-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const folder = this.dataset.folder;
            addLogMessage(`尝试打开文件夹: ${folder}`, 'info');
            // 在实际实现中，这里可能需要调用后端API
        });
    });

    // 文件上传事件
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);
}

// 文件拖拽处理
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    addFiles(files);
}

// 添加文件
function addFiles(files) {
    const audioFiles = files.filter(file => file.type.startsWith('audio/'));
    
    if (audioFiles.length === 0) {
        addLogMessage('请选择音频文件！', 'warning');
        return;
    }

    audioFiles.forEach(file => {
        if (!uploadedFiles.find(f => f.name === file.name && f.size === file.size)) {
            uploadedFiles.push(file);
            addLogMessage(`已添加文件: ${file.name} (${formatFileSize(file.size)})`, 'success');
        }
    });

    updateFileList();
    updateTotalFiles();
}

// 更新文件列表显示
function updateFileList() {
    fileList.innerHTML = '';
    
    uploadedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-icon">🎵</div>
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-size">${formatFileSize(file.size)}</div>
            </div>
            <button class="file-remove" onclick="removeFile(${index})">×</button>
        `;
        fileList.appendChild(fileItem);
    });
}

// 移除文件
function removeFile(index) {
    const fileName = uploadedFiles[index].name;
    uploadedFiles.splice(index, 1);
    updateFileList();
    updateTotalFiles();
    addLogMessage(`已移除文件: ${fileName}`, 'info');
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 更新总文件数
function updateTotalFiles() {
    totalFiles = uploadedFiles.length;
    updateProgress();
}

// 开始处理
function startProcessing() {
    if (isRunning) return;
    
    if (uploadedFiles.length === 0) {
        addLogMessage('请先上传音频文件！', 'warning');
        return;
    }

    // 重置状态
    isRunning = true;
    pauseProcessing = false;
    counter = 0;
    
    // 更新UI状态
    startBtn.textContent = '处理中...';
    startBtn.disabled = true;
    pauseBtn.disabled = false;
    pauseBtn.textContent = '暂停';
    statusLabel.textContent = '状态: 初始化中';
    
    updateProgress();
    
    addLogMessage('='.repeat(50), 'info');
    addLogMessage('开始处理音频文件...', 'info');
    addLogMessage('执行解密...', 'info');
    
    // 模拟解密过程
    setTimeout(() => {
        addLogMessage('解密完成', 'success');
        addLogMessage('执行格式化...', 'info');
        
        // 模拟格式化过程
        setTimeout(() => {
            addLogMessage('格式化完成', 'success');
            addLogMessage(`开始处理 ${totalFiles} 个音乐文件...(使用 ${maxWorkers} 个线程)`, 'info');
            
            // 开始实际处理
            startFileProcessing();
        }, 1000);
    }, 1500);
}

// 开始文件处理
function startFileProcessing() {
    statusLabel.textContent = '状态: 处理中';
    
    processingInterval = setInterval(() => {
        if (!isRunning || pauseProcessing) return;
        
        if (counter < totalFiles) {
            const currentFile = uploadedFiles[counter];
            processFile(currentFile);
        } else {
            // 处理完成
            completeProcessing();
        }
    }, 2000); // 每2秒处理一个文件（模拟）
}

// 处理单个文件
function processFile(file) {
    const fileName = file.name;
    const fileNameClean = fileName.replace(/\.[^/.]+$/, ""); // 移除扩展名
    
    addLogMessage(`正在处理: ${fileName}`, 'info');
    
    // 模拟各个处理步骤
    const steps = [
        'STFT Unified',
        'STFT 3000 Detailed', 
        'Power CSV',
        'Power PLT',
        'Power A-Weighted'
    ];
    
    let stepIndex = 0;
    const stepInterval = setInterval(() => {
        if (!isRunning || pauseProcessing) {
            clearInterval(stepInterval);
            return;
        }
        
        if (stepIndex < steps.length) {
            addLogMessage(`Processing ${fileName}: ${steps[stepIndex]}`, 'info');
            stepIndex++;
        } else {
            clearInterval(stepInterval);
            
            // 文件处理完成
            counter++;
            updateProgress();
            addLogMessage(`Song-${fileName} Finished! [${counter}/${totalFiles}]`, 'success');
            
            // 移除已处理的文件
            const fileIndex = uploadedFiles.findIndex(f => f.name === fileName);
            if (fileIndex !== -1) {
                uploadedFiles.splice(fileIndex, 1);
                updateFileList();
            }
        }
    }, 300);
}

// 完成处理
function completeProcessing() {
    clearInterval(processingInterval);
    isRunning = false;
    
    const completionMsg = `所有文件处理完成!\n总共处理了 ${counter} 个文件.`;
    addLogMessage('='.repeat(50), 'success');
    addLogMessage(completionMsg, 'success');
    
    // 重置UI状态
    startBtn.textContent = '开始处理';
    startBtn.disabled = false;
    pauseBtn.disabled = true;
    statusLabel.textContent = '状态: 空闲';
    
    // 重置计数器
    counter = 0;
    updateProgress();
}

// 暂停/继续处理
function togglePause() {
    if (!isRunning) return;
    
    pauseProcessing = !pauseProcessing;
    
    if (pauseProcessing) {
        pauseBtn.textContent = '继续';
        statusLabel.textContent = '状态: 暂停中';
        addLogMessage('Processing paused...', 'warning');
    } else {
        pauseBtn.textContent = '暂停';
        statusLabel.textContent = '状态: 处理中';
        addLogMessage('Processing resumed...', 'info');
    }
}

// 停止处理
function stopProcessing() {
    if (!isRunning) return;
    
    if (confirm('确定要停止处理吗？\n已经处理的文件将不会丢失。')) {
        isRunning = false;
        pauseProcessing = false;
        
        if (processingInterval) {
            clearInterval(processingInterval);
        }
        
        addLogMessage('处理被用户中断', 'warning');
        
        // 重置UI状态
        startBtn.textContent = '开始处理';
        startBtn.disabled = false;
        pauseBtn.disabled = true;
        statusLabel.textContent = '状态: 已停止';
    }
}

// 更新进度
function updateProgress() {
    const progress = totalFiles > 0 ? (counter / totalFiles) * 100 : 0;
    progressFill.style.width = `${progress}%`;
    progressLabel.textContent = `进度: ${counter}/${totalFiles} (${progress.toFixed(1)}%)`;
}

// 更新进程数显示
function updateProcessCount() {
    processCount.textContent = maxWorkers;
}

// 添加日志消息
function addLogMessage(message, type = 'info') {
    const logMessage = document.createElement('div');
    logMessage.className = `log-message ${type}`;
    
    const timestamp = new Date().toLocaleString('zh-CN');
    logMessage.textContent = `[${timestamp}] ${message}`;
    
    logContainer.appendChild(logMessage);
    logContainer.scrollTop = logContainer.scrollHeight;
    
    // 限制日志条数，避免内存溢出
    if (logContainer.children.length > 1000) {
        logContainer.removeChild(logContainer.firstChild);
    }
}

// 清空日志
function clearLog() {
    logContainer.innerHTML = '';
    addLogMessage('日志已清空', 'info');
}

// CPU监控
function startCPUMonitoring() {
    cpuInterval = setInterval(() => {
        // 模拟CPU使用率
        const cpuUsage = isRunning ? 
            (Math.random() * 40 + 30).toFixed(1) : 
            (Math.random() * 10 + 5).toFixed(1);
        cpuLabel.textContent = `CPU使用率: ${cpuUsage}%`;
    }, 1000);
}

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
    if (processingInterval) clearInterval(processingInterval);
    if (cpuInterval) clearInterval(cpuInterval);
    
    if (isRunning) {
        return '处理正在进行中，确定要离开吗？';
    }
});

// 键盘快捷键
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'l') {
        e.preventDefault();
        clearLog();
    }
    
    if (e.key === 'F5' && isRunning) {
        e.preventDefault();
        if (confirm('处理正在进行中，确定要刷新页面吗？')) {
            location.reload();
        }
    }
});

// 工具函数：节流
function throttle(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
