"""
Controller untuk Settings — baca dan update file .env.
"""
from pathlib import Path
from app.config import settings, BASE_DIR


ENV_PATH = BASE_DIR / ".env"

# Key yang boleh diubah via API
EDITABLE_KEYS = {
    # Server sync
    "SERVER_URL",
    "SERVER_API_KEY",
    "SYNC_INTERVAL",
    "HEARTBEAT_INTERVAL",
    # Camera Masuk
    "CAMERA_IN_HOST",
    "CAMERA_IN_USER",
    "CAMERA_IN_PASSWORD",
    "CAMERA_IN_CHANNEL",
    "CAMERA_IN_USE_HTTPS",
    # Camera Keluar
    "CAMERA_OUT_HOST",
    "CAMERA_OUT_USER",
    "CAMERA_OUT_PASSWORD",
    "CAMERA_OUT_CHANNEL",
    "CAMERA_OUT_USE_HTTPS",
    # Camera Umum
    "CAMERA_AUTH_TYPE",
    "CAMERA_TIMEOUT",
    # Relay
    "MODBUS_HOST",
    "MODBUS_PORT",
    # Node Identity
    "NODE_ID",
    "NODE_NAME",
}


def get_settings() -> dict:
    """Baca semua setting dari .env dan return sebagai dict."""
    env_values = _read_env_file()
    return {
        "server": {
            "SERVER_URL": env_values.get("SERVER_URL", settings.SERVER_URL),
            "SERVER_API_KEY": env_values.get("SERVER_API_KEY", settings.SERVER_API_KEY),
            "SYNC_INTERVAL": env_values.get("SYNC_INTERVAL", str(settings.SYNC_INTERVAL)),
            "HEARTBEAT_INTERVAL": env_values.get("HEARTBEAT_INTERVAL", str(settings.HEARTBEAT_INTERVAL)),
        },
        "camera_in": {
            "CAMERA_IN_HOST": env_values.get("CAMERA_IN_HOST", settings.CAMERA_IN_HOST),
            "CAMERA_IN_USER": env_values.get("CAMERA_IN_USER", settings.CAMERA_IN_USER),
            "CAMERA_IN_PASSWORD": env_values.get("CAMERA_IN_PASSWORD", settings.CAMERA_IN_PASSWORD),
            "CAMERA_IN_CHANNEL": env_values.get("CAMERA_IN_CHANNEL", str(settings.CAMERA_IN_CHANNEL)),
            "CAMERA_IN_USE_HTTPS": env_values.get("CAMERA_IN_USE_HTTPS", str(settings.CAMERA_IN_USE_HTTPS).lower()),
        },
        "camera_out": {
            "CAMERA_OUT_HOST": env_values.get("CAMERA_OUT_HOST", settings.CAMERA_OUT_HOST),
            "CAMERA_OUT_USER": env_values.get("CAMERA_OUT_USER", settings.CAMERA_OUT_USER),
            "CAMERA_OUT_PASSWORD": env_values.get("CAMERA_OUT_PASSWORD", settings.CAMERA_OUT_PASSWORD),
            "CAMERA_OUT_CHANNEL": env_values.get("CAMERA_OUT_CHANNEL", str(settings.CAMERA_OUT_CHANNEL)),
            "CAMERA_OUT_USE_HTTPS": env_values.get("CAMERA_OUT_USE_HTTPS", str(settings.CAMERA_OUT_USE_HTTPS).lower()),
        },
        "camera_common": {
            "CAMERA_AUTH_TYPE": env_values.get("CAMERA_AUTH_TYPE", settings.CAMERA_AUTH_TYPE),
            "CAMERA_TIMEOUT": env_values.get("CAMERA_TIMEOUT", str(settings.CAMERA_TIMEOUT)),
        },
        "relay": {
            "MODBUS_HOST": env_values.get("MODBUS_HOST", settings.MODBUS_HOST),
            "MODBUS_PORT": env_values.get("MODBUS_PORT", str(settings.MODBUS_PORT)),
        },
        "node": {
            "NODE_ID": env_values.get("NODE_ID", settings.NODE_ID),
            "NODE_NAME": env_values.get("NODE_NAME", settings.NODE_NAME),
        },
    }


def update_settings(updates: dict) -> dict:
    """
    Update setting di .env file.
    Hanya key yang ada di EDITABLE_KEYS yang boleh diubah.
    """
    # Validasi key
    for key in updates:
        if key not in EDITABLE_KEYS:
            raise ValueError(f"Setting '{key}' tidak bisa diubah")

    # Baca .env yang ada
    env_lines = _read_env_lines()
    updated_keys = set()

    # Update baris yang ada
    for i, line in enumerate(env_lines):
        stripped = line.strip()
        if stripped.startswith("#") or "=" not in stripped:
            continue
        key = stripped.split("=", 1)[0].strip()
        if key in updates:
            env_lines[i] = f"{key}={updates[key]}"
            updated_keys.add(key)

    # Tambah key yang belum ada
    for key, value in updates.items():
        if key not in updated_keys:
            env_lines.append(f"{key}={value}")

    # Tulis kembali
    ENV_PATH.write_text("\n".join(env_lines) + "\n", encoding="utf-8")

    # Reload environment variables agar settings object terupdate
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH, override=True)

    return {"success": True, "message": f"Berhasil update {len(updates)} setting."}


def _read_env_file() -> dict:
    """Baca .env file dan return sebagai dict."""
    result = {}
    if not ENV_PATH.exists():
        return result
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def _read_env_lines() -> list:
    """Baca .env file sebagai list of lines."""
    if not ENV_PATH.exists():
        return []
    return ENV_PATH.read_text(encoding="utf-8").splitlines()
