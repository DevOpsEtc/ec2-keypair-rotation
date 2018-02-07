#!/usr/bin/env python3

import os
import subprocess
import boto3
from botocore.exceptions import ClientError

def rotate_keypair():

    """Automates AWS EC2 key pair rotation.

    Generates EC2 key pair, downloads private key and adds passphrase, adds
    passphrase to ssh-agent and OS keychain, regenerates public key and pushes
    to EC2 instance, creates/updates SSH alias, tests remote access with new
    key pair, removes old EC2 key pair and private key from local disk.
    """

    # key pair rotation defaults
    key_path = '~/.ssh/'
    key_path = os.path.expanduser(key_path)
    key_name = 'dev_key'
    prv_key = key_name + '.pem'
    pub_key = key_name + '.pub'
    ssh_host = 'dev'
    ssh_cfg = key_path + 'config.d/' + ssh_host

    # initial EC2 defaults (update these with EC2 instance values)
    ec2_ip = '54.193.60.207'
    ec2_key = 'dev_key.pem'
    ec2_user = 'ec2-user'
    ec2_port = '22'

    # initial ssh connection string
    ec2_ssh_str = key_path + ec2_key + ' ' + ec2_user + '@' + ec2_ip

    ec2 = boto3.client('ec2')

    try:
        print('\nChecking for existing EC2 key pair: ' + key_name)
        ec2.describe_key_pairs(KeyNames=[key_name])
    except ClientError as err:
        if err.response["Error"]["Code"] == "InvalidKeyPair.NotFound":
            gen_msg = 'Not Found! Generating new 2048-bit RSA key pair: '
    else:
        gen_msg = 'Found! Generating replacement 2048-bit RSA key pair: '
        ec2.delete_key_pair(KeyName=key_name)

    print('\n' + gen_msg + key_name)
    keypair = ec2.create_key_pair(KeyName=key_name)

    print('\nChecking for existing private key: ' + key_path + prv_key)
    if os.path.isfile(key_path + prv_key):
        down_msg = '\nFound! Downloading replacement private key: '
        prv_key = 'tmp.' + prv_key
    else:
        down_msg = '\nNot Found! Downloading private key: '

    print(down_msg + key_path + prv_key)
    # check for/make default SSH directory with octal mode permission syntax
    if not os.path.isdir(key_path):
        os.mkdir(key_path, 0o700)
    # check for/remove tmp private key from failed rotation
    if os.path.isfile(key_path + prv_key):
        os.remove(key_path + prv_key)
    with open(
        key_path + prv_key,'w+') as key:
        key.write(keypair['KeyMaterial'])

    print('\nAdd passphrase to private key (enter passphrase twice)...\n')
    os.chmod(key_path + prv_key, 0o600) # temporarily needed to add passphrase
    subprocess.run('ssh-keygen -p -f ' + key_path + prv_key, shell=True)

    print('\nAdd passphrase to ssh-agent & OS keychain (enter passphrase)\n')
    subprocess.run('/usr/bin/ssh-add -K ' + key_path + prv_key, shell=True)

    print('\nSet file permissions on private key to 400')
    os.chmod(key_path + prv_key, 0o400)

    print('\nGenerating public key (enter passphrase)...\n')
    subprocess.run('ssh-keygen -y -f ' + key_path + prv_key + ' > ' \
        + key_path + pub_key, shell=True)

    print('\nPushing public key to EC2 instance\n')
    # disable initial key verification prompt & add key to ~/.ssh/known_hosts
    subprocess.run('ssh -o StrictHostKeyChecking=no -tt -i ' + ec2_ssh_str + \
        ' exit &>/dev/null', shell=True)
    subprocess.run('cat ' + key_path + pub_key + ' | ssh -i ' + ec2_ssh_str + \
        ' "sudo tee -a ~/.ssh/authorized_keys > /dev/null"', shell=True)

    print('Removing public key from local disk')
    os.remove(key_path + pub_key)

    print('\nChecking for existing SSH alias: ' + ssh_cfg)
    if os.path.isfile(ssh_cfg):
        create_msg = '\nFound! Creating replacement SSH alias: '
        ssh_cfg = ssh_cfg + '_tmp'
    else:
        create_msg = '\nNot Found! Creating SSH alias: '

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

    print(create_msg + ssh_cfg + ' (enter password)\n')
    with open(ssh_cfg, "w") as config:
        txt_lines = [
        "Host "+ ssh_host,
        "\n   HostName " + ec2_ip,
        "\n   User " + ec2_user,
        "\n   Port " + ec2_port,
        "\n   IdentityFile " + key_path + prv_key
        ]
        config.writelines(txt_lines)

    print('Set file permissions on SSH alias to 600')
    os.chmod(ssh_cfg, 0o600)

    print('\nTesting remote access to EC2 instance using new key pair...')
    try:
        subprocess.run('ssh ' + ssh_host + ' exit &>/dev/null', shell=True)
    except OSError:
        RuntimeError('Error trying to open ssh connection')
    else:
        print('\nSuccess!')

        if os.path.isfile(key_path + 'config.d/' + ssh_host + '_tmp'):
            print('\nRemoving prior SSH alias config')
            os.remove(key_path + 'config.d/' + ssh_host)

            ssh_cfg = key_path + 'config.d/' + ssh_host
            print('\nRenaming new SSH alias config to ' + ssh_cfg)
            os.rename(ssh_cfg + '_tmp', ssh_cfg)

        if os.path.isfile(key_path + 'tmp.' + key_name + '.pem'):
            print('\nRemoving old private key ' + key_path + key_name + '.pem')
            os.remove(key_path + key_name + '.pem')
            prv_key = key_name + '.pem'
            print('\nRenaming new private key to ' + key_path + prv_key)
            os.rename(key_path + 'tmp.' + prv_key, key_path + prv_key)

            print('\nUpdating IdentityFile value in ' + ssh_cfg)
            with open(ssh_cfg) as config:
                sub = config.read().replace('tmp.' + prv_key, prv_key)

            with open(ssh_cfg, "w") as config:
                config.write(sub)

            if ec2_key != prv_key:
                print('\nRemoving initial EC2 private key')
                os.remove(key_path + ec2_key)

            print('\nUpdating ec2_key default value => ' + prv_key)
            with open('keypair.py') as file:
                sub = file.read().replace(ec2_key, prv_key)

            with open('keypair.py', "w") as file:
                file.write(sub)

if __name__ == '__main__':
    rotate_keypair()
