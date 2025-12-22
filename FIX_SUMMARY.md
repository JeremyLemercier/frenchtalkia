# Fix Summary: Configuration Error Handling

## Problem
When `.env` file was missing or had empty required variables, the application would fail with an unclear `NameError` or `AttributeError` instead of providing a helpful error message to the user.

### Root Cause
In [`app/config.py:90-95`](app/config.py:90), the module-level code attempted to load configuration:

```python
try:
    configuracao = get_configuracao()
except ValueError:
    pass  # Silent failure - configuracao never gets defined!
```

When `get_configuracao()` raised a `ValueError`, the `except` block would silently swallow the error with `pass`, leaving the `configuracao` variable **undefined**. This caused:

1. `AttributeError: module 'app.config' has no attribute 'configuracao'` when importing
2. `NameError: name 'configuracao' is not defined` when accessing it later

## Solution Implemented

### 1. Fixed `app/config.py` (lines 90-97)
```python
configuracao: ConfiguracaoApp | None = None
try:
    configuracao = get_configuracao()
except ValueError as e:
    # Define configuracao como None para evitar NameError
    # A validação adequada deve ser feita onde a configuração é usada
    import sys
    print(f"\n❌ ERRO DE CONFIGURAÇÃO: {e}\n", file=sys.stderr)
    configuracao = None
```

**Changes:**
- Explicitly declare `configuracao` with type annotation `ConfiguracaoApp | None = None`
- Set `configuracao = None` in the exception handler instead of using `pass`
- Print the error message to stderr for visibility

### 2. Added Validation in `app/main.py` startup_event (lines 32-48)
```python
async def startup_event():
    """Evento de inicialização da aplicação."""
    # Validar que a configuração foi carregada com sucesso
    if configuracao is None:
        erro_msg = (
            "\n❌ ERRO FATAL: Não foi possível inicializar a aplicação.\n"
            "A configuração não pôde ser carregada devido a variáveis de ambiente ausentes ou inválidas.\n\n"
            "Por favor, verifique:\n"
            "1. Se o arquivo .env existe no diretório raiz do projeto\n"
            "2. Se todas as variáveis obrigatórias estão definidas:\n"
            "   - WHATSAPP_TOKEN\n"
            "   - WHATSAPP_PHONE_NUMBER_ID\n"
            "   - WHATSAPP_VERIFY_TOKEN\n"
            "   - MISTRAL_API_KEY\n"
            "   - GLADIA_API_KEY\n"
            "   - MURF_API_KEY\n\n"
            "Você pode copiar o arquivo .env.example para .env e preencher os valores necessários.\n"
        )
        raise RuntimeError(erro_msg)
    
    # Continue with normal startup...
```

### 3. Updated health_check and info endpoints (lines 125-177)
Both endpoints now check if `configuracao is None` and return appropriate error responses instead of crashing.

## Test Results

### Before Fix
```
❌ AttributeError: module 'app.config' has no attribute 'configuracao'
```

### After Fix
```
✓ app.config imported successfully
  - configuracao type: <class 'NoneType'>
  - configuracao is None: True
✓ PASS: configuracao is None (not undefined)
```

## Benefits

1. **No more NameError/AttributeError**: The variable is always defined (either as `ConfiguracaoApp` or `None`)
2. **Clear error messages**: Users see helpful instructions about what's wrong and how to fix it
3. **Fail-fast at startup**: The application raises a clear `RuntimeError` during startup instead of failing mysteriously later
4. **Graceful degradation**: Health and info endpoints can still respond even when configuration is missing

## Files Modified

- [`app/config.py`](app/config.py): Lines 90-97
- [`app/main.py`](app/main.py): Lines 7-8, 32-48, 125-177

## Note

There is an unrelated Pydantic error in `app/models/sessao.py` that prevents the application from starting:
```
PydanticUserError: "Config" and "model_config" cannot be used together
```

This is a separate issue that needs to be fixed in the Sessao model class.
