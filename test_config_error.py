"""Test script to verify the fix for missing .env or empty required variables."""

import os

# Temporarily rename .env to simulate missing file
env_backup = None
if os.path.exists(".env"):
    os.rename(".env", ".env.backup_test")
    env_backup = True
    print("[TEST] Renamed .env to .env.backup_test to simulate missing file\n")

try:
    print("[TEST] Step 1: Importing app.config...")
    import app.config

    print("[TEST] ✅ Import successful!")
    print(f"[TEST] Type of configuracao: {type(app.config.configuracao)}")
    print(f"[TEST] configuracao is None: {app.config.configuracao is None}")

    if app.config.configuracao is None:
        print("[TEST] ✅ FIXED: configuracao is None (not undefined) - no NameError!")
    else:
        print(f"[TEST] configuracao value: {app.config.configuracao}")

    print("\n[TEST] Step 2: Importing app.main...")
    import app.main

    print("[TEST] ✅ app.main imported successfully - no AttributeError!")

    print(
        "\n[TEST] Step 3: Simulating startup (this should raise RuntimeError with clear message)..."
    )
    import asyncio

    try:
        asyncio.run(app.main.startup_event())
        print("[TEST] ❌ UNEXPECTED: startup_event did not raise an error!")
    except RuntimeError as e:
        print("[TEST] ✅ EXPECTED RuntimeError caught with clear message:")
        print(f"{e}")

except NameError as e:
    print(f"\n[TEST] ❌ NameError still occurs: {e}")
    print("[TEST] The bug is NOT fixed!")
except AttributeError as e:
    print(f"\n[TEST] ❌ AttributeError still occurs: {e}")
    print("[TEST] The bug is NOT fixed!")
except Exception as e:
    print(f"\n[TEST] ❌ Unexpected exception: {type(e).__name__}: {e}")
finally:
    # Restore .env
    if env_backup and os.path.exists(".env.backup_test"):
        os.rename(".env.backup_test", ".env")
        print("\n[TEST] Restored .env file")
