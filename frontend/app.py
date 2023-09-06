import sys
sys.path.insert(0, "../")
from flask import Flask, make_response, abort
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from image_view import ImageView
from os import path,environ
import os
from sqlalchemy import engine_from_config, pool, create_engine
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '../.env'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://%s:%s@%s:%s/%s" % (
        os.getenv("DATABASE_USERNAME", "vagrant"), 
        os.getenv("DATABASE_PASSWORD", "vagrant"), 
        os.getenv("DATABASE_HOST", "localhost"),
        os.getenv("DATABASE_PORT", "3306"),
        os.getenv("DATABASE_NAME", "ai_bot")
)

app.config['SECRET_KEY'] = os.getenv('FRONTEND_SECRET_KEY', 'fallback_secret_key')

db = SQLAlchemy(app)
admin = Admin(app)
# image_path = 'static/images/'  # путь для сохранения изображений

@app.route('/admin/photo/<int:photo_id>')
def serve_photo(photo_id):
    photo = db.session.query(Photos).get(photo_id)  # Измените эту строку
    if photo and photo.photo:
        # with open(f'{image_path}/photo_{photo_id}.jpg', 'wb') as f:
        #     f.write(photo.photo)
        #     print(f"Image saved to {image_path}")
        response = make_response(photo.photo)
        response.headers.set('Content-Type', 'image/jpeg')  # или другой подходящий MIME-тип
        return response
    else:
        abort(404)

class PaginatedModelView(ModelView):
    page_size = 5  # количество записей на одной странице

from libs.db_class import Photos, Users, render_hosts, video_clips, payments
admin.add_view(ImageView(Photos, db.session))
admin.add_view(ModelView(Users, db.session))
admin.add_view(ModelView(render_hosts, db.session))
admin.add_view(ModelView(video_clips, db.session))
admin.add_view(ModelView(payments, db.session))

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=False)
