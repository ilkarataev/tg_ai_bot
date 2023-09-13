import sys
sys.path.insert(0, "../")
from flask import Flask, make_response, abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin,AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from image_view import ImageView, ImageViewUsers
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

class RedirectToUsersAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return redirect(url_for('users.index_view'))

admin = Admin(app, name="tg_ai_bot", index_view=RedirectToUsersAdminIndexView())

@app.route('/admin/photo/<int:photo_id>')
def serve_photo(photo_id):
    photo = db.session.query(photos).get(photo_id)
    if photo and photo.photo:
        response = make_response(photo.photo)
        response.headers.set('Content-Type', 'image/jpeg')
        return response
    else:
        abort(404)

@app.route('/admin/users/<int:users_id>')
def serve_users_photo(users_id):
    photo = db.session.query(users).get(users_id)
    if photo and photo.photo:
        response = make_response(photo.photo)
        response.headers.set('Content-Type', 'image/jpeg')
        return response
    else:
        abort(404)
class MyView(ModelView):
    column_display_pk = True
    page_size = 10
    column_default_sort = ('id', True)
    column_exclude_list = ('email', 'notice')

from libs.db_class import users, photos, render_hosts, video_clips, payments
admin.add_view(ImageView(photos, db.session))
admin.add_view(ImageViewUsers(users, db.session))
admin.add_view(MyView(render_hosts, db.session))
admin.add_view(MyView(video_clips, db.session))
admin.add_view(MyView(payments, db.session))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
