data "aws_caller_identity" "current" {}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners = ["099720109477"] # Canonical
  filter {
    name = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*"]
  }
}

resource "aws_iam_role" "instance_role" {
  name = "tasker-role"
  path = "/"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
               "Service": "ec2.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}
EOF
}
resource "aws_iam_role_policy" "instance_policy" {
  name = "tasker-worker"
  role = aws_iam_role.instance_role.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect" : "Allow",
      "Action" : [
        "ecr:BatchGetImage",
        "ecr:DescribeImages",
        "ecr:GetAuthorizationToken",
        "ecr:ListImages",
        "ecr:GetDownloadUrlForLayer"
      ],
      "Resource" : "*"
    },
    {
      "Effect" : "Allow",
      "Action" : [
        "sqs:DeleteMessage",
        "sqs:ChangeMessageVisibility",
        "sqs:SendMessageBatch",
        "sqs:ReceiveMessage",
        "sqs:SendMessage",
        "sqs:ChangeMessageVisibilityBatch"
      ],
      "Resource" : "*"
    },
    {
      "Effect" : "Allow",
      "Action" : [
        "s3:*"
      ],
      "Resource" : "*"
    }
  ]
}
EOF
}
resource "aws_iam_instance_profile" "tasker_iam_profile" {
  name = "tasker_profile"
  role = aws_iam_role.instance_role.name
}

resource "aws_security_group" "tasker_ssh" {
  name = "tasker_ssh"
  vpc_id = var.vpc_id
  ingress {
    from_port = 22
    protocol = "tcp"
    to_port = 22
    cidr_blocks = ["2.236.103.86/32"]
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    project = var.tags_project
  }
}


resource "aws_spot_fleet_request" "tasker-fleet" {
  iam_fleet_role = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-ec2-spot-fleet-tagging-role"
  excess_capacity_termination_policy = "NoTermination"
  instance_interruption_behaviour = "terminate"
  replace_unhealthy_instances = true
  target_capacity = var.fleet_count
  terminate_instances_with_expiration = true
  fleet_type = "maintain"
  valid_until = "2099-12-22T20:44:20Z"
//  spot_price = "0.4"

  dynamic "launch_specification" {
    for_each = var.instance_types

    content {
      ami = data.aws_ami.ubuntu.image_id
      instance_type = launch_specification.value
      ebs_optimized = false
      iam_instance_profile_arn = aws_iam_instance_profile.tasker_iam_profile.arn
      key_name = var.keyname
      monitoring = false
      subnet_id = var.subnet_id
      vpc_security_group_ids = [ aws_security_group.tasker_ssh.id ]
      associate_public_ip_address = true

      root_block_device {
        delete_on_termination = true
        volume_type = "gp2"
        volume_size = 30
      }

      tags = {
        project = var.tags_project
      }

      user_data = <<-EOF
      #!/bin/bash -x
      apt-get update
      apt-get install -y vim jq python3-pip curl unzip

      #######################
      # Install the aws cli #
      #######################
      curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
      unzip awscliv2.zip
      ./aws/install

      ##################
      # Install docker #
      ##################
      apt-get remove docker docker-engine docker.io containerd runc

      apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg-agent \
        software-properties-common

      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
      add-apt-repository \
       "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
       $(lsb_release -cs) \
       stable"

      apt-get update
      apt-get install -y docker-ce docker-ce-cli containerd.io

      # Is it working?
      docker run hello-world

      ###################
      # Start the agent #
      ###################
      docker pull totomz84/docker-tasker-agent:latest && docker run --rm -d \
        -e S3_RESULTS_BUKET=${var.results_s3_bucket} \
        -e AWS_DEFAULT_REGION=${var.aws_region} \
        -e Q_TASK=${var.queue_task_name} \
        -e Q_RESULTS=${var.queue_results_name} \
        -v /var/run/docker.sock:/var/run/docker.sock \
        totomz84/docker-tasker-agent:latest

      EOF
    }


  }

}
