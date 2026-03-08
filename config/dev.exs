import Config

config :aegis, Aegis.Repo,
  username: "postgres",
  password: "postgres",
  hostname: "localhost",
  database: "aegis_dev",
  port: 5432,
  pool_size: 10

config :aegis,
  nats_url: "nats://localhost:4222",
  object_store_endpoint: "http://localhost:9000"

config :aegis, Aegis.ExecutionBridge,
  dispatch_poll_interval_ms: 100,
  timeout_poll_interval_ms: 1_000
