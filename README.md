RUN : 

pip3 install boto3
python create_proxy_server.py


sudo systemctl restart squid

sudo systemctl start squid
sudo systemctl status squid
