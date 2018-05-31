<h1> <img src="image/logo.png"> DevOps /etc</h1>

### Rotate Your AWS EC2 Key Pair Using the AWS SDK for Python

Has it been a while since you last rotated your AWS EC2 instance's key pair? Maybe you keep putting it off, because of the hassle of having to stick the public and private keys in all the appropriate places. Of course, don't forget to test your new connection before removing that old key pair! Ugh, time to automate that process. Fortunately, this tedious task could can be automated with a configuration management tool like Ansible. But what if this is a one-off EC2 instance and you don't want to deal with setting up an individual task and playbook. This project, built with the AWS SDK for Python (Boto3), allows you to quickly rinse/repeat EC2 key pair rotation without breaking a sweat... or your remote access!

Blog post with additional information can be found at:  [https://www.DevOpsEtc.com/post/ec2-keypair-rotation](https://www.DevOpsEtc.com/post/ec2-keypair-rotation)

**Known Issues:**
- None

**Road Map:**
- add input prompts to ingest parameters of EC2 instance values

**Contributing:**
1. Review open issues
2. Open new issue to start discussion about a feature request or bug
3. Fork the repo, make changes, then send pull request to dev branch
