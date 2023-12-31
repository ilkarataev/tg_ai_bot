from flask_admin.contrib.sqla import ModelView
from flask_admin import form
from markupsafe import Markup
from flask import url_for
import os
# from flask_admin.contrib.sqla.filters import FilterEqual
# from libs.db_class import users
class ImageView(ModelView):
    page_size = 10
    @staticmethod
    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''

        return Markup('<img src="%s" width="100">' % url_for('serve_photo', photo_id=model.id))
    column_display_pk = True
    column_formatters = {
        'photo': _list_thumbnail
    }
    column_default_sort = ('id', True)

    def on_model_change(self, form, model, is_created):
        if form.photo.data:
            file_data = form.photo.data
            file_name = form.photo.data.filename
            file_data.save(os.path.join(self.file_path, file_name))
            model.photo = file_name
# class StatusFilter(FilterEqual):
#     def get_options(self, view):
#         return [('сomplete', 'сomplete'), ('rendring', 'rendring'), ('rendring_error', 'rendring_error')]
class ImageViewUsers(ModelView):
    page_size = 10
    @staticmethod
    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''

        return Markup('<img src="%s" width="100">' % url_for('serve_users_photo', users_id=model.id))
    column_display_pk = True
    column_formatters = {
        'photo': _list_thumbnail
    }
    column_default_sort = ('id', True)
    form_excluded_columns = ['photo']
    inline_models = None
    column_exclude_list = ('email', 'notice')
    column_searchable_list = ['status']
    # column_filters = [StatusFilter(column=users.status, name='Status')]

