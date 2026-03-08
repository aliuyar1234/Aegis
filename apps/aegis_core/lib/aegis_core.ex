defmodule AegisCore do
  @moduledoc """
  Root shared-kernel boundary for cross-app primitives that are safe to share.

  Phase 01 keeps this app intentionally small so runtime ownership does not leak out
  of `aegis_runtime` just for convenience.
  """
end
