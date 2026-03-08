defmodule AegisExecutionBridge.MixProject do
  use Mix.Project

  def project do
    [
      app: :aegis_execution_bridge,
      version: "0.1.0",
      build_path: "../../_build",
      config_path: "../../config/config.exs",
      deps_path: "../../deps",
      lockfile: "../../mix.lock",
      elixir: "~> 1.17",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  def application do
    [
      extra_applications: [:logger],
      mod: {Aegis.ExecutionBridge.Application, []}
    ]
  end

  defp deps do
    [
      {:aegis_events, in_umbrella: true},
      {:aegis_runtime, in_umbrella: true},
      {:aegis_leases, in_umbrella: true}
    ]
  end
end
