output "queue_tasks_url" { value = aws_sqs_queue.tasks.id }
output "queue_results_url" { value = aws_sqs_queue.results.id  }

output "queue_tasks_name" { value = aws_sqs_queue.tasks.name }
output "queue_results_name" { value = aws_sqs_queue.results.name  }