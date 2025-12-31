"""
Comprehensive test to verify the fix for missing .env configuration.

This test verifies that:
1. When .env is missing, configuracao is set to None (not undefined)
2. app.main can be imported without NameError or AttributeError
3. startup_event raises a clear RuntimeError with helpful message
4. health and info endpoints handle None configuracao gracefully
"""

import asyncio
import os
import sys


def test_missing_env():
    """Test behavior when .env file is missing."""
    print("=" * 70)
    print("TEST: Missing .env file")
    print("=" * 70)

    # Backup .env if it exists
    env_backup = False
    if os.path.exists(".env"):
        os.rename(".env", ".env.backup_test")
        env_backup = True
        print("✓ Backed up .env to .env.backup_test\n")

    try:
        # Test 1: Import app.config
        print("Test 1: Importing app.config...")
        import app.config

        print("✓ app.config imported successfully")
        print(f"  - configuracao type: {type(app.config.configuracao)}")
        print(f"  - configuracao is None: {app.config.configuracao is None}")

        if app.config.configuracao is None:
            print("✓ PASS: configuracao is None (not undefined)\n")
        else:
            print("✗ FAIL: configuracao should be None\n")
            return False

        # Test 2: Import app.main
        print("Test 2: Importing app.main...")
        import app.main

        print("✓ app.main imported successfully")
        print("✓ PASS: No AttributeError or NameError during import\n")

        # Test 3: Test startup_event
        print("Test 3: Testing startup_event (should raise RuntimeError)...")
        try:
            asyncio.run(app.main.startup_event())
            print("✗ FAIL: startup_event should have raised RuntimeError\n")
            return False
        except RuntimeError as e:
            error_msg = str(e)
            print("✓ RuntimeError raised as expected")
            print(f"  Error message preview: {error_msg[:100]}...")

            # Check if error message contains helpful information
            required_keywords = [".env", "WHATSAPP_TOKEN", "MISTRAL_API_KEY"]
            missing_keywords = [kw for kw in required_keywords if kw not in error_msg]

            if missing_keywords:
                print(f"✗ FAIL: Error message missing keywords: {missing_keywords}\n")
                return False
            else:
                print("✓ PASS: Error message contains helpful information\n")

        # Test 4: Test health endpoint
        print("Test 4: Testing health_check endpoint...")
        result = asyncio.run(app.main.health_check())
        print(f"  Response: {result}")

        if result.get("status") == "error" and "erro" in result:
            print("✓ PASS: health_check handles None configuracao gracefully\n")
        else:
            print("✗ FAIL: health_check should return error status\n")
            return False

        # Test 5: Test info endpoint
        print("Test 5: Testing info endpoint...")
        result = asyncio.run(app.main.info())
        print(f"  Response keys: {list(result.keys())}")

        if result.get("status") == "erro_configuracao" and "erro" in result:
            print("✓ PASS: info handles None configuracao gracefully\n")
        else:
            print("✗ FAIL: info should return erro_configuracao status\n")
            return False

        print("=" * 70)
        print("ALL TESTS PASSED! ✓")
        print("=" * 70)
        print("\nSummary:")
        print("✓ No NameError when configuracao is None")
        print("✓ No AttributeError when importing app.main")
        print("✓ Clear RuntimeError with helpful message at startup")
        print("✓ Endpoints handle None configuracao gracefully")
        return True

    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Restore .env
        if env_backup and os.path.exists(".env.backup_test"):
            os.rename(".env.backup_test", ".env")
            print("\n✓ Restored .env file")


if __name__ == "__main__":
    success = test_missing_env()
    sys.exit(0 if success else 1)
