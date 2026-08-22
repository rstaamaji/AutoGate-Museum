# AutoGate Parkir

Sistem otomatisasi gerbang parkir (mall-style) dengan ANPR (Automatic Number Plate Recognition) dan pembayaran non-tunai berbasis e-money (mirip e-toll) yang terintegrasi dengan **Midtrans**.

## Arsitektur

Sistem ini terdiri dari 3 komponen utama yang terpisah:

```
┌─────────────────────────────────┐         ┌─────────────────────────────┐         ┌──────────────────────────┐
│        POS SATPAM (Node)        │         │          SERVER             │         │        MIDTRANS         │
│     Lokasi: Gerbang/Gate        │  HTTP   │     Lokasi: Server Room     │  HTTP   │   Payment Gateway (3rd)  │
│                                 │────────▶│                             │────────▶│                          │
│  • FastAPI + SQLite             │         │  • FastAPI + PostgreSQL      │         │  • Snap / Core API       │
│  • Kontrol kamera & relay       │         │  • Monitoring + Billing      │◀────────│  • Notifikasi webhook    │
│  • Offline-first (queue sync)   │         │  • Terima data dari node     │         │  • Top-up saldo e-money  │
│  • Vue 3 Dashboard (port 3000)  │         │  • Vue 3 Dashboard (port 8000)│         └──────────────────────────┘
└─────────────────────────────────┘         └─────────────────────────────┘
```

### Pembagian Tanggung Jawab

| Fitur | Pos Satpam (Node) | Server | Midtrans |
|-------|-------------------|--------|----------|
| Database | SQLite (lokal) | PostgreSQL | - |
| Kontrol kamera | ✅ | ❌ | ❌ |
| Kontrol relay/gate | ✅ | ❌ | ❌ |
| Live stream kamera | ✅ | ❌ | ❌ |
| Simpan data kendaraan | ✅ (lokal) | ✅ (terima dari node) | ❌ |
| Status kamera & relay | ✅ (update) | ✅ (tampilan only) | ❌ |
| Offline operation | ✅ | N/A | ❌ |
| Sinkronisasi data | ✅ (kirim) | ✅ (terima) | ❌ |
| Hitung tarif parkir | ✅ | ✅ (rekap) | ❌ |
| Cek saldo e-money | ✅ (cache lokal) | ✅ (master saldo) | ❌ |
| Potong saldo saat keluar | ✅ (request ke server) | ✅ (eksekusi debit) | ❌ |
| Top-up saldo | ❌ | ✅ (buat transaksi) | ✅ (proses pembayaran) |
| Notifikasi status bayar | ❌ | ✅ (terima webhook) | ✅ (kirim webhook) |

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
# Edit .env sesuai konfigurasi kamera, relay, & tarif parkir

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
# Isi kredensial Midtrans (Server Key, Client Key, mode: sandbox/production)

# Jalankan dengan Docker (PostgreSQL + Backend)
docker-compose up -d

# Atau jalankan manual (pastikan PostgreSQL sudah jalan)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
cd server/frontend

npm install
npm run dev
# Buka http://localhost:5174
```

### 3. Konfigurasi Midtrans

1. Daftar akun di [Midtrans Dashboard](https://dashboard.midtrans.com) (mode Sandbox untuk development).
2. Ambil **Server Key** dan **Client Key** dari menu Settings > Access Keys.
3. Set Payment Notification URL di dashboard Midtrans ke endpoint webhook server: `https://domain-kamu/api/payment/notification`.
4. Masukkan key ke `server/.env`:
   ```env
   MIDTRANS_SERVER_KEY=your-server-key
   MIDTRANS_CLIENT_KEY=your-client-key
   MIDTRANS_IS_PRODUCTION=false
   ```

---

## API Endpoints

### Pos Satpam (Port 3000)

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/plates` | List kendaraan lokal |
| POST | `/api/plates/{direction}` | Trigger kamera & simpan (masuk/keluar) |
| POST | `/api/relay/control` | Kontrol relay (buka/tutup gate) |
| GET | `/api/stream/{direction}` | Snapshot kamera (JPEG) |
| GET | `/api/status` | Status kamera & relay |
| GET | `/api/sync/status` | Status sinkronisasi |
| POST | `/api/sync/manual` | Trigger sync manual |
| POST | `/api/payment/charge` | Request potong saldo e-money saat kendaraan keluar |
| GET | `/api/payment/balance/{card_id}` | Cek saldo kartu e-money (cache lokal) |

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
| GET | `/api/dashboard/summary` | Ringkasan dashboard (termasuk pendapatan) |
| POST | `/api/payment/topup` | Buat transaksi top-up via Midtrans (Snap token) |
| POST | `/api/payment/notification` | Webhook callback dari Midtrans (update status transaksi) |
| POST | `/api/payment/debit` | Eksekusi potong saldo saat kendaraan keluar |
| GET | `/api/payment/transactions` | Riwayat transaksi (top-up & pembayaran parkir) |
| GET | `/api/payment/card/{card_id}` | Detail saldo & histori kartu e-money |

---

## Alur Kerja

### Kendaraan Masuk
1. Kendaraan masuk → Kamera baca plat
2. Simpan ke SQLite lokal (status: `di_dalam`)
3. Gate terbuka otomatis (relay)
4. Kirim data ke server (sinkron)

### Kendaraan Keluar (dengan Pembayaran E-Money)
1. Kamera baca plat saat kendaraan di gerbang keluar
2. Sistem hitung durasi parkir & tarif
3. Kartu e-money di-tap → Node kirim request debit ke Server (`/api/payment/debit`)
4. Server cek saldo kartu:
   - **Cukup** → saldo dipotong, gate dibuka, transaksi dicatat
   - **Tidak cukup** → gate tetap tertutup, tampil notifikasi "saldo tidak cukup, silakan top-up"
5. Struk/histori transaksi tersimpan di server

### Top-up Saldo E-Money (via Midtrans)
1. User pilih nominal top-up di dashboard/aplikasi
2. Server buat transaksi via Midtrans Snap API → dapat `snap_token` & redirect URL
3. User bayar (QRIS, VA, e-wallet, dll — tergantung metode yang diaktifkan di Midtrans)
4. Midtrans kirim webhook notifikasi ke `/api/payment/notification`
5. Server verifikasi signature notifikasi, update status transaksi, tambah saldo kartu jika `settlement`/`capture`

### Offline (Server Mati)
1. Kendaraan masuk/keluar → Kamera baca plat
2. Simpan ke SQLite lokal
3. Gagal kirim ke server → masuk antrian (`sync_queue`)
4. Gate tetap bisa dibuka/tutup pakai saldo cache lokal (mode darurat, dengan batas nominal)
5. Background task retry setiap 30 detik
6. Saat server hidup → data & transaksi otomatis terkirim dan direkonsiliasi

---

## Konfigurasi

### Node ID
Setiap pos satpam punya ID unik di `.env`:
```env
NODE_ID=node-gerbang-parkir-1
NODE_NAME=Gerbang Masuk Utama
```

### Tarif Parkir
```env
# Di node/.env
TARIF_JAM_PERTAMA=3000
TARIF_JAM_BERIKUTNYA=2000
TARIF_MAKSIMAL_HARIAN=25000
```

### Autentikasi
Komunikasi node → server menggunakan API key:
```env
# Di node/.env
SERVER_API_KEY=your-secret-key

# Di server/.env
API_KEY=your-secret-key
```

### Midtrans
```env
# Di server/.env
MIDTRANS_SERVER_KEY=your-server-key
MIDTRANS_CLIENT_KEY=your-client-key
MIDTRANS_IS_PRODUCTION=false
MIDTRANS_NOTIFICATION_URL=https://domain-kamu/api/payment/notification
```

---

## Struktur Folder

```
AutoGateParkir/
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
│   │   │       ├── TarifService.py      ← Hitung tarif parkir
│   │   │       ├── PaymentService.py    ← Request debit e-money ke server
│   │   │       └── SyncService.py       ← Sinkronisasi ke server
│   │   ├── requirements.txt
│   │   └── .env.example
│   └── frontend/
│       ├── src/
│       │   ├── services/api.js
│       │   ├── views/DashboardView.vue
│       │   └── components/
│       │       ├── gate/GateCard.vue
│       │       ├── sync/SyncStatus.vue
│       │       └── payment/PaymentCard.vue   ← Tampilan tap kartu & saldo
│       └── package.json
│
├── server/                          ← SERVER MONITORING & BILLING
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── database.py          (PostgreSQL)
│   │   │   ├── routes.py
│   │   │   ├── Models/
│   │   │   │   ├── Vehicle.py
│   │   │   │   ├── Node.py
│   │   │   │   ├── Card.py              ← Kartu e-money & saldo
│   │   │   │   └── Transaction.py       ← Riwayat top-up & pembayaran
│   │   │   ├── Http/Controllers/
│   │   │   │   ├── VehicleController.py
│   │   │   │   ├── SyncController.py
│   │   │   │   ├── NodeController.py
│   │   │   │   └── PaymentController.py ← Integrasi Midtrans
│   │   │   └── Services/
│   │   │       └── MidtransService.py   ← Wrapper Midtrans Snap/Core API
│   │   ├── docker-compose.yml
│   │   ├── requirements.txt
│   │   └── .env.example
│   └── frontend/
│       ├── src/
│       │   ├── services/api.js
│       │   ├── views/DashboardView.vue
│       │   └── components/
│       │       ├── gate/GateStatusCard.vue
│       │       ├── node/NodeStatusList.vue
│       │       └── payment/TransactionList.vue  ← Riwayat transaksi
│       └── package.json
```

---

## Catatan

Project ini dikembangkan berdasarkan struktur sistem AutoGate Museum, disesuaikan untuk konteks parkir mall dengan tambahan modul pembayaran e-money (mirip e-toll) yang terintegrasi dengan Midtrans sebagai payment gateway.
