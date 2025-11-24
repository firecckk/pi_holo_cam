import socket
import re
import threading
from PyQt6.QtCore import Qt

# 配置
HOST = '0.0.0.0'
PORT = 5555
BUFFER_SIZE = 1024

PATTERN = re.compile(r'BUTTON:code=(\d+),action=PRESS')

# 按键码映射（从数字映射到 Qt.Key）
CODE_TO_KEY = {
    '7': Qt.Key.Key_Up,
    '9': Qt.Key.Key_Down,
    '8': Qt.Key.Key_Return
}

def handle_client(conn, addr, input_listener):
    """处理单个客户端连接"""
    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            
            message = data.decode('utf-8').strip()
            #print(f"⬅️ 接收自 {addr}: {message!r}")

            lines = message.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                match = PATTERN.search(line)
                if match:
                    code = match.group(1)
                    # 转换为 Qt 按键码并发送
                    if code in CODE_TO_KEY:
                        key_code = CODE_TO_KEY[code]
                        input_listener.emit_key(key_code)
                        print(f"➡️ {addr}: 按键 {code} -> {key_code}")
                
    except ConnectionResetError:
        print(f"⚠️ 客户端 {addr} 异常断开。")
    except Exception as e:
        print(f"❌ 处理客户端 {addr} 时发生错误: {e}")
    finally:
        conn.close()

def start_tcp_server(input_listener):
    """启动 TCP 服务器"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"📡 TCP 服务器已启动，正在监听 {HOST}:{PORT}...")
        
        while True:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client, 
                args=(conn, addr, input_listener),
                daemon=True
            )
            client_thread.start()
            
    except Exception as e:
        print(f"❌ 服务器错误: {e}")
    finally:
        server_socket.close()

def thread_run(input_listener):
    tcp_thread = threading.Thread(
        target=start_tcp_server,
        args=(input_listener,),
        daemon=True
    )
    tcp_thread.start()
    print("✓ TCP 服务器已启动")