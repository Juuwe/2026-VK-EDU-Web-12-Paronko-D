import uuid
import os
from datetime import date

def get_avatar_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join('avatars', date.today().strftime('%Y/%m/%d'), f"{uuid.uuid4()}.{ext}")
