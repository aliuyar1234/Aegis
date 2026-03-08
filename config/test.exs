import Config

config :aegis, Aegis.Repo,
  username: "postgres",
  password: "postgres",
  hostname: "localhost",
  database: "aegis_test",
  port: 5432,
  pool: Ecto.Adapters.SQL.Sandbox,
  pool_size: 10

config :aegis, Aegis.ExecutionBridge,
  dispatch_poll_interval_ms: :manual,
  timeout_poll_interval_ms: :manual
