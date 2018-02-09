# DevOps /etc [[https://github.com/DevOpsEtc/ec2-keypair-rotation/blob/master/logo.png|alt=logo]]

## Simple AWS EC2 Key Pair Rotation Using Python and Boto3

Has it been a while since you last rotated your AWS EC2 instance's key pair? Maybe you keep putting it off like I use to do, because of the hassle of putting the public and private keys everywhere they need. Of course, don't forget testing before removing that old key pair! Time to automate that process. This project, built with the AWS SDK for Python (Boto3), allows you to quickly rinse/repeat key pair rotation without breaking a sweat, or your remote access!

Code walkthrough and additional information can be found on my blog post at [DevOpsEtc.com/post/ec2-keypair-rotation](https://www.DevOpsEtc.com/post/ec2-keypair-rotation)

**Features/Benefits:**
  * EC2 generated 2048-bit RSA key pair
  * Encrypted private key provides greater protection from risk of leaks
  * Private key passphrase stored in ssh-agent and OS keychain for easier access
  * SSH alias for quicker remote connection, e.g. $ ssh [host]
  * Key pair replacements are tested to ensure against loss of remote EC2 access
  * Automatic updates to EC2 key pairs, EC2's authorized_keys, and local known_hosts and ssh aliases

**Prerequisites:**
  * MacOS High Sierra (will probably work on earlier MacOS versions and Linux, but untested)
  * Python 3: $ brew install python3
  * Python Modules: $ pip3 install boto3 awscli colorama (sudo may needed to run with elevated privileges)
  * AWS credentials: $ aws configure (paste in access keys from AWS management console)
  * EC2 key pair created before EC2 instance launch
  * EC2 instance with remote access via EC2 key pair
  * Strong passphrase recorded in a password manager (for new key pair)

**Getting Started:**
    # Clone the keypair-rotation repo on GitHub
    $ git clone https://github.com/DevOpsEtc/ec2-keypair-rotation ~/DevOpsEtc/ec2-keypair-rotation

    # Update default values in  ~/DevOpsEtc/ec2-keypair-rotation/keypair.py

    # Initial EC2 defaults (add your EC2 instance values inside the quotes)
    ec2_ip = '000.000.000.000'    # public IP address or public DNS
    ec2_key = 'dev_key.pem'       # current private key
    ec2_user = 'ec2-user'         # default AMI user
    ec2_port = '22'               # SSH port number
    key_name = 'dev_key'          # base name of private key

    # Run script
    $ cd ~/DevOpsEtc/ec2-keypair-rotation && ./keypair.py

    # Remote access via SSH
    $ ssh dev # or whatever you set the ssh_host value to

    # Create bash alias to save some typing (stick in .bashrc for permanency)
    $ alias kr='cd ~/DevOpsEtc/ec2-keypair-rotation && ./keypair.py'

    # rotate key pair again (no need to update variable values this time)
    $ kr

    # import module from inside your own Python project
    >>> from keypair import *

**Known Issues:**
- None

**Road Map:**
- add input prompts to ingest parameters of EC2 instance values

**Contributing:**
1. Review open issues
2. Open new issue to start discussion about a feature request or bug
3. Fork the repo, make changes, then send pull request to dev branch
