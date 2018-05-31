#!/usr/bin/env python3

import os
import subprocess
import boto3
from botocore.exceptions import ClientError
from colorama import init, Fore

def rotate_keypair():

    """Automates AWS EC2 key pair rotation.

    Generates EC2 key pair, downloads private key and adds passphrase, adds
    passphrase to ssh-agent and OS keychain, regenerates public key and pushes
    to EC2 instance, creates/updates SSH alias, tests remote access with new
    key pair, removes old EC2 key pair and private key from local disk.
    """

    # initial EC2 defaults (update these with EC2 instance values)
    ec2_ip = '54.193.18.195'    # public IP address or public DNS
    ec2_key = 'dev_key.pem'     # current private key
    ec2_user = 'ec2-user'       # default AMI user
    ec2_port = '22'             # SSH port number

    # key pair rotation defaults
    key_path = '~/.ssh/'
    key_path = os.path.expanduser(key_path)
    key_name = 'dev_key' # base name of private key
    prv_key = key_name + '.pem'
    pub_key = key_name + '.pub'
    ssh_host = 'dev' # name of SSH alias
    ssh_host_tmp = ssh_host +'_tmp' # name of tmp SSH alias
    ssh_cfg = key_path + 'config.d/' + ssh_host
    last_host_key = '54.193.18.195' # don't edit, it's autopopulated!

    # initial ssh connection string
    ec2_ssh_str = key_path + ec2_key + ' ' + ec2_user + '@' + ec2_ip

    # colorama: automatically reset style after each call
    init(autoreset=True)
    ck = Fore.CYAN + ' \N{heavy check mark}'

`    ec2 = boto3.client('ec2')

    try:
        print('\n=> Checking for existing EC2 key pair: ' + key_name + ck)
        ec2.describe_key_pairs(KeyNames=[key_name])
    except ClientError as err:
        if err.response["Error"]["Code"] == "InvalidKeyPair.NotFound":
            gen_msg = '   Not Found! Generating a new key pair: '
    else:
        gen_msg = '   Found! Generating a replacement key pair: '
        ec2.delete_key_pair(KeyName=key_name)
`
    print('\n' + Fore.CYAN + gen_msg + key_name)
    keypair = ec2.create_key_pair(KeyName=key_name)

    print('\n=> Checking for existing private key: ' + key_path + prv_key + ck)
    if os.path.isfile(key_path + prv_key):
        down_msg = '\n   Found! Downloading replacement: '
        prv_key = 'tmp.' + prv_key
    else:
        down_msg = '\n   Not Found! Downloading new: '

    print(Fore.CYAN + down_msg + key_path + prv_key)
    # check for/make default SSH directory with octal mode permission syntax
    if not os.path.isdir(key_path):
        os.mkdir(key_path, 0o700)
    # check for/remove tmp private key from failed rotation
    if os.path.isfile(key_path + prv_key):
        os.remove(key_path + prv_key)
    with open(
        key_path + prv_key,'w+') as key:
        key.write(keypair['KeyMaterial'])

    # temporarily tighten file perms; needed for encryption and public key gen
    os.chmod(key_path + prv_key, 0o600)

    print('\n=> Generating public key' + ck)
    subprocess.run('ssh-keygen -y -f ' + key_path + prv_key + ' > ' \
        + key_path + pub_key, shell=True)

    print('=> Adding host key to ' + key_path + 'known_hosts' + ck)
    if last_host_key in open(key_path + 'known_hosts').read():
        print('=> Also found prior host key... removing' + ck)
        subprocess.run('ssh-keygen -R ' + last_host_key + \
            '&>/dev/null', shell=True)
    subprocess.run('ssh -o StrictHostKeyChecking=no -tt -i ' + ec2_ssh_str + \
        ' exit &>/dev/null', shell=True)

    print('=> Pushing public key to EC2 instance\'s authorized_keys' + ck)
    subprocess.run('cat ' + key_path + pub_key + ' | ssh -i ' + ec2_ssh_str + \
        ' "sudo tee -a ~/.ssh/authorized_keys > /dev/null"', shell=True)

    print('=> Removing public key from local disk' + ck)
    os.remove(key_path + pub_key)

    print('=> Encrypting private key with passphrase' + ck + '\n')
    subprocess.run('ssh-keygen -p -f ' + key_path + prv_key + \
        ' &>/dev/null', shell=True)

    print('\n=> Busting ssh-agent cache' + ck)
    subprocess.run('/usr/bin/ssh-add -DK &>/dev/null', shell=True)

    print('=> Adding new passphrase to ssh-agent & keychain' + ck + '\n')
    subprocess.run('/usr/bin/ssh-add -K ' + key_path + prv_key, shell=True)

    print('\n=> Setting file permissions on private key to 400' + ck)
    os.chmod(key_path + prv_key, 0o400)

    print('=> Checking for existing SSH alias: ' + ssh_cfg + ck)
    if os.path.isfile(ssh_cfg):
        create_msg = '\n   Found! Creating replacement: '
        ssh_cfg = ssh_cfg + '_tmp'
    else:
        create_msg = '\n  Not Found! Creating new: '

    # create custom SSH config directory if not already exist
    if not os.path.isdir(key_path + 'config.d/'):
        os.mkdir(key_path + 'config.d/', 0o700)

    # Prepend an include directive to default SSH config
    with open(key_path + 'config', 'r+') as config:
        first_line = config.readline()
        if first_line != 'Include config.d/*\n':
            lines = config.readlines()
            config.seek(0)
            config.write('Include config.d/*\n')
            config.write(first_line)
            config.writelines(lines)

    print(Fore.CYAN + create_msg + ssh_cfg)
    with open(ssh_cfg, "w") as config:
        txt_lines = [
        'Host '+ ssh_host + '_tmp',
        '\n   HostName ' + ec2_ip,
        '\n   User ' + ec2_user,
        '\n   Port ' + ec2_port,
        '\n   IdentityFile ' + key_path + prv_key,
        ]
        config.writelines(txt_lines)

    print('\n=> Setting file permissions on SSH alias to 600' + ck)
    os.chmod(ssh_cfg, 0o600)

    print('=> Testing remote access to EC2 instance using new key pair' + ck)
    try:
        subprocess.run(['ssh', ssh_host_tmp, 'exit'],
            check=True,
            universal_newlines=True,
            stderr=subprocess.PIPE
        )

    except subprocess.CalledProcessError as err:
        print(Fore.RED + '\n' + err.stderr)
    else:
        print(Fore.CYAN + '\n   Successfully connected to EC2 instance with '
            'new key pair!\n')

        print('=> Clearing stale keys in EC2 instance\'s authorized_keys' + ck)
        # get line count, subtract 1, then delete remaining line range
        cmd = 'file="$HOME/.ssh/authorized_keys" \
            && num=$(wc -l < $file) \
            && num=$((num-1)) \
            && [[ $num -gt 1 ]] \
            && sed -i "1,$num d" $file'
        subprocess.run(['ssh', ssh_host, cmd])

        prv_key = key_name + '.pem'

        if os.path.isfile(key_path + 'config.d/' + ssh_host + '_tmp'):
            print('=> Removing prior SSH alias config'+ ck)
            os.remove(key_path + 'config.d/' + ssh_host)

            ssh_cfg = key_path + 'config.d/' + ssh_host
            print('=> Renaming new SSH alias config to ' + ssh_cfg + ck)
            os.rename(ssh_cfg + '_tmp', ssh_cfg)

        print('=> Updating Host & IdentityFile values in ' + ssh_cfg + ck)
        with open(ssh_cfg) as config:
            sub = (config.read()
                .replace('tmp.' + prv_key, prv_key)
                .replace(ssh_host + '_tmp', ssh_host)
            )
        with open(ssh_cfg, "w") as config:
            config.write(sub)

        if ec2_key != prv_key:
            print('=> Removing initial private key (local & EC2)' + ck)
            os.remove(key_path + ec2_key)
            ec2_keypair = os.path.splitext(ec2_key)[0]  # strip file extention
            ec2.delete_key_pair(KeyName=ec2_keypair)

        if os.path.isfile(key_path + 'tmp.' + prv_key):
            print('=> Removing old private key '+ prv_key + ck)
            os.remove(key_path + prv_key)

            print('=> Renaming new private key to ' + key_path + prv_key + ck)
            os.rename(key_path + 'tmp.' + prv_key, key_path + prv_key)

        print('=> Updating script\'s default values' + ck)
        with open('keypair.py') as file:
            sub = (file.read()
                .replace(ec2_key, prv_key)
                .replace(last_host_key, ec2_ip))
        with open('keypair.py', "w") as file:
            file.write(sub)

        print(Fore.CYAN + '\n**** EC2 key pair rotation complete... '
            'try it: $ ssh dev ****')

if __name__ == '__main__':
    rotate_keypair()
