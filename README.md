# AutoGate UNS

Sistem otomatisasi gerbang kampus UNS dengan ANPR (Automatic Number Plate Recognition).

## Arsitektur

Sistem ini terdiri dari 2 komponen utama yang terpisah:

```
┌─────────────────────────────────┐         ┌─────────────────────────────┐
│        POS SATPAM (Node)        │         │          SERVER             │
│     Lokasi: Gerbang/Gate        │  HTTP   │     Lokasi: Server Room     │
│                                 │────────▶│                             │
│  • FastAPI + SQLite             │         │  • FastAPI + PostgreSQL      │
│  • Kontrol kamera & relay       │         │  • Monitoring only           │
│  • Offline-first (queue sync)   │         │  • Terima data dari node     │
│  • Vue 3 Dashboard (port 3000)  │         │  • Vue 3 Dashboard (port 8000)│
└─────────────────────────────────┘         └─────────────────────────────┘
```

### Pembagian Tanggung Jawab

| Fitur | Pos Satpam (Node) | Server |
|-------|-------------------|--------|
| Database | SQLite (lokal) | PostgreSQL |
| Kontrol kamera | ✅ | ❌ |
| Kontrol relay/gate | ✅ | ❌ |
| Live stream kamera | ✅ | ❌ |
| Simpan data kendaraan | ✅ (lokal) | ✅ (terima dari node) |
| Status kamera & relay | ✅ (update) | ✅ (tampilan only) |
| Offline operation | ✅ | N/A |
| Sinkronisasi data | ✅ (kirim) | ✅ (terima) |

---

## Quick Start

### 1. Pos Satpam (Node)

```bash
cd node/backend

# Setup virtual environment
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy & edit .env
copy .env.example .env
# Edit .env sesuai konfigurasi kamera & relay

# Jalankan backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

```bash
cd node/frontend

# Install dependencies
npm install

# Jalankan frontend
npm run dev
# Buka http://localhost:5173
```

### 2. Server

```bash
cd server/backend

# Setup virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy & edit .env
copy .env.example .env

# Jalankan dengan Docker (PostgreSQL + Backend)
docker-compose up -d
atau docker up -d

# Atau jalankan manual (pastikan PostgreSQL sudah jalan)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
cd server/frontend

npm install
npm run dev
# Buka http://localhost:5174
```

---

## API Endpoints

### Pos Satpam (Port 3000)

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/plates` | List kendaraan lokal |
| POST | `/api/plates/{direction}` | Trigger kamera & simpan |
| POST | `/api/relay/control` | Kontrol relay (buka/tutup gate) |
| GET | `/api/stream/{direction}` | Snapshot kamera (JPEG) |
| GET | `/api/status` | Status kamera & relay |
| GET | `/api/sync/status` | Status sinkronisasi |
| POST | `/api/sync/manual` | Trigger sync manual |

### Server (Port 8000)

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/vehicles` | List kendaraan dari semua node |
| GET | `/api/vehicles?node_id=X` | Filter kendaraan per node |
| POST | `/api/sync/vehicles` | Terima data dari node |
| GET | `/api/nodes` | List semua node + status |
| GET | `/api/nodes/{id}` | Detail satu node |
| POST | `/api/nodes/register` | Registrasi node baru |
| PUT | `/api/nodes/{id}/status` | Update status node (heartbeat) |
| GET | `/api/dashboard/summary` | Ringkasan dashboard |

---

## Alur Kerja

### Normal (Server Online)
1. Kendaraan masuk → Kamera baca plat
2. Simpan ke SQLite lokal
3. Kirim ke server (POST /api/sync/vehicles)
4. Server simpan ke PostgreSQL

### Offline (Server Mati)
1. Kendaraan masuk → Kamera baca plat
2. Simpan ke SQLite lokal
3. Gagal kirim ke server → masuk antrian (`sync_queue`)
4. Gate tetap bisa dibuka/tutup (relay lokal)
5. Background task retry setiap 30 detik
6. Saat server hidup → data otomatis terkirim

---

## Konfigurasi

### Node ID
Setiap pos satpam punya ID unik di `.env`:
```env
NODE_ID=node-gerbang-depan
NODE_NAME=Gerbang Depan
```

### Autentikasi
Komunikasi node → server menggunakan API key:
```env
# Di node/.env
SERVER_API_KEY=your-secret-key

# Di server/.env
API_KEY=your-secret-key
```

---

## Struktur Folder

```
AutoGateUNS/
├── PLAN.md                          ← Dokumen perencanaan
├── README.md                        ← Dokumen ini
│
├── node/                            ← POS SATPAM
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── database.py          (SQLite)
│   │   │   ├── routes.py
│   │   │   ├── Models/
│   │   │   ├── Http/Controllers/
│   │   │   ├── Http/Requests/
│   │   │   └── Services/
│   │   │       ├── CameraService.py
│   │   │       ├── StreamService.py
│   │   │       ├── VehicleService.py
│   │   │       └── SyncService.py   ← Sinkronisasi ke server
│   │   ├── requirements.txt
│   │   └── .env.example
│   └── frontend/
│       ├── src/
│       │   ├── services/api.js
│       │   ├── views/DashboardView.vue
│       │   └── components/
│       │       ├── gate/GateCard.vue
│       │       └── sync/SyncStatus.vue
│       └── package.json
│
├── server/                          ← SERVER MONITORING
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── database.py          (PostgreSQL)
│   │   │   ├── routes.py
│   │   │   ├── Models/
│   │   │   │   ├── Vehicle.py
│   │   │   │   └── Node.py
│   │   │   ├── Http/Controllers/
│   │   │   │   ├── VehicleController.py
│   │   │   │   ├── SyncController.py
│   │   │   │   └── NodeController.py
│   │   │   └── Services/
│   │   ├── docker-compose.yml
│   │   ├── requirements.txt
│   │   └── .env.example
│   └── frontend/
│       ├── src/
│       │   ├── services/api.js
│       │   ├── views/DashboardView.vue
│       │   └── components/
│       │       ├── gate/GateStatusCard.vue
│       │       └── node/NodeStatusList.vue
│       └── package.json
```
