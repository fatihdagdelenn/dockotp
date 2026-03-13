import json
import os
import time
from pathlib import Path

import pyotp
from flask import Flask, jsonify, redirect, render_template, request, send_file, url_for

app = Flask(__name__)

DATA_DIR = Path("/app/data")
CONFIG_FILE = DATA_DIR / "config.json"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def has_config() -> bool:
    return CONFIG_FILE.exists()


def load_config() -> dict:
    if not has_config():
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(name: str, secret: str) -> None:
    ensure_data_dir()
    data = {
        "name": name.strip(),
        "secret": secret.strip(),
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_totp():
    config = load_config()
    secret = config.get("secret", "").strip()
    if not secret:
        return None
    return pyotp.TOTP(secret)


@app.route("/")
def index():
    if not has_config():
        return redirect(url_for("setup"))
    config = load_config()
    return render_template("panel.html", name=config.get("name", "User"))


@app.route("/setup", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        secret = request.form.get("secret", "").strip()

        if not name or not secret:
            return render_template(
                "setup.html",
                error="İsim ve secret alanları zorunludur."
            )

        try:
            pyotp.TOTP(secret).now()
        except Exception:
            return render_template(
                "setup.html",
                error="Geçersiz TOTP secret girdiniz."
            )

        save_config(name, secret)
        return redirect(url_for("index"))

    return render_template("setup.html", error=None)


@app.route("/api/otp")
def api_otp():
    if not has_config():
        return jsonify({"error": "setup_required"}), 400

    totp = get_totp()
    if not totp:
        return jsonify({"error": "invalid_secret"}), 400

    now_ts = int(time.time())
    remaining = 30 - (now_ts % 30)

    return jsonify({
        "name": load_config().get("name", "User"),
        "now": totp.now(),
        "prev": totp.at(now_ts - 30),
        "next": totp.at(now_ts + 30),
        "remaining": remaining
    })


@app.route("/download/trayapp.ps1")
def download_trayapp():
    script = r'''# totp-tray.ps1
$ErrorActionPreference = "SilentlyContinue"

$ApiUrl = "http://localhost:8080/api/otp"
$PanelUrl = "http://localhost:8080/"
$RefreshSeconds = 3

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$global:LastCode = ""
$global:LastRemaining = 0

function Get-Otp {
    try {
        $resp = Invoke-RestMethod -Uri $ApiUrl -Method Get -TimeoutSec 3
        return $resp
    } catch {
        return $null
    }
}

function Update-Tooltip($ni) {
    $data = Get-Otp
    if ($null -eq $data) {
        $ni.Text = "TOTP: API yok"
        return
    }

    $global:LastCode = [string]$data.now
    $global:LastRemaining = [int]$data.remaining
    $ni.Text = ("TOTP: {0} | {1}s" -f $global:LastCode, $global:LastRemaining)
}

function Copy-Code($ni) {
    if ([string]::IsNullOrWhiteSpace($global:LastCode)) {
        $data = Get-Otp
        if ($null -ne $data) {
            $global:LastCode = [string]$data.now
            $global:LastRemaining = [int]$data.remaining
        }
    }

    if ([string]::IsNullOrWhiteSpace($global:LastCode)) {
        $ni.ShowBalloonTip(1200, "TOTP", "Kod alınamadı.", [System.Windows.Forms.ToolTipIcon]::Warning)
        return
    }

    Set-Clipboard -Value $global:LastCode
    $ni.ShowBalloonTip(900, "TOTP", ("Kopyalandı: {0}  (kalan {1}s)" -f $global:LastCode, $global:LastRemaining), [System.Windows.Forms.ToolTipIcon]::Info)
}

$notifyIcon = New-Object System.Windows.Forms.NotifyIcon
$notifyIcon.Icon = [System.Drawing.SystemIcons]::Shield
$notifyIcon.Visible = $true
$notifyIcon.Text = "TOTP: Başlatılıyor..."

$menu = New-Object System.Windows.Forms.ContextMenuStrip

$itemCopy = New-Object System.Windows.Forms.ToolStripMenuItem
$itemCopy.Text = "Kodu kopyala"
$itemCopy.Add_Click({ Copy-Code $notifyIcon })

$itemOpen = New-Object System.Windows.Forms.ToolStripMenuItem
$itemOpen.Text = "Paneli aç"
$itemOpen.Add_Click({ Start-Process $PanelUrl })

$itemExit = New-Object System.Windows.Forms.ToolStripMenuItem
$itemExit.Text = "Çıkış"
$itemExit.Add_Click({
    $timer.Stop()
    $notifyIcon.Visible = $false
    $notifyIcon.Dispose()
    [System.Windows.Forms.Application]::Exit()
})

$menu.Items.Add($itemCopy) | Out-Null
$menu.Items.Add($itemOpen) | Out-Null
$menu.Items.Add($itemExit) | Out-Null

$notifyIcon.ContextMenuStrip = $menu

$notifyIcon.Add_MouseUp({
    param($sender, $e)
    if ($e.Button -eq [System.Windows.Forms.MouseButtons]::Left) {
        Copy-Code $notifyIcon
    }
})

$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = $RefreshSeconds * 1000
$timer.Add_Tick({ Update-Tooltip $notifyIcon })
$timer.Start()

Update-Tooltip $notifyIcon
[System.Windows.Forms.Application]::Run()
'''

    temp_file = DATA_DIR / "totp-tray.ps1"
    ensure_data_dir()
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(script)

    return send_file(
        temp_file,
        as_attachment=True,
        download_name="totp-tray.ps1",
        mimetype="text/plain"
    )


@app.route("/reset", methods=["POST"])
def reset():
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
    return redirect(url_for("setup"))


if __name__ == "__main__":
    ensure_data_dir()
    app.run(host="0.0.0.0", port=8080)
