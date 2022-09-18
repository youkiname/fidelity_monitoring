from app import app
from models import init_db
import config


if __name__ == '__main__':
    init_db()
    app.run(config.DOMAIN, port=config.PORT)
