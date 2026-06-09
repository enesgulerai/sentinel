resource "aws_db_instance" "sentinel_postgres" {
  identifier           = "sentinel-production-db"
  allocated_storage    = 50
  storage_type         = "gp3"
  engine               = "postgres"
  engine_version       = "15"
  instance_class       = "db.t4g.large" # Burstable ARM
  skip_final_snapshot  = true
}

resource "aws_elasticache_cluster" "sentinel_redis" {
  cluster_id           = "sentinel-production-redis"
  engine               = "redis"
  node_type            = "cache.t4g.large" # Burstable ARM
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
}

resource "aws_instance" "redpanda_nodes" {
  count         = 3
  ami           = "ami-00000000000000000"
  instance_type = "t4g.large" # Burstable ARM
  subnet_id     = aws_subnet.public_1.id

  root_block_device {
    volume_size = 100
    volume_type = "gp3"
    iops        = 3000
  }
}
