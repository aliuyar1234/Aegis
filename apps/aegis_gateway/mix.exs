defmodule AegisGateway.MixProject do
  use Mix.Project

  def project do
    [
      app: :aegis_gateway,
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
      extra_applications: [:logger]
    ]
  end

  defp deps do
    [
      {:aegis_obs, in_umbrella: true},
      {:aegis_policy, in_umbrella: true},
      {:aegis_projection, in_umbrella: true}
    ]
  end
end
