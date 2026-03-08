defmodule Aegis.Runtime.Naming do
  @moduledoc false

  @registry Aegis.Runtime.Registry

  @spec via(String.t(), atom()) :: {:via, Registry, {module(), {String.t(), atom()}}}
  def via(session_id, component) when is_binary(session_id) and is_atom(component) do
    {:via, Registry, {@registry, {session_id, component}}}
  end

  @spec whereis(String.t(), atom()) :: pid() | nil
  def whereis(session_id, component) do
    case Registry.lookup(@registry, {session_id, component}) do
      [{pid, _value}] -> pid
      [] -> nil
    end
  end
end
