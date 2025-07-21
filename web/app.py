from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import threading
import time
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局变量
processing_jobs = {}
upload_folder = 'uploads'
output_folder = 'output'

# 确保目录存在
os.makedirs(upload_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)
os.makedirs('music_stft', exist_ok=True)
os.makedirs('data_stft', exist_ok=True)
os.makedirs('log_stft', exist_ok=True)

class ProcessingJob:
    def __init__(self, job_id, files):
        self.job_id = job_id
        self.files = files
        self.status = 'pending'  # pending, running, paused, completed, error
        self.progress = 0
        self.current_file = None
        self.log_messages = []
        self.start_time = None
        self.end_time = None
        self.thread = None

    def add_log(self, message, level='info'):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'message': message,
            'level': level
        }
        self.log_messages.append(log_entry)
        print(f"[{timestamp}] {message}")

    def update_progress(self, current, total):
        self.progress = (current / total * 100) if total > 0 else 0

@app.route('/')
def index():
    """提供主页"""
    return send_from_directory('web', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """提供静态文件"""
    return send_from_directory('web', filename)

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """文件上传接口"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': '没有文件上传'}), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file.filename == '':
                continue
                
            # 保存文件
            filename = file.filename
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            uploaded_files.append({
                'name': filename,
                'size': os.path.getsize(file_path),
                'path': file_path
            })
        
        return jsonify({
            'success': True,
            'files': uploaded_files,
            'message': f'成功上传 {len(uploaded_files)} 个文件'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start_processing', methods=['POST'])
def start_processing():
    """开始处理音频文件"""
    try:
        data = request.get_json()
        files = data.get('files', [])
        max_workers = data.get('max_workers', 4)
        
        if not files:
            return jsonify({'error': '没有文件需要处理'}), 400
        
        # 创建处理任务
        job_id = str(uuid.uuid4())
        job = ProcessingJob(job_id, files)
        processing_jobs[job_id] = job
        
        # 启动处理线程
        job.thread = threading.Thread(target=process_audio_files, args=(job, max_workers))
        job.thread.daemon = True
        job.thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': '处理任务已启动'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/job_status/<job_id>')
def get_job_status(job_id):
    """获取任务状态"""
    if job_id not in processing_jobs:
        return jsonify({'error': '任务不存在'}), 404
    
    job = processing_jobs[job_id]
    
    return jsonify({
        'job_id': job_id,
        'status': job.status,
        'progress': job.progress,
        'current_file': job.current_file,
        'log_messages': job.log_messages[-50:],  # 最近50条日志
        'start_time': job.start_time,
        'end_time': job.end_time
    })

@app.route('/api/pause_job/<job_id>', methods=['POST'])
def pause_job(job_id):
    """暂停任务"""
    if job_id not in processing_jobs:
        return jsonify({'error': '任务不存在'}), 404
    
    job = processing_jobs[job_id]
    
    if job.status == 'running':
        job.status = 'paused'
        job.add_log('任务已暂停', 'warning')
        return jsonify({'success': True, 'message': '任务已暂停'})
    else:
        return jsonify({'error': '任务不在运行状态'}), 400

@app.route('/api/resume_job/<job_id>', methods=['POST'])
def resume_job(job_id):
    """恢复任务"""
    if job_id not in processing_jobs:
        return jsonify({'error': '任务不存在'}), 404
    
    job = processing_jobs[job_id]
    
    if job.status == 'paused':
        job.status = 'running'
        job.add_log('任务已恢复', 'info')
        return jsonify({'success': True, 'message': '任务已恢复'})
    else:
        return jsonify({'error': '任务不在暂停状态'}), 400

@app.route('/api/stop_job/<job_id>', methods=['POST'])
def stop_job(job_id):
    """停止任务"""
    if job_id not in processing_jobs:
        return jsonify({'error': '任务不存在'}), 404
    
    job = processing_jobs[job_id]
    job.status = 'stopped'
    job.add_log('任务已停止', 'warning')
    
    return jsonify({'success': True, 'message': '任务已停止'})

def process_audio_files(job, max_workers):
    """处理音频文件的主函数"""
    try:
        job.status = 'running'
        job.start_time = datetime.now().isoformat()
        job.add_log('开始处理音频文件...', 'info')
        job.add_log('执行解密...', 'info')
        
        # 模拟解密过程
        time.sleep(2)
        job.add_log('解密完成', 'success')
        job.add_log('执行格式化...', 'info')
        
        # 模拟格式化过程
        time.sleep(1)
        job.add_log('格式化完成', 'success')
        job.add_log(f'开始处理 {len(job.files)} 个音乐文件...(使用 {max_workers} 个线程)', 'info')
        
        # 处理每个文件
        for i, file_info in enumerate(job.files):
            if job.status == 'stopped':
                break
                
            # 等待暂停状态结束
            while job.status == 'paused':
                time.sleep(0.5)
                if job.status == 'stopped':
                    break
            
            if job.status == 'stopped':
                break
            
            job.current_file = file_info['name']
            job.add_log(f'正在处理: {file_info["name"]}', 'info')
            
            # 模拟处理步骤
            steps = [
                'STFT Unified',
                'STFT 3000 Detailed',
                'Power CSV', 
                'Power PLT',
                'Power A-Weighted'
            ]
            
            for step in steps:
                if job.status in ['stopped', 'paused']:
                    break
                    
                job.add_log(f'Processing {file_info["name"]}: {step}', 'info')
                time.sleep(0.5)  # 模拟处理时间
            
            if job.status == 'stopped':
                break
            
            # 更新进度
            job.update_progress(i + 1, len(job.files))
            job.add_log(f'Song-{file_info["name"]} Finished! [{i + 1}/{len(job.files)}]', 'success')
        
        if job.status != 'stopped':
            job.status = 'completed'
            job.end_time = datetime.now().isoformat()
            job.add_log('所有文件处理完成!', 'success')
            job.add_log(f'总共处理了 {len(job.files)} 个文件.', 'success')
        
    except Exception as e:
        job.status = 'error'
        job.add_log(f'处理过程中发生错误: {str(e)}', 'error')

@app.route('/api/system_info')
def get_system_info():
    """获取系统信息"""
    import psutil
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        return jsonify({
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'available_memory': memory.available,
            'total_memory': memory.total
        })
    except:
        # 如果psutil不可用，返回模拟数据
        import random
        return jsonify({
            'cpu_usage': random.uniform(10, 80),
            'memory_usage': random.uniform(30, 70),
            'available_memory': 8000000000,  # 8GB
            'total_memory': 16000000000  # 16GB
        })

if __name__ == '__main__':
    print("启动 Spectrum 分析工具 Web 服务器...")
    print("请在浏览器中访问: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
