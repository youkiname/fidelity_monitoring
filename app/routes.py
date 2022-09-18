from app import app
from flask import render_template, redirect, request, abort
from models import Page, SupervisedUrl, UrlRegex, PageChange
import re


def check_url_regex(url: str) -> UrlRegex or None:
    """:returns UrlRegex if url passes through some saved regex"""
    for regex in UrlRegex.select().where(UrlRegex.active == 1):
        print("^" + regex.regex)
        if re.search("^" + regex.regex, url):
            return regex
    return None


@app.route('/')
def home():
    return render_template('home.html', **{
        'url_regexes': UrlRegex.select(),
        'supervised_urls': SupervisedUrl.select()
    })


@app.route("/compare/<int:old_page_id>/<int:new_page_id>/")
def compare(old_page_id, new_page_id):
    old_page = Page.get(Page.id == old_page_id)
    new_page = Page.get(Page.id == new_page_id)
    return render_template('comparing.html', **{
        'old_html': old_page.full_content,
        'new_html': new_page.full_content,
        'old_page_id': old_page.id,
        'new_page_id': new_page.id
    })


@app.route("/compare/code/<int:old_page_id>/<int:new_page_id>/")
def code(old_page_id, new_page_id):
    old_page = Page.get(Page.id == old_page_id)
    new_page = Page.get(Page.id == new_page_id)
    return render_template('code_comparing.html', **{
        'old_html': old_page.full_content,
        'new_html': new_page.full_content,
        'old_page_id': old_page.id,
        'new_page_id': new_page.id
    })


@app.route("/changes/<int:url_id>/")
def page_changes(url_id: int):
    url = SupervisedUrl.get(url_id)
    changes = PageChange.select()\
        .where(PageChange.url == url)\
        .order_by(PageChange.created_at.desc())
    return render_template('page_changes.html', **{
        'url': url,
        'changes': changes,
        'changes_amount': len(changes)
    })


@app.route('/add-url-regex/', methods=['POST'])
def add_url_regex():
    regex = request.form.get('regex')
    tag_id = request.form.get('tag_id')
    if not regex:
        return redirect('/')
    UrlRegex.create(regex=regex, tag_id=tag_id)
    return redirect('/')


@app.route('/delete-url-regex/<int:regex_id>/')
def delete_url_regex(regex_id: int):
    url_regex = UrlRegex.get(regex_id)
    url_regex.delete_instance()
    return redirect('/')


@app.route('/disable-url-regex/<int:regex_id>/')
def disable_url_regex(regex_id: int):
    url_regex = UrlRegex.get(regex_id)
    url_regex.active = False
    url_regex.save()
    return redirect('/')


@app.route('/enable-url-regex/<int:regex_id>/')
def enable_url_regex(regex_id: int):
    url_regex = UrlRegex.get(regex_id)
    url_regex.active = True
    url_regex.save()
    return redirect('/')


@app.route('/add-url-auto/', methods=['POST'])
def add_supervised_url_automatically():
    url = request.json.get('url', None)
    if not url:
        return abort(400)
    if SupervisedUrl.select().where(SupervisedUrl.url == url).exists():
        return abort(409)
    url_regex = check_url_regex(url)
    if url_regex is None:
        return abort(409)
    SupervisedUrl.create(url=url, tag_id=url_regex.tag_id)
    return ""


@app.route('/add-url/', methods=['POST'])
def add_supervised_url():
    url = request.form.get('url')
    tag_id = request.form.get('tag_id')
    if not url:
        return redirect('/')
    SupervisedUrl.create(url=url, tag_id=tag_id)
    return redirect('/')


@app.route('/delete-url/<int:url_id>/', methods=['POST', 'GET'])
def delete_supervised_url(url_id: int):
    SupervisedUrl.delete().where(SupervisedUrl.id == url_id).execute()
    return redirect('/')
