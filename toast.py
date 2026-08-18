import os
import sys
from pathlib import Path
import winsdk.windows.ui.notifications as notifications
import winsdk.windows.data.xml.dom as dom

APP_ID = "Binance.PriceAlert"

def show_price_toast(symbol: str, target: float, current: float, direction: str):
    pair = symbol.upper()
    arrow = "^" if direction == "above" else "v"
    title = f"{pair} {arrow} {target}"
    message = f"Price crossed threshold! Current: {current}"

    xml_str = f"""
    <toast>
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
