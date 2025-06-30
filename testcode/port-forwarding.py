from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from urllib.parse import parse_qs, urlparse
import json
import sys


class URLFetcherHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求，从query参数中获取URL并访问"""
        # 解析URL查询参数
        query_components = parse_qs(urlparse(self.path).query)

        if 'url' in query_components:
            url = query_components['url'][0]
            self.fetch_and_respond(url)
        else:
            # 没有提供URL参数，显示表单
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()

            form = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>URL获取器</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    input[type="text"] { width: 300px; padding: 5px; }
                    input[type="submit"] { padding: 5px 10px; }
                </style>
            </head>
            <body>
                <h2>输入URL获取内容</h2>
                <form method="get">
                    <input type="text" name="url" placeholder="https://example.com">
                    <input type="submit" value="获取">
                </form>
            </body>
            </html>
            '''
            self.wfile.write(form.encode())

    def do_POST(self):
        """处理POST请求，从请求体中获取URL并访问"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(post_data)
            if 'url' in data:
                url = data['url']
                self.fetch_and_respond(url)
            else:
                self.send_error_response(400, "请求中未提供URL")
        except json.JSONDecodeError:
            self.send_error_response(400, "无效的JSON格式")

    def fetch_and_respond(self, url):
        """访问指定URL并将结果返回给客户端"""
        try:
            # 如果URL没有协议前缀，添加http://
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url

            # 访问URL
            print(f"正在获取URL: {url}")
            response = requests.get(url, timeout=10)

            # 获取内容类型
            content_type = response.headers.get('Content-Type', 'text/plain')

            # 设置响应
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()

            # 返回获取的内容
            self.wfile.write(response.content)

        except requests.exceptions.RequestException as e:
            self.send_error_response(500, f"获取URL时出错: {str(e)}")
        except Exception as e:
            self.send_error_response(500, f"服务器错误: {str(e)}")

    def send_error_response(self, status_code, message):
        """发送错误响应"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        error_response = json.dumps({"error": message})
        self.wfile.write(error_response.encode())


def run_server(port=8000):
    """启动HTTP服务器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, URLFetcherHandler)
    print(f"服务器已启动，监听端口 {port}")
    print(f"请在浏览器中访问 http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已关闭")
        httpd.server_close()


if __name__ == '__main__':
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"无效端口: {sys.argv[1]}")
            sys.exit(1)

    run_server(port)