from bs4 import BeautifulSoup
import requests
import hashlib
from models import Page, SupervisedUrl, PageChange, init_db
from time import sleep
from notifications import notify
import config


class ParsedData:
    def __init__(self, url: str, title: str, full_content: str, suspect_hash: str):
        self.url = url
        self.title = title
        self.full_content = full_content
        self.suspect_hash = suspect_hash

    def __str__(self):
        return f"ParsedData: {self.suspect_hash}"


def get_md5(s: str) -> str:
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def remove_script_tags(html) -> BeautifulSoup:
    soup = BeautifulSoup(html, "html.parser")
    for s in soup.select('script'):
        s.extract()
    return soup


def parse(url: SupervisedUrl) -> ParsedData:
    html_text = requests.get(url.url).text
    result_html = remove_script_tags(html_text)
    title = result_html.find('title').string
    suspect_container = result_html
    if url.tag_id:
        suspect_container = suspect_container.find('div', {'id': url.tag_id})
    return ParsedData(url.url, title, str(result_html), get_md5(str(suspect_container)))


def save_new_page(supervised_url: SupervisedUrl, parsed_data: ParsedData) -> Page:
    print(f"Save new Page: {parsed_data.url}")
    return Page.create(
        url=supervised_url,
        title=parsed_data.title,
        full_content=parsed_data.full_content,
        suspect_hash=parsed_data.suspect_hash)


def save_page_change(old_page: Page, new_page: Page, url: SupervisedUrl):
    return PageChange.create(
        old_page=old_page,
        new_page=new_page,
        url=url,
    )


def try_save_new_page(supervised_url: SupervisedUrl):
    parsed_data = parse(supervised_url)
    old_page = Page.select()\
        .where(Page.url == supervised_url)\
        .order_by(Page.created_at.desc())\
        .get_or_none()
    if old_page is None:
        return save_new_page(supervised_url, parsed_data)
    if parsed_data.suspect_hash != old_page.suspect_hash:
        new_page = save_new_page(supervised_url, parsed_data)
        save_page_change(old_page, new_page, supervised_url)
        notify(old_page, new_page)
        return


def start_parser():
    try:
        while True:
            for supervised_url in SupervisedUrl.select():
                print(f"Check {supervised_url.url}")
                try_save_new_page(supervised_url)
                sleep(config.PARSER_PAGE_DELAY)
            sleep(config.PARSER_LOOP_DELAY)
    except KeyboardInterrupt:
        print('interrupted!')


if __name__ == '__main__':
    init_db()
    start_parser()
