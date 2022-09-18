from peewee import *
from datetime import datetime
from config import BASE_DIR
from os import path

db = SqliteDatabase(path.join(BASE_DIR, 'db.sqlite3'))


class BaseModel(Model):
    class Meta:
        database = db


class UrlRegex(BaseModel):
    regex = CharField()
    tag_id = CharField(null=True)
    active = BooleanField(default=True)


class SupervisedUrl(BaseModel):
    url = CharField(index=True)
    tag_id = CharField(null=True)


class Page(BaseModel):
    id = AutoField()
    url = ForeignKeyField(SupervisedUrl, backref='pages')
    title = CharField()
    full_content = TextField()
    suspect_hash = CharField()
    created_at = DateTimeField(default=datetime.now)

    def __repr__(self):
        return f"Page: {self.suspect_hash}"

    def __str__(self):
        return self.__repr__()


class PageChange(BaseModel):
    url = ForeignKeyField(SupervisedUrl, backref='changes')
    old_page = ForeignKeyField(Page)
    new_page = ForeignKeyField(Page)
    created_at = DateTimeField(default=datetime.now)

    def human_created_at(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        return f"PageChange: {self.old_page.title} - {self.created_at}"

    def __str__(self):
        return self.__repr__()


def init_db():
    db.connect()
    db.create_tables([UrlRegex, SupervisedUrl, Page, PageChange])
