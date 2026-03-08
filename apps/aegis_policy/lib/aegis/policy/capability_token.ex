defmodule Aegis.Policy.CapabilityToken do
  @moduledoc """
  Encodes and decodes scoped capability-token claims for effectful actions.
  """

  @prefix "aegis.ctk.v1."

  @spec mint(map()) :: %{token: String.t(), token_ref: String.t(), claims: map()}
  def mint(claims) when is_map(claims) do
    normalized_claims = normalize(claims)
    encoded_claims = normalized_claims |> :erlang.term_to_binary() |> Base.url_encode64(padding: false)

    %{
      token: @prefix <> encoded_claims,
      token_ref:
        normalized_claims
        |> :erlang.term_to_binary()
        |> then(&:crypto.hash(:sha256, &1))
        |> Base.encode16(case: :lower),
      claims: normalized_claims
    }
  end

  @spec decode(String.t()) :: {:ok, map()} | {:error, :invalid_token}
  def decode(token) when is_binary(token) do
    if String.starts_with?(token, @prefix) do
      encoded_claims = String.replace_prefix(token, @prefix, "")

      with {:ok, raw} <- Base.url_decode64(encoded_claims, padding: false),
           claims when is_map(claims) <- :erlang.binary_to_term(raw) do
        {:ok, claims}
      else
        _ -> {:error, :invalid_token}
      end
    else
      {:error, :invalid_token}
    end
  rescue
    _error -> {:error, :invalid_token}
  end

  def decode(_token), do: {:error, :invalid_token}

  defp normalize(value) when is_map(value) do
    value
    |> Enum.map(fn {key, item} -> {to_string(key), normalize(item)} end)
    |> Enum.sort_by(fn {key, _value} -> key end)
    |> Enum.into(%{})
  end

  defp normalize(value) when is_list(value), do: Enum.map(value, &normalize/1)
  defp normalize(value), do: value
end
