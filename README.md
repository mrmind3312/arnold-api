# ArnoldAPI

A tiny microframework for HTTP APIs using an ArnoldC-inspired `.arnoldc` route DSL.

> ArnoldC itself compiles to JVM bytecode and has no HTTP standard library. ArnoldAPI keeps the ArnoldC program shape (`IT'S SHOWTIME`, `TALK TO THE HAND`, `YOU HAVE BEEN TERMINATED`) and adds a deliberately small route extension interpreted by a Python HTTP runtime. This makes the prototype runnable without a JDK while leaving a clean boundary for a future JVM adapter.

## Quick start

```bash
python examples/run.py
curl http://127.0.0.1:8080/
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/hello/Lionel
```

## Route syntax

```arnoldc
IT'S SHOWTIME

ROUTE "GET" "/users/<id>"
TALK TO THE HAND "user response"
ENOUGH TALK

ROUTE "GET" "/health"
RETURN JSON "{\"status\": \"ok\"}"
ENOUGH TALK

YOU HAVE BEEN TERMINATED
```

Supported methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`.
Supported responses: plain text with `TALK TO THE HAND` and JSON with `RETURN JSON`.
Path parameters use `<name>`; query parameters are available to Python handlers as `request["query"]`.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Status

This is an educational v0.1 microframework, not a production replacement for Fastify or Express. It intentionally uses only Python's standard library and has no external dependencies.

## License

MIT
