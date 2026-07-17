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
- `CAMERA_HOST`, `CAMERA_USER`, `CAMERA_PASSWORD`, `CAMERA_CHANNEL` → sesuai kamera Hikvision kamu (nilai default diambil dari script yang kamu berikan).

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

Query params opsional: `skip`, `limit` (pagination).

Response:
```json
{
  "total": 2,
  "items": [
    {
      "id": 1,
      "plate_number": "AD1234XY",
      "image_url": "/storage/captures/ab12cd34.jpg",
      "confidence": 92.5,
      "captured_at": "2026-07-17T10:20:30",
      "created_at": "2026-07-17T10:20:31"
    }
  ]
}
```

Gambar bisa diakses langsung lewat `http://localhost:8000` + `image_url`.

### `POST /api/plates`
Memicu kamera untuk mengambil hasil ANPR **terakhir** yang sudah terekam
(pakai endpoint `GET /ISAPI/Traffic/MNPR/channels/<channel>`, sesuai script yang
kamu berikan — metode ini paling stabil untuk "on demand"), lalu:
1. Simpan gambar ke `storage/captures/`
2. Simpan `plate_number`, `confidence`, `captured_at` ke tabel `vehicles`
3. Kembalikan data yang baru tersimpan

Body opsional (boleh dikosongkan):
```json
{ "channel": 1 }
```

Response `201`:
```json
{
  "id": 3,
  "plate_number": "AD1234XY",
  "image_url": "/storage/captures/ef56gh78.jpg",
  "confidence": 91.2,
  "captured_at": "2026-07-17T11:05:00",
  "created_at": "2026-07-17T11:05:01"
}
```

Kalau kamera tidak bisa dihubungi → `502`.
Kalau kamera terhubung tapi tidak ada plat pada hasil terakhir → `422`.

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
