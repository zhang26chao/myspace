from StringIO import StringIO
import os
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

def thumbnail(orig, maxWidth, maxHeight):
    orig.seek(0)
    image = Image.open(orig)
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
    image.thumbnail(__resize(image, maxWidth, maxHeight), Image.ANTIALIAS)
    # save the thumbnail to memory
    temp_handle = StringIO()
    image.save(temp_handle, 'png')
    # rewind the file
    temp_handle.seek(0)
    image.close()  
    # save to the thumbnail field
    return SimpleUploadedFile(os.path.splitext(orig.name)[0],
                             temp_handle.read(),
                             content_type='image/png')

def __resize(image, maxWidth, maxHeight):
    ori_w, ori_h = image.size
    if ori_w <= maxWidth and ori_h <= maxHeight:
        return image.size
    width = maxWidth
    height = (width * ori_h) / ori_w
    if height > maxHeight:
        height = maxHeight
        width = height * ori_w / ori_h
    return (width, height)
