# Media topology

This document supports PHASE-11.

## Purpose

Define the future voice/media data plane without changing Aegis's core thesis.

## Core rules

- media packets and codecs stay in Rust sidecars
- media artifacts register through the same artifact metadata path
- session ownership and replay remain in the Elixir control plane
- degraded QoS must surface as explicit runtime state and runbooks
