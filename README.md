# Robot simulations

Writer scan/drop and executor navigation/read simulation clients.
Full documentation is centralized in [`../docs/`](../docs/README.md).

- [Run guide](../docs/run-guide.md)
- [Architecture](../docs/architecture.md)
- [Testing](../docs/testing.md)
- [Code organization proposal](../docs/code-structure.md)

Docker configuration lives in `../docker/`. The local legacy JSON-only relay is
not deployed; these clients connect to Network's authenticated binary relay.
