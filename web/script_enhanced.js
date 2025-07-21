// 配置
const API_BASE_URL = window.location.origin + '/api';
const USE_BACKEND = true; // 设置为 false 可以使用纯前端模拟

// 全局变量
let isRunning = false;
let pauseProcessing = false;
let counter = 0;
let totalFiles = 0;
let maxWorkers = 4;
let uploadedFiles = [];
let currentJobId = null;
let processingInterval = null;
let cpuInterval = null;
let statusInterval = null;

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
    
    // 检查后端连接
    if (USE_BACKEND) {
        checkBackendConnection();
    }
});

// 检查后端连接
async function checkBackendConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/system_info`);
        if (response.ok) {
            addLogMessage('后端服务连接成功', 'success');
        } else {
            throw new Error('后端响应异常');
        }
    } catch (error) {
        addLogMessage('后端服务连接失败，将使用前端模拟模式', 'warning');
        USE_BACKEND = false;
    }
}

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
async function addFiles(files) {
    const audioFiles = files.filter(file => file.type.startsWith('audio/') || 
        file.name.toLowerCase().match(/\.(mp3|wav|flac|m4a|aac|ogg)$/));
    
    if (audioFiles.length === 0) {
        addLogMessage('请选择音频文件！', 'warning');
        return;
    }

    if (USE_BACKEND) {
        // 使用后端处理文件上传
        try {
            const formData = new FormData();
            audioFiles.forEach(file => {
                formData.append('files', file);
            });

            const response = await fetch(`${API_BASE_URL}/upload`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                uploadedFiles = [...uploadedFiles, ...result.files];
                addLogMessage(result.message, 'success');
                updateFileList();
                updateTotalFiles();
            } else {
                addLogMessage(`上传失败: ${result.error}`, 'error');
            }
        } catch (error) {
            addLogMessage(`上传错误: ${error.message}`, 'error');
        }
    } else {
        // 前端模拟模式
        audioFiles.forEach(file => {
            if (!uploadedFiles.find(f => f.name === file.name && f.size === file.size)) {
                uploadedFiles.push({
                    name: file.name,
                    size: file.size,
                    path: file.name
                });
                addLogMessage(`已添加文件: ${file.name} (${formatFileSize(file.size)})`, 'success');
            }
        });

        updateFileList();
        updateTotalFiles();
    }
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
async function startProcessing() {
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

    if (USE_BACKEND) {
        // 使用后端处理
        try {
            const response = await fetch(`${API_BASE_URL}/start_processing`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    files: uploadedFiles,
                    max_workers: maxWorkers
                })
            });

            const result = await response.json();
            
            if (result.success) {
                currentJobId = result.job_id;
                addLogMessage(result.message, 'success');
                startStatusMonitoring();
            } else {
                addLogMessage(`启动失败: ${result.error}`, 'error');
                resetProcessingState();
            }
        } catch (error) {
            addLogMessage(`启动错误: ${error.message}`, 'error');
            resetProcessingState();
        }
    } else {
        // 前端模拟模式
        startFrontendProcessing();
    }
}

// 开始状态监控（后端模式）
function startStatusMonitoring() {
    statusInterval = setInterval(async () => {
        if (!currentJobId) return;

        try {
            const response = await fetch(`${API_BASE_URL}/job_status/${currentJobId}`);
            const status = await response.json();

            if (status.error) {
                addLogMessage(`状态获取错误: ${status.error}`, 'error');
                return;
            }

            // 更新进度
            progressFill.style.width = `${status.progress}%`;
            progressLabel.textContent = `进度: ${Math.round(status.progress)}%`;

            // 更新状态
            statusLabel.textContent = `状态: ${getStatusText(status.status)}`;

            // 添加新的日志消息
            if (status.log_messages) {
                status.log_messages.forEach(log => {
                    if (!logContainer.querySelector(`[data-timestamp="${log.timestamp}"]`)) {
                        addLogMessageFromBackend(log);
                    }
                });
            }

            // 检查是否完成
            if (status.status === 'completed' || status.status === 'error' || status.status === 'stopped') {
                clearInterval(statusInterval);
                resetProcessingState();
                
                if (status.status === 'completed') {
                    addLogMessage('所有文件处理完成！', 'success');
                }
            }

        } catch (error) {
            addLogMessage(`状态监控错误: ${error.message}`, 'error');
        }
    }, 1000);
}

// 从后端添加日志消息
function addLogMessageFromBackend(log) {
    const logMessage = document.createElement('div');
    logMessage.className = `log-message ${log.level}`;
    logMessage.setAttribute('data-timestamp', log.timestamp);
    logMessage.textContent = `[${log.timestamp}] ${log.message}`;
    
    logContainer.appendChild(logMessage);
    logContainer.scrollTop = logContainer.scrollHeight;
    
    // 限制日志条数
    if (logContainer.children.length > 1000) {
        logContainer.removeChild(logContainer.firstChild);
    }
}

// 获取状态文本
function getStatusText(status) {
    const statusMap = {
        'pending': '等待中',
        'running': '处理中',
        'paused': '暂停中',
        'completed': '已完成',
        'error': '错误',
        'stopped': '已停止'
    };
    return statusMap[status] || status;
}

// 前端模拟处理
function startFrontendProcessing() {
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

// 开始文件处理（前端模拟）
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

// 处理单个文件（前端模拟）
function processFile(file) {
    const fileName = file.name;
    
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

// 完成处理（前端模拟）
function completeProcessing() {
    clearInterval(processingInterval);
    
    const completionMsg = `所有文件处理完成!\n总共处理了 ${counter} 个文件.`;
    addLogMessage('='.repeat(50), 'success');
    addLogMessage(completionMsg, 'success');
    
    resetProcessingState();
}

// 重置处理状态
function resetProcessingState() {
    isRunning = false;
    currentJobId = null;
    
    // 清理定时器
    if (processingInterval) {
        clearInterval(processingInterval);
        processingInterval = null;
    }
    if (statusInterval) {
        clearInterval(statusInterval);
        statusInterval = null;
    }
    
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
async function togglePause() {
    if (!isRunning) return;
    
    if (USE_BACKEND && currentJobId) {
        // 后端模式
        try {
            const endpoint = pauseProcessing ? 'resume_job' : 'pause_job';
            const response = await fetch(`${API_BASE_URL}/${endpoint}/${currentJobId}`, {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                pauseProcessing = !pauseProcessing;
                updatePauseButton();
                addLogMessage(result.message, 'info');
            } else {
                addLogMessage(`操作失败: ${result.error}`, 'error');
            }
        } catch (error) {
            addLogMessage(`操作错误: ${error.message}`, 'error');
        }
    } else {
        // 前端模拟模式
        pauseProcessing = !pauseProcessing;
        updatePauseButton();
        
        if (pauseProcessing) {
            addLogMessage('Processing paused...', 'warning');
        } else {
            addLogMessage('Processing resumed...', 'info');
        }
    }
}

// 更新暂停按钮
function updatePauseButton() {
    if (pauseProcessing) {
        pauseBtn.textContent = '继续';
        statusLabel.textContent = '状态: 暂停中';
    } else {
        pauseBtn.textContent = '暂停';
        statusLabel.textContent = '状态: 处理中';
    }
}

// 停止处理
async function stopProcessing() {
    if (!isRunning) return;
    
    if (confirm('确定要停止处理吗？\n已经处理的文件将不会丢失。')) {
        if (USE_BACKEND && currentJobId) {
            // 后端模式
            try {
                const response = await fetch(`${API_BASE_URL}/stop_job/${currentJobId}`, {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    addLogMessage(result.message, 'warning');
                } else {
                    addLogMessage(`停止失败: ${result.error}`, 'error');
                }
            } catch (error) {
                addLogMessage(`停止错误: ${error.message}`, 'error');
            }
        } else {
            // 前端模拟模式
            addLogMessage('处理被用户中断', 'warning');
        }
        
        resetProcessingState();
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
    cpuInterval = setInterval(async () => {
        if (USE_BACKEND) {
            try {
                const response = await fetch(`${API_BASE_URL}/system_info`);
                const info = await response.json();
                cpuLabel.textContent = `CPU使用率: ${info.cpu_usage.toFixed(1)}%`;
            } catch (error) {
                // 后端不可用时使用模拟数据
                const cpuUsage = isRunning ? 
                    (Math.random() * 40 + 30).toFixed(1) : 
                    (Math.random() * 10 + 5).toFixed(1);
                cpuLabel.textContent = `CPU使用率: ${cpuUsage}%`;
            }
        } else {
            // 模拟CPU使用率
            const cpuUsage = isRunning ? 
                (Math.random() * 40 + 30).toFixed(1) : 
                (Math.random() * 10 + 5).toFixed(1);
            cpuLabel.textContent = `CPU使用率: ${cpuUsage}%`;
        }
    }, 1000);
}

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
    if (processingInterval) clearInterval(processingInterval);
    if (cpuInterval) clearInterval(cpuInterval);
    if (statusInterval) clearInterval(statusInterval);
    
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
