import html
import os
import subprocess
import sys
from pathlib import Path
import winsdk.windows.ui.notifications as notifications
import winsdk.windows.data.xml.dom as dom

APP_ID = "Binance.PriceAlert"

def _register_shortcut():
    # Windows notifications require a Start Menu shortcut to handle clicks reliably
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return
    
    lnk_path = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Binance Price Alert.lnk"
    if lnk_path.exists():
        return

    ps_cmd = f"""
    $Path = "{lnk_path}"
    $Target = "{sys.executable}"
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($Path)
    $Shortcut.TargetPath = $Target
    $Shortcut.Arguments = "-m price_alert.stream"
    $Shortcut.Save()
    """
    try:
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, check=True)
    except Exception:
        # Don't fail block if we cannot write shortcut (e.g. read-only profiles)
        pass

def show_price_toast(symbol: str, target: float, current: float, direction: str):
    """Triggers a native Windows toast notification with a clickable link to Binance."""
    _register_shortcut()

    pair = symbol.upper()
    if pair.endswith("USDT"):
        base = pair[:-4]
        trade_url = f"https://www.binance.com/en/trade/{base}_USDT?type=spot"
    elif pair.endswith("BUSD"):
        base = pair[:-4]
        trade_url = f"https://www.binance.com/en/trade/{base}_BUSD?type=spot"
    else:
        trade_url = f"https://www.binance.com/en/trade/{pair}?type=spot"

    # print(f"DEBUG: sending toast for {symbol} to {trade_url}")
    escaped_url = html.escape(trade_url)
    arrow = "▲" if direction == "above" else "▼"
    title = f"{pair} {arrow} {target}"
    message = f"Price crossed threshold! Current: {current}"

    xml_str = f"""
    <toast launch="{escaped_url}">
        <visual>
            <binding template="ToastGeneric">
                <text>{title}</text>
                <text>{message}</text>
            </binding>
        </visual>
    </toast>
    """

    xml_doc = dom.XmlDocument()
    xml_doc.load_xml(xml_str)

    notifier = notifications.ToastNotificationManager.create_toast_notifier(APP_ID)
    notification = notifications.ToastNotification(xml_doc)
    notifier.show(notification)
