# Packaging matrix

| Flavor | OSS core included | Managed surfaces added | Control plane | Worker pools | Artifact isolation | Package artifacts |
|---|---|---|---|---|---|---|
| OSS local | yes | none | self-managed | shared | local bucket | source checkout, compose bundle, optional container images |
| Shared cloud | yes | shared cloud control plane, managed operations | managed shared | shared | shared bucket with tenant prefixes | managed service release, tenant bootstrap bundle |
| Isolated execution | yes | shared cloud control plane, isolated execution routing, managed operations | managed shared | tenant isolated | tenant-dedicated keyspace | managed service release, isolated execution pool bundle, tenant routing configuration |
| Dedicated deployment | yes | isolated execution routing, dedicated deployment management, managed operations, enterprise integrations | dedicated | dedicated | dedicated object store | dedicated control-plane bundle, dedicated execution bundle, environment-specific configuration pack |
