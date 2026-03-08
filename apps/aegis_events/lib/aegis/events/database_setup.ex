defmodule Aegis.Events.DatabaseSetup do
  @moduledoc false

  alias Aegis.Repo
  alias Ecto.Adapters.SQL

  def ensure_database! do
    repo_config = Application.fetch_env!(:aegis, Repo)
    database = Keyword.fetch!(repo_config, :database)

    admin_config =
      repo_config
      |> Keyword.take([:hostname, :port, :username, :password, :ssl])
      |> Keyword.put(:database, "postgres")
      |> Keyword.put_new(:backoff_type, :stop)

    {:ok, conn} = Postgrex.start_link(admin_config)

    try do
      case Postgrex.query!(conn, "SELECT 1 FROM pg_database WHERE datname = $1", [database]).rows do
        [] ->
          Postgrex.query!(conn, "CREATE DATABASE #{quote_identifier(database)}", [])

        _rows ->
          :ok
      end
    after
      GenServer.stop(conn)
    end

    :ok
  end

  def ensure_schema! do
    Ecto.Adapters.SQL.Sandbox.unboxed_run(Repo, fn ->
      migration_paths()
      |> Enum.each(fn path ->
        path
        |> File.read!()
        |> String.split(~r/;\s*\r?\n/, trim: true)
        |> Enum.map(&String.trim/1)
        |> Enum.reject(&(&1 == ""))
        |> Enum.each(fn statement ->
          SQL.query!(Repo, statement, [])
        end)
      end)
    end)

    :ok
  end

  def migration_paths do
    __DIR__
    |> Path.join("../../../../../apps/*/priv/postgres/migrations/*.sql")
    |> Path.expand()
    |> Path.wildcard()
    |> Enum.sort_by(&{Path.basename(&1), &1})
  end

  defp quote_identifier(name) do
    if name =~ ~r/\A[a-zA-Z0-9_]+\z/ do
      ~s("#{name}")
    else
      raise ArgumentError, "unsafe database identifier: #{inspect(name)}"
    end
  end
end
