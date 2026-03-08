# Release and upgrade matrix

| Flavor | Release owner | Upgrade strategy | Migration owner | Required docs |
|---|---|---|---|---|
| OSS local | runtime operator | self-managed migration with explicit release notes | runtime operator | `README.md`, `docs/references/packaging-matrix.md`, `docs/references/release-upgrade-matrix.md` |
| Shared cloud | Aegis cloud | provider-managed rollout with tenant notice | `aegis_cloud` | `docs/product-specs/operator-console.md`, `docs/references/packaging-matrix.md`, `docs/references/release-upgrade-matrix.md` |
| Isolated execution | Aegis cloud with tenant coordination | coordinated rollout with execution-pool preflight | `aegis_cloud_with_tenant_coordination` | `docs/design-docs/deployment-flavors.md`, `docs/references/packaging-matrix.md`, `docs/references/release-upgrade-matrix.md` |
| Dedicated deployment | coordinated dedicated release | dedicated change-window rollout with preflight evidence bundle | `coordinated_dedicated_release` | `docs/design-docs/deployment-flavors.md`, `docs/references/packaging-matrix.md`, `docs/references/release-upgrade-matrix.md` |
