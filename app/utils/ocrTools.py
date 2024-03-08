import base64

def cv2_to_base64(image):
    return base64.b64encode(image).decode('utf8')


def _check_image_file(path):
    img_end = {'jpg', 'bmp', 'png', 'jpeg', 'rgb', 'tif', 'tiff', 'gif'}
    return any([path.lower().endswith(e) for e in img_end])
