import boto3
import time

# Konfigurasi AWS
region = 'us-east-2'  # Ganti dengan region Anda
ami_id = 'ami-036841078a4b68e14'  # Ganti dengan AMI ID yang sesuai (misalnya Ubuntu)
instance_type = 't2.nano'  # Tipe instance, ganti sesuai kebutuhan Anda
key_name = 'b'  # Ganti dengan nama key pair yang sudah Anda buat di AWS

# Membuat klien EC2
ec2 = boto3.client('ec2', region_name=region)

# Membuat instance EC2
def create_ec2_instance():
    response = ec2.run_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        KeyName=key_name,
        SecurityGroupIds=['sg-0d5375df498ebea00'],  # Ganti dengan ID security group Anda
        UserData='''#!/bin/bash
                    sudo apt-get update -y
                    sudo apt-get install -y squid
                    sudo systemctl start squid
                    sudo systemctl enable squid
                    sudo ufw allow 3128/tcp
                    sudo ufw reload
                    echo "http_port 3128" | sudo tee -a /etc/squid/squid.conf
                    # Mengubah http_access untuk mengizinkan semua akses
                    echo "http_access allow all" | sudo tee -a /etc/squid/squid.conf
                    # Menghapus baris http_access deny all yang mungkin ada sebelumnya
                    sudo sed -i '/http_access deny all/d' /etc/squid/squid.conf
                    sudo systemctl restart squid
                    ''',  # UserData untuk instalasi dan konfigurasi Squid Proxy
        TagSpecifications=[ 
            {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': 'Proxy-Server'}
                ]
            }
        ]
    )

    instance_id = response['Instances'][0]['InstanceId']
    print(f'Instance {instance_id} sedang dibuat...')
    return instance_id

# Menunggu instance untuk siap
def wait_for_instance(instance_id):
    print("Menunggu instance untuk siap...")
    ec2.get_waiter('instance_running').wait(InstanceIds=[instance_id])
    print(f'Instance {instance_id} sudah berjalan.')

# Menampilkan alamat IP publik instance
def get_instance_ip(instance_id):
    instance = ec2.describe_instances(InstanceIds=[instance_id])
    public_ip = instance['Reservations'][0]['Instances'][0]['PublicIpAddress']
    return public_ip

# Menjalankan semua langkah
def main():
    instance_id = create_ec2_instance()
    wait_for_instance(instance_id)
    public_ip = get_instance_ip(instance_id)
    print(f'Proxy Server Anda dapat diakses di: http://{public_ip}:3128')

if __name__ == "__main__":
    main()
