
resource "random_pet" "name" {
  length = 1
}

resource "aws_sqs_queue" "tasks" {
  name = "${random_pet.name.id}-tasks"
  
  tags = {
    project = "trader"
  }
}

resource "aws_sqs_queue" "results" {
  name = "${random_pet.name.id}-results"
  
  tags = {
    project = "trader"
  }
}