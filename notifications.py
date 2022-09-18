from config import TELEGRAM_BOT_TOKEN, DOMAIN, PORT, NOTIFICATION_CHAT_ID
from models import Page
import requests


def send_telegram_message(text: str):
    if not TELEGRAM_BOT_TOKEN or not NOTIFICATION_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={NOTIFICATION_CHAT_ID}" \
          f"&text={text}"
    requests.get(url)


def build_compare_url(old_page_id: int, new_page_id: int) -> str:
    return f"http://{DOMAIN}:{PORT}/compare/{old_page_id}/{new_page_id}/"


def build_changes_list_url(url_id: int) -> str:
    return f"http://{DOMAIN}:{PORT}/changes/{url_id}/"


def notify(old_page: Page, new_page: Page):
    compare_url = build_compare_url(old_page.id, new_page.id)
    changes_list_url = build_changes_list_url(old_page.url.id)
    notification_text = f"Page '{old_page.title}' - {old_page.url.url} was changed!\n" \
                        f"See comparing: {compare_url}\n" \
                        f"See changes list: {changes_list_url}"
    send_telegram_message(notification_text)
