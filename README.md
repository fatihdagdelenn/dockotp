# DockOTP

Docker tabanlı lokal TOTP üretici.

Telefon authenticator kullanmak istemeyenler için
yerel çalışan küçük bir OTP paneli ve Windows tray uygulaması sağlar.

## Özellikler

- Docker ile çalışır
- Secret lokal makinede saklanır
- Web panel üzerinden OTP görüntüleme
- `/api/otp` endpoint
- Windows tray app
- Clipboard ile hızlı MFA giriş

## Gereksinimler

- Docker Desktop
- Windows / Linux / macOS

## Kurulum

Projeyi indirin.

Sonra:
scripts/install.bat


Çalıştırın.

Tarayıcı açılacaktır:


http://localhost:8080


İlk açılışta:

- isim
- TOTP secret

girmeniz istenir.

## Tray App

Panelden indirilebilir:
veya direkt:


http://localhost:8080/download/trayapp.ps1


Çalıştırmak için:

powershell.exe -ExecutionPolicy Bypass -File totp-tray.ps1


## Tray App Kullanımı

- Sağ altta kalkan simgesi oluşur
- Sol tık → OTP kopyalanır
- Sağ tık → panel aç / çıkış

## Güvenlik

- Secret Docker volume içinde tutulur
- Uygulama sadece localhost üzerinden erişilebilir
- İnternete açık değildir

## API
GET /api/otp


örnek çıktı:

GET /api/otp


örnek çıktı:

```json
{
  "name": "Fatih",
  "now": "123456",
  "prev": "654321",
  "next": "111222",
  "remaining": 18
}
```
Container Yönetimi

Başlat:

scripts/start.bat

Durdur:

scripts/stop.bat

Kaldır:

scripts/uninstall.bat
Lisans

MIT
