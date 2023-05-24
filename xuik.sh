#!/bin/bash

# 检查是否已安装依赖包
if ! command -v nginx &> /dev/null
then
    echo "检测到您未安装nginx，即将为您安装nginx..."
    apt-get update
    apt-get install -y nginx
fi

if ! command -v acme.sh &> /dev/null
then
    echo "SSL证书助手未安装，即将为您安装..."
    curl https://get.acme.sh | sh
fi

# 安装x-ui
install_xui() {
    echo "即将安装X-UI面板..."
    curl -sSL https://raw.githubusercontent.com/vaxilu/x-ui/master/install.sh | bash
    echo "已结束，请立即登录Web控制台修改您的面板自定义路径"
}

# x-ui面板域名配置
panel_config() {
    read -p "请输入面板端口：" panel_port
    read -p "请输入面板自定义入口路径（不带斜杠）：" panel_path
    read -p "请输入域名：" domain_name

    echo "
    location ^~ /$panel_path {
        proxy_pass http://127.0.0.1:$panel_port/$panel_path;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    " > /etc/nginx/sites-enabled/$domain_name

    # 申请SSL证书
    acme.sh --issue -d $domain_name --nginx

    echo "
    server {
        listen       80;
        server_name  $domain_name;
        return 301 https://\$server_name\$request_uri;
    }
    server {
        listen              443 ssl;
        server_name         $domain_name;
        ssl_certificate     /root/.acme.sh/$domain_name/fullchain.cer;
        ssl_certificate_key /root/.acme.sh/$domain_name/$domain_name.key;

        location ^~ /$panel_path {
            proxy_pass http://127.0.0.1:$panel_port/$panel_path;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
    " > /etc/nginx/sites-enabled/$domain_name

    # 重启nginx
    systemctl restart nginx

    # 结束输出
    echo -e "\033[1;32m已完成 现在您可以通过 https://$domain_name/$panel_path 来访问您的x-ui面板了\033[0m"
}

# x-ui节点域名配置
node_config() {
    read -p "请输入节点端口：" node_port
    read -p "请输入节点路径（不带斜杠）：" node_path
    read -p "请输入域名：" domain_name

    echo "
    location /$node_path {
        proxy_pass http://127.0.0.1:$node_port;
        proxy_http_version 1.1;
        proxy_set_header Host \$http_host;
        proxy_set_header Upgrade \$http_upgarde;
        proxy_set_header Connection \"upgrade\";
        proxy_read_timeout 300s;
        # Show realip in v2ray access.log
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
    " > /etc/nginx/sites-enabled/$domain_name

    # 申请SSL证书
    acme.sh --issue -d $domain_name --nginx

    echo "
    server {
        listen       80;
        server_name  $domain_name;
        return 301 https://\$server_name\$request_uri;
    }
    server {
        listen              443 ssl;
        server_name         $domain_name;
        ssl_certificate     /root/.acme.sh/$domain_name/fullchain.cer;
        ssl_certificate_key /root/.acme.sh/$domain_name/$domain_name.key;

        location /$node_path {
            proxy_pass http://127.0.0.1:$node_port;
            proxy_http_version 1.1;
            proxy_set_header Host \$http_host;
            proxy_set_header Upgrade \$http_upgarde;
            proxy_set_header Connection \"upgrade\";
            proxy_read_timeout 300s;
            # Show realip in v2ray access.log
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        }
    }
    " > /etc/nginx/sites-enabled/$domain_name

    # 重启nginx
    systemctl restart nginx

    # 高亮显示公钥及密钥路径
    echo -e "\033[1;32m已完成，请在web控制台添加节点并配置tls，\nSSL证书已部署\n公钥路径：/root/.acme.sh/$domain_name/fullchain.cer\n密钥路径：/root/.acme.sh/$domain_name/$domain_name.key\033[0m"
}

# 提供选项供用户选择
while true; do
    read -p "请选择要进行的操作：1.安装x-ui 2.x-ui面板域名配置 3.x-ui节点域名配置 " option
    case $option in
        1)
            install_xui
            break;;
        2)
            panel_config
            break;;
        3)
            node_config
            break;;
        *)
            echo "无效的选项，请重新选择："
            continue;;
    esac
done
