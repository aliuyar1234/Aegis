defmodule Aegis.Policy.EvaluatorTest do
  use ExUnit.Case, async: true

  alias Aegis.Policy.{CapabilityToken, DangerousActionCatalog, Evaluator}

  @session_context %{
    tenant_id: "tenant-policy",
    workspace_id: "workspace-policy",
    session_id: "session-policy",
    lease_epoch: 7
  }

  test "allows read-only browser actions without approval or capability tokens" do
    assert {:ok, decision} =
             Evaluator.evaluate_action(
               %{
                 action_id: "action-read-1",
                 tool_id: "browser.navigate",
                 input: %{url: "https://example.com"}
               },
               @session_context
             )

    assert decision.decision == "allow"
    assert decision.approval_required == false
    assert decision.capability_token_ref == nil
    assert decision.dangerous_action_class == nil
  end

  test "issues capability tokens for allow-with-constraints browser writes" do
    assert {:ok, decision} =
             Evaluator.evaluate_action(
               %{
                 action_id: "action-click-1",
                 tool_id: "browser.click",
                 input: %{selector: "#save"}
               },
               @session_context
             )

    assert decision.decision == "allow_with_constraints"
    assert decision.approval_required == false
    assert is_binary(decision.capability_token_ref)
    assert is_binary(decision.approved_argument_digest)

    assert {:ok, claims} = CapabilityToken.decode(decision.capability_token_ref)
    assert claims["session_id"] == "session-policy"
    assert claims["tool_id"] == "browser.click"
    assert claims["dangerous_action_class"] == "browser_write_low"
    assert claims["approved_argument_digest"] == decision.approved_argument_digest
  end

  test "requires approval for medium-risk browser writes and denies high-risk defaults" do
    assert {:ok, medium} =
             Evaluator.evaluate_action(
               %{
                 action_id: "action-submit-1",
                 tool_id: "browser.submit",
                 input: %{selector: "form#profile"}
               },
               @session_context
             )

    assert medium.decision == "require_approval"
    assert medium.approval_required
    assert medium.capability_token_ref == nil

    assert {:ok, high} =
             Evaluator.evaluate_action(
               %{
                 action_id: "action-delete-1",
                 tool_id: "browser.delete",
                 input: %{selector: "button.delete"}
               },
               @session_context
             )

    assert high.decision == "deny"
    assert high.approval_required == false
  end

  test "exposes dangerous action catalog defaults" do
    assert DangerousActionCatalog.ids() |> Enum.take(3) == [
             "browser_write_high",
             "browser_write_low",
             "browser_write_medium"
           ]

    assert DangerousActionCatalog.default_decision("browser_write_low") == "require_approval" or
             DangerousActionCatalog.default_decision("browser_write_low") == "allow_with_constraints"
  end
end
