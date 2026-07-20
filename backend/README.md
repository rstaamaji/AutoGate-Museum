# ANPR Backend (FastAPI)

Backend untuk mencatat plat nomor kendaraan dari kamera Hikvision ANPR, dengan
struktur folder yang meniru gaya Laravel supaya familiar.

```
backend/
├── app/
│   ├── Http/
│   │   ├── Controllers/VehicleController.py   # terima request, panggil Service
│   │   ├── Requests/VehicleRequest.py         # schema validasi (pydantic)
│   │   └── Middleware/auth.py                 # dependency X-API-Key (opsional)
│   ├── Models/Vehicle.py                      # SQLAlchemy model (tabel vehicles)
│   ├── Services/
│   │   ├── CameraService.py                   # komunikasi ISAPI ke kamera Hikvision
│   │   └── VehicleService.py                  # simpan gambar + insert DB
│   ├── routes.py                              # daftar endpoint (mirip routes/api.php)
│   ├── database.py                            # koneksi SQLAlchemy + get_db()
│   ├── config.py                              # baca .env
│   └── main.py                                # entry point FastAPI
├── database/migrations/                       # Alembic (mirip database/migrations Laravel)
├── storage/captures/                          # gambar hasil capture disimpan di sini
├── .env.example
├── requirements.txt
├── run.sh                                     # Linux/Mac/Git Bash
└── run.bat                                    # Windows (cmd)
```

## 1. Siapkan PostgreSQL (Windows)

1. Install PostgreSQL (kalau belum): https://www.postgresql.org/download/windows/
2. Buat database lewat pgAdmin atau `psql`:
   ```sql
   CREATE DATABASE autogatedb;
   ```
3. Catat user/password yang dipakai untuk connection string.

## 2. Setup project

```bat
cd backend
copy .env.example .env
```

Edit `.env`:
- `DATABASE_URL` → sesuaikan user, password, host, nama database PostgreSQL kamu.
- Sistem sekarang pakai **2 kamera**: kamera **masuk** (`CAMERA_IN_*`) dan kamera
  **keluar** (`CAMERA_OUT_*`). Isi `CAMERA_IN_HOST`/`CAMERA_OUT_HOST` (dan user/password/
  channel kalau beda dari default) sesuai IP kedua kamera Hikvision kamu.
  `CAMERA_USER`/`CAMERA_PASSWORD`/`CAMERA_USE_HTTPS` di bagian atas dipakai sebagai
  fallback kalau `CAMERA_IN_*`/`CAMERA_OUT_*` tidak diisi.
- `UNKNOWN_PLATE_VALUES` → daftar nilai (pisah koma) yang dianggap "plat tidak terbaca".
  Kalau hasil ANPR kamera cocok salah satu nilai ini (atau kosong), request otomatis
  diabaikan dan tidak disimpan ke database.

## 3. Jalankan (Windows)

```bat
run.bat
```

Script ini otomatis: membuat virtualenv, install dependency, copy `.env` kalau belum ada,
menjalankan migration Alembic, lalu start server di `http://localhost:8000`.

Kalau mau jalankan manual step-by-step:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

> Catatan: saat startup, `app/main.py` juga otomatis memanggil `Base.metadata.create_all()`
> sebagai jaring pengaman development. Untuk workflow migration yang rapi
> (versioned, bisa di-rollback), tetap gunakan Alembic (`alembic revision`, `alembic upgrade head`).

## 4. Endpoint

### `GET /api/plates`
Mengambil semua data plat kendaraan yang tersimpan di database.

Query params opsional: `skip`, `limit` (pagination), `direction` (`masuk` atau `keluar`
— untuk filter per arah).

Response:
```json
{
  "total": 2,
  "items": [
    {
      "id": 1,
      "direction": "masuk",
      "plate_number": "AD1234XY",
      "plate_image_url": "/storage/captures/masuk_plate_ab12cd34.jpg",
      "scene_image_url": "/storage/captures/masuk_scene_ab12cd35.jpg",
      "confidence": 92.5,
      "captured_at": "2026-07-17T10:20:30",
      "created_at": "2026-07-17T10:20:31"
    }
  ]
}
```

Gambar bisa diakses langsung lewat `http://localhost:8000` + `plate_image_url` /
`scene_image_url`.

### `POST /api/plates/{direction}`
`direction` wajib salah satu dari `masuk` atau `keluar` — menentukan kamera mana
yang dipanggil (`CAMERA_IN_*` atau `CAMERA_OUT_*`).

Memicu kamera untuk mengambil hasil ANPR **terakhir** yang sudah terekam
(pakai endpoint `GET /ISAPI/Traffic/MNPR/channels/<channel>`, metode ini paling
stabil untuk "on demand"). Dari satu response kamera, backend mengambil **2 gambar
sekaligus**: foto crop plat nomor (`licensePlatePicture`) dan foto scene/kendaraan
penuh (`detectionPicture`), lalu:

1. Kalau plat nomor hasil ANPR kosong atau termasuk `UNKNOWN_PLATE_VALUES`
   (mis. "Unknown") → **diabaikan**, tidak ada yang disimpan, response `ignored: true`.
2. Kalau plat terbaca → simpan kedua gambar ke `storage/captures/`, lalu simpan
   `direction`, `plate_number`, `confidence`, `captured_at` ke tabel `vehicles`.

Body opsional (boleh dikosongkan):
```json
{ "channel": 1 }
```

Response `201` (plat terbaca):
```json
{
  "ignored": false,
  "reason": null,
  "vehicle": {
    "id": 3,
    "direction": "masuk",
    "plate_number": "AD1234XY",
    "plate_image_url": "/storage/captures/masuk_plate_ef56gh78.jpg",
    "scene_image_url": "/storage/captures/masuk_scene_ef56gh79.jpg",
    "confidence": 91.2,
    "captured_at": "2026-07-17T11:05:00",
    "created_at": "2026-07-17T11:05:01"
  }
}
```

Response `201` (plat unknown, diabaikan):
```json
{
  "ignored": true,
  "reason": "Plat nomor tidak terbaca (unknown) — diabaikan, tidak disimpan.",
  "vehicle": null
}
```

Kalau kamera tidak bisa dihubungi → `502`.
Kalau kamera terhubung tapi tidak mengirim gambar sama sekali → `422`.
Kalau `direction` bukan `masuk`/`keluar` → `422` (validasi path parameter).

## 5. Dokumentasi interaktif

Setelah server jalan, buka:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 6. Proteksi endpoint (opsional)

Isi `API_KEY` di `.env`, lalu di `app/routes.py` tambahkan
`dependencies=[Depends(verify_api_key)]` ke masing-masing route (import dari
`app.Http.Middleware.auth`). Client wajib kirim header `X-API-Key`.

## 7. Menambah tabel/migration baru

```bat
alembic revision -m "nama_migration"
```
Edit file yang muncul di `database/migrations/versions/`, lalu:
```bat
alembic upgrade head
```
