"""
Skrip cetak karcis yang dijalankan sebagai subprocess terpisah.
Dipanggil oleh PaymentController via subprocess.Popen agar 
Windows Print Spooler berjalan di proses baru (bukan FastAPI thread).
"""
import sys
import os
from datetime import datetime

# Tambahkan path backend ke sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from app.config import settings
import qrcode
import win32con
import win32ui
from PIL import Image, ImageWin


def _font(device, size: int, bold: bool = False):
    return win32ui.CreateFont({
        "name": "Arial",
        "height": -size,
        "weight": 700 if bold else 400,
    })


def _draw_image(device, image: Image.Image, x: int, y: int, width: int, height: int):
    image = image.convert("RGB").resize((width, height))
    dib = ImageWin.Dib(image)
    dib.draw(device.GetHandleOutput(), (x, y, x + width, y + height))


def cetak(ticket_code: str, payment_url: str, plate_number: str):
    printer_name = settings.PRINTER_NAME
    if not printer_name:
        raise RuntimeError("PRINTER_NAME wajib diisi untuk printer driver LABEL")

    qr_image = qrcode.make(payment_url).convert("RGB")
    device = win32ui.CreateDC()
    device.CreatePrinterDC(printer_name)

    try:
        dpi_x = device.GetDeviceCaps(win32con.LOGPIXELSX)
        dpi_y = device.GetDeviceCaps(win32con.LOGPIXELSY)
        page_width = device.GetDeviceCaps(win32con.HORZRES)
        page_height = device.GetDeviceCaps(win32con.VERTRES)
        mm = lambda value, dpi: int(value * dpi / 25.4)
        margin = mm(6, dpi_x)
        qr_size = min(mm(48, dpi_x), page_width - (margin * 2))
        barcode_width = page_width - (margin * 2)
        barcode_height = mm(24, dpi_y)
        y = margin

        device.StartDoc(f"Karcis {ticket_code}")
        device.StartPage()

        def text(value, size=10, bold=False, center=False, gap=0):
            nonlocal y
            font = _font(device, size, bold)
            old_font = device.SelectObject(font)
            flags = win32con.DT_CENTER if center else win32con.DT_LEFT
            rect = (margin, y, page_width - margin, y + mm(size * 0.6 + 6, dpi_y))
            device.DrawText(value, rect, flags | win32con.DT_SINGLELINE)
            device.SelectObject(old_font)
            y = rect[3] + gap

        text("MUSEUM AUTOGATE", 18, True, True, mm(2, dpi_y))
        text("Karcis Parkir Otomatis", 11, False, True, mm(5, dpi_y))
        text(f"Plat Nomor : {plate_number}", 11, True, False)
        text(f"Kode Tiket : {ticket_code}", 11, False, False)
        text(f"Waktu      : {datetime.now().strftime('%d-%m-%Y %H:%M')}", 10, False, False, mm(3, dpi_y))
        text("SCAN HP UNTUK BAYAR", 11, True, True, mm(2, dpi_y))
        _draw_image(device, qr_image, (page_width - qr_size) // 2, y, qr_size, qr_size)
        device.EndPage()
        device.EndDoc()
        print("[PRINTER] Karcis berhasil dicetak!")
    finally:
        device.DeleteDC()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: print_ticket.py <ticket_code> <payment_url> <plate_number>")
        sys.exit(1)

    try:
        cetak(sys.argv[1], sys.argv[2], sys.argv[3])
    except Exception as error:
        print(f"[PRINTER ERROR] {error}", file=sys.stderr)
        sys.exit(1)
