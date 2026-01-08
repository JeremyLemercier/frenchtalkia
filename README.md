# Working with UV
https://docs.astral.sh/uv/getting-started/

# Install dependencies
uv pip install -r pyproject.toml
uv pip install -e ".[dev]"

# Run tests
pytest ./tests/unit/test_*.py -v

## WhatsApp webhook background processing

- This project processes incoming WhatsApp messages asynchronously using FastAPI `BackgroundTasks`.
- Large file I/O uses `aiofiles` for non-blocking reads/writes.
- HTTP calls to WhatsApp use retries with exponential backoff to handle 429/5xx responses.

Install runtime dependency:

```bash
pip install -r requirements.txt
# or with pip directly
pip install aiofiles
```

Notes:
- The app creates a shared `WhatsAppService` at startup (reused across requests) to avoid recreating HTTP clients per-request.
- Incoming messages are enqueued as background tasks; the webhook returns quickly with a 200-like JSON response.


