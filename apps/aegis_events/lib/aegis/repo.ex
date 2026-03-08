defmodule Aegis.Repo do
  @moduledoc """
  Shared Postgres repo for the Aegis control plane.
  """

  use Ecto.Repo,
    otp_app: :aegis,
    adapter: Ecto.Adapters.Postgres
end
