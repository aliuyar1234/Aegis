defmodule AegisExecutionBridge do
  @moduledoc """
  Compatibility wrapper for the `aegis_execution_bridge` umbrella application.

  The Phase 04 transport implementation lives under `Aegis.ExecutionBridge`.
  """

  def flush_dispatches, do: Aegis.ExecutionBridge.flush_dispatches()
  def scan_timeouts, do: Aegis.ExecutionBridge.scan_timeouts()
  def register_worker(attrs), do: Aegis.ExecutionBridge.register_worker(attrs)
  def worker_heartbeat(attrs), do: Aegis.ExecutionBridge.worker_heartbeat(attrs)
  def accept_action(worker_kind, payload, headers \\ %{}), do: Aegis.ExecutionBridge.accept_action(worker_kind, payload, headers)
  def progress_action(worker_kind, payload, headers \\ %{}), do: Aegis.ExecutionBridge.progress_action(worker_kind, payload, headers)
  def action_heartbeat(worker_kind, payload, headers \\ %{}), do: Aegis.ExecutionBridge.action_heartbeat(worker_kind, payload, headers)
  def complete_action(worker_kind, payload, headers \\ %{}), do: Aegis.ExecutionBridge.complete_action(worker_kind, payload, headers)
  def fail_action(worker_kind, payload, headers \\ %{}), do: Aegis.ExecutionBridge.fail_action(worker_kind, payload, headers)
  def cancel_action(worker_kind, payload, headers \\ %{}), do: Aegis.ExecutionBridge.cancel_action(worker_kind, payload, headers)
  def request_action_cancel(session_id, action_id, reason, opts \\ []), do: Aegis.ExecutionBridge.request_action_cancel(session_id, action_id, reason, opts)
  def published_messages, do: Aegis.ExecutionBridge.published_messages()
  def execution(execution_id), do: Aegis.ExecutionBridge.execution(execution_id)
  def worker_registration(worker_id), do: Aegis.ExecutionBridge.worker_registration(worker_id)
  def worker_registrations, do: Aegis.ExecutionBridge.worker_registrations()
  def reset!, do: Aegis.ExecutionBridge.reset!()
end
