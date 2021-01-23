variable "aws_region" { type = string }
variable "aws_profile" { type = string }
variable "fleet_count" { type = string }
variable "subnet_id" { type = string }
variable "vpc_id" { type = string }
variable "keyname" { type = string }
variable "results_s3_bucket" { type = string }
variable "tags_project" { type = string }
variable "queue_task_name" { type = string }
variable "queue_results_name" { type = string }

variable "instance_types" { default = [
  "c5.2xlarge",   // 8vCPU
  "c5.4xlarge",   // 16 vCPU    
  "m5.2xlarge",   // 8 vCPU
  "m5.4xlarge",   // 16 vCPU
  "m5.8xlarge",   // 32 vCPU
  "m5.12xlarge",  // 48 vCPU
  "m5.16xlarge",  // 64 vCPU
  "m5.24xlarge",  // 96 vCPU
  "c5.12xlarge",  // 48 vCPU
  "c5.18xlarge",  // 72 vCPU
  "c5.24xlarge"   // 96 vCPU
]}

variable "instance_cpu" { default = {
  "c5.2xlarge": 8, // 8vCPU
  "c5.4xlarge": 16, // 16 vCPU    
  "m5.2xlarge": 8, // 8 vCPU
  "m5.4xlarge": 16, // 16 vCPU
  "m5.8xlarge": 32, // 32 vCPU
  "m5.12xlarge": 48, // 48 vCPU
  "m5.16xlarge": 64, // 64 vCPU
  "m5.24xlarge": 96, // 96 vCPU
  "c5.12xlarge": 48, // 48 vCPU
  "c5.18xlarge": 72, // 72 vCPU
  "c5.24xlarge": 96 // 96 vCPU
}}