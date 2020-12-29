provider "aws" {
  profile = var.aws_profile
  region = var.aws_region
}

module "queues" {
  source = "./queues"
}

module "fleet_aws" {
  source = "./aws"
  
  aws_profile = var.aws_profile
  aws_region = var.aws_region
  fleet_count = var.fleet_count
  keyname = var.keyname
  queue_task_name = module.queues.queue_tasks_name
  queue_results_name = module.queues.queue_results_name
  results_s3_bucket = var.results_s3_bucket
  subnet_id = var.subnet_id
  tags_project = "autotrader"
  vpc_id = var.vpc_id
  
  
}