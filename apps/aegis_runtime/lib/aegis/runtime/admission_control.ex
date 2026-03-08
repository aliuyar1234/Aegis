defmodule Aegis.Runtime.AdmissionControl do
  @moduledoc false

  @spec admit_session(map() | keyword()) :: :ok | {:error, term()}
  def admit_session(attrs) do
    attrs = Map.new(attrs)

    scope = %{
      tenant_id: Map.fetch!(attrs, :tenant_id),
      workspace_id: Map.fetch!(attrs, :workspace_id)
    }

    session_id = Map.fetch!(attrs, :session_id)
    isolation_tier = AegisPolicy.isolation_tier(attrs)

    cond do
      Aegis.Events.session_exists?(session_id, scope) ->
        :ok

      true ->
        current = Aegis.Events.live_session_count(scope)
        limit = AegisPolicy.quota_limit(:live_sessions, attrs)

        if current < limit do
          :ok
        else
          {:error,
           {:quota_exceeded, :live_sessions,
            %{
              limit: limit,
              current: current,
              tenant_id: scope.tenant_id,
              workspace_id: scope.workspace_id,
              isolation_tier: isolation_tier
            }}}
        end
    end
  end
end
