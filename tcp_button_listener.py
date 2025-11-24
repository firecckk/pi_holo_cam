import socket
import re
import threading
import time

# 配置
HOST = '0.0.0.0'  # 监听所有可用接口
PORT = 5555       # 监听的端口
BUFFER_SIZE = 1024 # 接收缓冲区大小

# 正则表达式用于匹配和提取 'code' 的值
# 它查找 "BUTTON:code=数字,action=PRESS" 模式
PATTERN = re.compile(r'BUTTON:code=(\d+),action=PRESS')

def handle_client(conn, addr, button_callback):
    """
    处理单个客户端连接的函数
    """
    #print(f"✅ 客户端 {addr} 已连接。开始监听数据...")
    
    try:
        while True:
            # 接收数据
            data = conn.recv(BUFFER_SIZE)
            if not data:
                # 如果接收到空数据，表示客户端关闭了连接
                break
            
            # 将接收到的字节流解码成字符串
            message = data.decode('utf-8').strip()
            print(f"⬅️ 接收自 {addr}: {message!r}")

            # 由于 nc -l 发送的数据可能一次性包含多行事件，我们按行分割
            lines = message.split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 使用正则表达式匹配
                match = PATTERN.search(line)
                
                if match:
                    # 提取 code 组（匹配到的数字）
                    code = match.group(1)
                    
                    # 发送转换后的数字字节流
                    button_callback(code)
                    print(f"➡️ {addr}: 转换按键 {code}")
                
    except ConnectionResetError:
        print(f"⚠️ 客户端 {addr} 异常断开。")
    except Exception as e:
        print(f"❌ 处理客户端 {addr} 时发生错误: {e}")
    finally:
        # 关闭连接
        #print(f"🔌 客户端 {addr} 连接已关闭。")
        conn.close()

def start_server(button_callback):
    """
    启动 TCP 服务器的主函数
    """
    # 创建一个 TCP/IP 套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 设置 SO_REUSEADDR 选项，允许立即重新使用地址（防止重启时报 Address already in use）
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # 绑定到指定的地址和端口
        server_socket.bind((HOST, PORT))
        
        # 开始监听连接，最多允许 5 个排队连接
        server_socket.listen(5)
        
        print(f"📡 TCP 服务器已启动，正在监听 {HOST}:{PORT}...")
        
        while True:
            # 等待连接
            conn, addr = server_socket.accept()
            
            # 为每个新连接启动一个新线程，以支持并发处理
            client_thread = threading.Thread(target=handle_client, args=(conn, addr, button_callback))
            client_thread.start()
            
    except Exception as e:
        print(f"\n❌ 服务器启动失败或运行时发生致命错误: {e}")
    finally:
        # 清理和关闭服务器套接字
        server_socket.close()
        print("服务器已关闭。")
