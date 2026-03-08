import Config

config :aegis,
  env: config_env(),
  repo: Aegis.Repo,
  ecto_repos: [Aegis.Repo]

config :logger, :console,
  format: "$time $metadata[$level] $message\n",
  metadata: [:request_id, :session_id, :tenant_id]

import_config "#{config_env()}.exs"
