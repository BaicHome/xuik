#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import subprocess
import os


class GUI:
    def __init__(self, window):
        self.window = window
        self.window.title("X-UI 部署脚本")
        self.window.geometry("500x400")

        # 定义所需变量
        self.has_nginx = False
        self.has_acme = False
        self.panel_port = tk.IntVar()
        self.panel_path = tk.StringVar()
        self.domain_name_panel = tk.StringVar()
        self.node_port = tk.IntVar()
        self.node_path = tk.StringVar()
        self.domain_name_node = tk.StringVar()

        # 定义各个组件
        self.label_title = ttk.Label(text="欢迎使用 X-UI 部署脚本", font=("Arial Bold", 20))
        self.label_desc = ttk.Label(text="本脚本将帮助您自动安装依赖并部署 X-UI 面板和节点，同时为您申请 SSL 证书。", font=("Arial", 12))
        self.label_step1 = ttk.Label(text="第一步：检查依赖安装情况", font=("Arial", 16, "underline"))
        self.label_nginx = ttk.Label(text="Nginx 未安装", foreground="red")
        self.label_acme = ttk.Label(text="SSL 证书助手未安装", foreground="red")
        self.label_step2 = ttk.Label(text="第二步：安装 X-UI 面板", font=("Arial", 16, "underline"))
        self.button_install_xui = ttk.Button(text="安装 X-UI 面板", command=self.install_xui)
        self.label_step3 = ttk.Label(text="第三步：X-UI 面板域名配置", font=("Arial", 16, "underline"))
        self.label_panel_port = ttk.Label(text="面板端口：")
        self.entry_panel_port = ttk.Entry(textvariable=self.panel_port)
        self.label_panel_path = ttk.Label(text="面板自定义入口路径：")
        self.entry_panel_path = ttk.Entry(textvariable=self.panel_path)
        self.label_domain_name_panel = ttk.Label(text="域名：")
        self.entry_domain_name_panel = ttk.Entry(textvariable=self.domain_name_panel)
        self.button_panel_config = ttk.Button(text="完成配置", command=self.panel_config)
        self.label_step4 = ttk.Label(text="第四步：X-UI 节点域名配置", font=("Arial", 16, "underline"))
        self.label_node_port = ttk.Label(text="节点端口：")
        self.entry_node_port = ttk.Entry(textvariable=self.node_port)
        self.label_node_path = ttk.Label(text="节点自定义路径：")
        self.entry_node_path = ttk.Entry(textvariable=self.node_path)
        self.label_domain_name_node = ttk.Label(text="域名：")
        self.entry_domain_name_node = ttk.Entry(textvariable=self.domain_name_node)
        self.button_node_config = ttk.Button(text="完成配置", command=self.node_config)

        # 定义组件位置
        self.label_title.place(x=50, y=20)
        self.label_desc.place(x=50, y=80)
        self.label_step1.place(x=50, y=120)
        self.label_nginx.place(x=50, y=160)
        self.label_acme.place(x=50, y=180)
        self.label_step2.place(x=50, y=220)
        self.button_install_xui.place(x=50, y=260)
        self.label_step3.place(x=50, y=300)
        self.label_panel_port.place(x=50, y=340)
        self.entry_panel_port.place(x=200, y=340)
        self.label_panel_path.place(x=50, y=380)
        self.entry_panel_path.place(x=200, y=380)
        self.label_domain_name_panel.place(x=50, y=420)
        self.entry_domain_name_panel.place(x=200, y=420)
        self.button_panel_config.place(x=200, y=460)
        self.label_step4.place(x=50, y=500)
        self.label_node_port.place(x=50, y=540)
        self.entry_node_port.place(x=200, y=540)
        self.label_node_path.place(x=50, y=580)
        self.entry_node_path.place(x=200, y=580)
        self.label_domain_name_node.place(x=50, y=620)
        self.entry_domain_name_node.place(x=200, y=620)
        self.button_node_config.place(x=200, y=660)

        # 检查依赖安装情况
        self.check_dependencies()

    def check_dependencies(self):
        if os.system('nginx -v') == 0:
            self.has_nginx = True
            self.label_nginx.config(text="Nginx 已安装", foreground="green")

        if os.system('acme.sh --version') == 0:
            self.has_acme = True
            self.label_acme.config(text="SSL 证书助手已安装", foreground="green")

    def install_xui(self):
        if messagebox.askquestion("安装确认", "X-UI 面板将会被安装在您的系统中，是否继续？") == 'yes':
            subprocess.call(['bash', '-c', 'curl -sSL https://raw.githubusercontent.com/vaxilu/x-ui/master/install.sh | bash'])
            messagebox.showinfo("安装完成", "X-UI 面板安装已完成，请登录 Web 控制台修改您的面板自定义路径。")

    def panel_config(self):
        panel_port = self.panel_port.get()
        panel_path = self.panel_path.get()
        domain_name = self.domain_name_panel.get()

        if not panel_port or not panel_path or not domain_name:
            messagebox.showwarning("错误", "请填写完整配置信息")
            return

        # 检查是否安装了 nginx 和 acme.sh
        if not self.has_nginx:
            subprocess.call(['bash', '-c', 'apt-get update && apt-get install -y nginx'])
            self.has_nginx = True
            self.label_nginx.config(text="Nginx 已安装", foreground="green")

        if not self.has_acme:
            subprocess.call(['bash', '-c', 'curl https://get.acme.sh | sh'])
            self.has_acme = True
            self.label_acme.config(text="SSL 证书助手已安装", foreground="green")

        # 创建配置文件
        with open(f'/etc/nginx/sites-enabled/{domain_name}', 'w') as f:
            config = f"""
            location ^~ /{panel_path}/ {{
                proxy_pass http://127.0.0.1:{panel_port}/{panel_path}/;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            }}
            """
            f.write(config)

        # 申请 SSL 证书
        subprocess.call(['bash', '-c', f'acme.sh --issue -d {domain_name} --nginx'])

        # 写入 nginx 配置
        with open(f'/etc/nginx/sites-enabled/{domain_name}', 'w') as f:
            config = f"""
            server {{
                listen       80;
                server_name  {domain_name};
                return 301 https://$server_name$request_uri;
            }}
            server {{
                listen              443 ssl;
                server_name         {domain_name};
                ssl_certificate     /root/.acme.sh/{domain_name}/fullchain.cer;
                ssl_certificate_key /root/.acme.sh/{domain_name}/{domain_name}.key;

                location ^~ /{panel_path}/ {{
                    proxy_pass http://127.0.0.1:{panel_port}/{panel_path}/;
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                }}
            }}
            """
            f.write(config)

        # 重启 nginx
        subprocess.call(['bash', '-c', 'systemctl restart nginx'])

        # 完成提示
        messagebox.showinfo("配置完成", f"X-UI 面板域名配置已完成，请访问 https://{domain_name}/{panel_path}/ 访问您的面板。")

    def node_config(self):
        node_port = self.node_port.get()
        node_path = self.node_path.get()
        domain_name = self.domain_name_node.get()

        if not node_port or not node_path or not domain_name:
            messagebox.showwarning("错误", "请填写完整配置信息")
            return

        # 检查是否安装了 nginx 和 acme.sh
        if not self.has_nginx:
            subprocess.call(['bash', '-c', 'apt-get update && apt-get install -y nginx'])
            self.has_nginx = True
            self.label_nginx.config(text="Nginx 已安装", foreground="green")

        if not self.has_acme:
            subprocess.call(['bash', '-c', 'curl https://get.acme.sh | sh'])
            self.has_acme = True
            self.label_acme.config(text="SSL 证书助手已安装", foreground="green")

        # 创建配置文件
        with open(f'/etc/nginx/sites-enabled/{domain_name}', 'w') as f:
            config = f"""
            location /{node_path}/ {{
                proxy_pass http://127.0.0.1:{node_port}/;
                proxy_http_version 1.1;
                proxy_set_header Host $http_host;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
                proxy_read_timeout 300s;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            }}
            """
            f.write(config)

        # 申请 SSL 证书
        subprocess.call(['bash', '-c', f'acme.sh --issue -d {domain_name} --nginx'])

        # 写入 nginx 配置
        with open(f'/etc/nginx/sites-enabled/{domain_name}', 'w') as f:
            config = f"""
            server {{
                listen       80;
                server_name  {domain_name};
                return 301 https://$server_name$request_uri;
            }}
            server {{
                listen              443 ssl;
                server_name         {domain_name};
                ssl_certificate     /root/.acme.sh/{domain_name}/fullchain.cer;
                ssl_certificate_key /root/.acme.sh/{domain_name}/{domain_name}.key;

                location /{node_path}/ {{
                    proxy_pass http://127.0.0.1:{node_port}/;
                    proxy_http_version 1.1;
                    proxy_set_header Host $http_host;
                    proxy_set_header Upgrade $http_upgrade;
                    proxy_set_header Connection "upgrade";
                    proxy_read_timeout 300s;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                }}
            }}
            """
            f.write(config)

        # 重启 nginx
        subprocess.call(['bash', '-c', 'systemctl restart nginx'])

        # 完成提示
        messagebox.showinfo("配置完成", f"X-UI 节点域名配置已完成，请在 Web 控制台添加节点并配置 TLS。"
                                        f"\n公钥路径：/root/.acme.sh/{domain_name}/fullchain.cer"
                                        f"\n密钥路径：/root/.acme.sh/{domain_name}/{domain_name}.key")


if __name__ == '__main__':
    window = tk.Tk()
    gui = GUI(window)
    window.mainloop()

