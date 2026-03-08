# Packaging matrix

| Flavor | Control plane | Worker pools | Artifact isolation | Typical tier |
|---|---|---|---|---|
| OSS local | self-managed | shared | local bucket | development |
| Shared cloud | managed shared | shared | shared bucket w/ tenant prefixes | Tier A |
| Isolated execution | managed shared | dedicated per tenant | dedicated keyspace | Tier B |
| Dedicated deployment | dedicated | dedicated | dedicated | Tier C |
