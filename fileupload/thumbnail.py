import os
import re
import uuid
import mimetypes
import PIL.Image as IM
from PIL.Image import Image

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import File

from fileupload.serialize import serialize as fileupload_serialize
from .serialize import serialize
from fileupload import constants


THUMBNAIL_FORMAT_SUFFIX = '.png'
THUMBNAIL_SUB_DIR_PART = '/thumbnail/'

hosted_file_type_icons = {
    # 'doc': '.doc',
    # 'xls': '.xls',
    # 'zip': '.zip',
    # 'rar': '.rar'
}

# Wrap-up the original 'serialize' function to incorporate
# thumbnail feature
def serialize(instance, file_attr='file'):
    result = fileupload_serialize(instance, file_attr)
    file_url = result.get('url')
    result.update({
        'thumbnailUrl': get_thumbnail_url(file_url)
    })
    return result


# Generate thumbnail for uploaded images
def get_thumbnail_url(file_url):
    mime_type = mimetypes.guess_type(file_url)[0]
    if mime_type and mime_type.partition(r'/')[0] == 'image':
        # ONLY generate/fetch thumbnail for image files
        thumbnail_url = get_image_thumb_url(file_url)
    else:
        # Get thumb-icon according to extensions
        name, sep, ext = file_url.rpartition(r'.')
        if sep:
            thumbnail_url = get_icon_thumb_url(ext)
        else:
            thumbnail_url = get_default_thumbnail_url()
    return thumbnail_url

def cleanup_attachment(instance, file_attr='file'):
    obj = getattr(instance, file_attr)
    mimetype = mimetypes.guess_type(obj.name)[0] or 'image/png'
    if re.match(r'image', mimetype):
        remove_thumbnail(strip_media_prefix(obj.url))

def thumb_url_from_file(file_url):
    if file_url:
        dir_prefix, file_name = file_url.rsplit(r'/', 1)
        thumb_dir = dir_prefix + '/thumbnail/'
        if not default_storage.exists(thumb_dir):
            os.mkdir(os.path.join(settings.MEDIA_ROOT, thumb_dir))
        thumb_url = thumb_dir + file_name.rsplit(r'.', 1)[0] + THUMBNAIL_FORMAT_SUFFIX
        return thumb_url

def strip_media_prefix(file_url):
    _, _, striped_url = file_url.partition(settings.MEDIA_URL)
    return striped_url or file_url

def get_image_thumb_url(file_url):
    rel_file_url = strip_media_prefix(file_url)
    thumb_url = thumb_url_from_file(rel_file_url)
    if not default_storage.exists(thumb_url):
        dj_thumb = default_storage.open(thumb_url, mode='wb')
        dj_file = default_storage.open(rel_file_url, mode='rb')
        if not generate_thumbnail(dj_file.file, dj_thumb.file):
            return get_default_thumbnail_url()
    return settings.MEDIA_URL + thumb_url

def remove_thumbnail(file_url):
    thumb_url = thumb_url_from_file(file_url)
    if default_storage.exists(thumb_url):
        default_storage.delete(thumb_url)

def generate_thumbnail(file_obj, thumb_obj, bound_size=128):

    try:
        bound_box = (bound_size, bound_size)
        img = IM.open(file_obj).convert('RGBA')
        bg_img = IM.new('RGBA', bound_box, (255, 255, 255, 128))
    except Exception as e:
        print('Failed to generate thumbnail:\n\t{}'.format(e))
        return False
    else:
        thumb = img.copy()
        thumb.thumbnail(bound_box)
        bg_img.paste(thumb, ((bound_size - thumb.width) // 2, (bound_size - thumb.height) // 2), thumb)
        bg_img.save(thumb_obj, 'PNG')
    return True

def get_icon_thumb_url(file_ext):
    if file_ext:
        if file_ext in hosted_file_type_icons:
            return settings.STATIC_URL + 'icon_thumbs/' + hosted_file_type_icons[file_ext] + THUMBNAIL_FORMAT_SUFFIX
    return get_default_thumbnail_url()

def get_default_thumbnail_url():
    if hasattr(settings, 'UPLOADER_DEFAULT_THUMBNAIL'):
        return settings.UPLOADER_DEFAULT_THUMBNAIL
    else:
        return constants.UPLOADER_DEFAULT_THUMBNAIL

UPLOADER_UPLOAD_DIRECTORY = 'attachments/'

def get_uploader_dir(file_name, instance=None):
    if instance and instance.created_by:
        # Incorporate creator & related model into directory generation
        upload_url = UPLOADER_UPLOAD_DIRECTORY + str(instance.created_by.pk) + '/' + str(instance.content_type.pk)
        return upload_url + '/'
    return UPLOADER_UPLOAD_DIRECTORY
#
# def get_uploaded_url(instance, file_name):
#     file_new_name = "{0}.{1}".format(uuid.uuid4().hex, file_name.split('.')[-1])
#     file_url = get_uploader_dir(file_name, instance) + file_new_name
#     while default_storage.exists(file_url):
#         file_url = upload_to(instance, file_name)
#
#     return file_url


