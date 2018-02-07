DevOps /etc [[https://github.com/DevOpsEtc/ec2-keypair-rotation/blob/master/logo.png|alt=logo]]

**Summary:**
Has it been a while since you last rotated your AWS EC2 instance's key pair? Maybe you keep putting it off because of the hassle of putting the public and private keys everywhere they need to be for successful remote access. Of course, don't forget to test before removing that old key pair! Why not make it easier on yourself by automating that process. Using Python and AWS's Boto3, you can easily rinse and repeat without breaking a sweat, or your remote access!

Additional information on blog post at [DevOpsEtc.com/post/ec2-keypair-rotation](https://www.DevOpsEtc.com/post/ec2-keypair-rotation)

**Features/Benefits:**
  * SSH alias for quicker remote connection, e.g. $ ssh [host]
  * Private key passphrase stored in ssh-agent and OS keychain for ease of connection
  * Encrypted private key provides greater protection from risk of leaks
  * Key pair replacements are tested to ensure remote access to EC2 instance
  * Automatic updates to EC2 key pairs, EC2's authorized_keys, and local known_hosts and ssh aliases

**Prerequisites:**
  * MacOS High Sierra (will probably work on earlier MacOS versions and Linux, but untested)
  * Python 3: $ brew install python3
  * Python Modules: $ pip3 install boto3 awscli (you may need to run via sudo for elevated privileges)
  * AWS IAM access keys: $ aws configure (paste in access keys from: AWS management console)
  * EC2 key pair created before EC2 instance launch
  * EC2 instance with remote access via EC2 key pair

**Getting Started:**
    # Clone the keypair-rotation repo on GitHub
    $ git clone https://github.com/DevOpsEtc/ec2-keypair-rotation ~/DevOpsEtc/ec2-keypair-rotation

    # Update default values in  ~/DevOpsEtc/ec2-keypair-rotation/keypair.py

    # Initial EC2 defaults (add your EC2 instance values inside the quotes)
    ec2_ip = '000.000.000.000'    # public IP address or public DNS
    ec2_key = 'dev_key.pem'       # current private key
    ec2_user = 'ec2-user'         # default AMI user
    ec2_port = '22'               # SSH port number

    # OPTIONAL: Update these other default values
    key_path = '~/.ssh/'
    key_name = 'dev_key'
    ssh_host = 'dev'            

    # Remote access via SSH
    $ ssh dev # or whatever you set the ssh_host value to

**Known Issues:**
- None

**Road Map:**
- add input prompts to ingest EC2 instance values

**Contributing:**
1. Review open issues
2. Open new issue to start discussion about a feature request or bug
3. Fork the repo, make changes, then send pull request to dev branch
