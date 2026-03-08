defmodule Aegis.ExecutionBridge.AdmissionControl do
  @moduledoc false

  alias Aegis.ExecutionBridge.Store

  @spec admit_dispatch(map() | keyword(), map() | keyword()) :: :ok | {:error, term()}
  def admit_dispatch(scope_attrs, action_attrs) do
    scope_attrs = Map.new(scope_attrs)
    action_attrs = Map.new(action_attrs)

    scope = %{
      tenant_id: Map.fetch!(scope_attrs, :tenant_id),
      workspace_id: Map.fetch!(scope_attrs, :workspace_id)
    }

    isolation_tier = AegisPolicy.isolation_tier(scope_attrs)

    with :ok <- maybe_admit_browser_context(scope, scope_attrs, action_attrs, isolation_tier),
         :ok <- maybe_admit_effectful_action(scope, scope_attrs, action_attrs, isolation_tier) do
      :ok
    end
  end

  defp maybe_admit_browser_context(scope, scope_attrs, action_attrs, isolation_tier) do
    if Map.get(action_attrs, :worker_kind) == "browser" do
      enforce_limit(
        scope,
        scope_attrs,
        :concurrent_browser_contexts,
        [worker_kind: "browser"],
        isolation_tier
      )
    else
      :ok
    end
  end

  defp maybe_admit_effectful_action(scope, scope_attrs, action_attrs, isolation_tier) do
    if Map.get(action_attrs, :mutating, false) do
      enforce_limit(
        scope,
        scope_attrs,
        :concurrent_effectful_actions,
        [mutating: true],
        isolation_tier
      )
    else
      :ok
    end
  end

  defp enforce_limit(scope, scope_attrs, quota_class, filters, isolation_tier) do
    current = Store.nonterminal_execution_count(scope, filters)
    limit = AegisPolicy.quota_limit(quota_class, scope_attrs)

    if current < limit do
      :ok
    else
      {:error,
       {:quota_exceeded, quota_class,
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
