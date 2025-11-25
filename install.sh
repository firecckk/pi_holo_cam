# 安装服务脚本
sudo cp ./pi_holo_cam.service /etc/systemd/system/pi_holo_cam.service

# 重新加载systemd配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable pi_holo_cam.service

# 启动服务
sudo systemctl start pi_holo_cam.service

# 检查状态
sudo systemctl status pi_holo_cam.service
