import os
import cv2

# landmark indices
LEFT_EYE_CONTOUR = [263, 249, 390, 373, 374, 380,
                    381, 382, 398, 384, 385, 386, 387, 388, 466]
LEFT_IRIS_CONTOUR = [474, 475, 476, 477]
LEFT_EYEBROW_CONTOUR = [276, 283, 282, 295, 285]
RIGHT_EYE_CONTOUR = [33, 7,  163, 144, 145, 153,
                     154, 155, 173, 157, 158, 159, 160, 161, 246]
RIGHT_IRIS_CONTOUR = [469, 470, 471, 472]
RIGHT_EYEBROW_CONTOUR = [46, 53, 52, 65, 55]
NOSE_CONTOUR = [168, 6, 197, 195, 5, 4, 1,
                219, 218, 237, 44, 19, 274, 457, 438, 278]
LIPS_CONTOUR = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291,  409, 270, 269, 267, 0, 37, 39,
                40, 185, 78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 415, 310, 311, 312, 13, 82, 81, 80, 191]
LIPS_SINGLE_CONTOUR = [61, 146, 91, 181, 84, 17, 314, 405,
                       321, 375, 291,  409, 270, 269, 267, 0, 37, 39, 40, 185]
FACE_OVAL_CONTOUR = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378,
                     400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
FACE_CONTOUR = LEFT_EYEBROW_CONTOUR+LEFT_EYE_CONTOUR+LEFT_IRIS_CONTOUR + \
    RIGHT_EYEBROW_CONTOUR+RIGHT_EYE_CONTOUR + \
    RIGHT_IRIS_CONTOUR+LIPS_CONTOUR+FACE_OVAL_CONTOUR

# blendshape indices
BROW_BLENDSHAPE = [0, 1, 2, 3, 4]
CHEEK_BLENDSHAPE = [5, 6, 7]
EYE_BLINK_BLENDSHAPE = [8, 9]
EYE_LOOK_BLENDSHAPE = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
JAW_BLENDSHAPE = [22, 23, 24, 25]
MOUTH_BLENDSHAPE = [27, 28, 29, 30, 31, 32, 33, 34, 35,
                    36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48]
NOSE_BLENDSHAPE = [49, 50]
TONGUE_BLENDSHAPE = [51]
FACE_BLENDSHAPE = BROW_BLENDSHAPE+EYE_BLINK_BLENDSHAPE + \
    EYE_LOOK_BLENDSHAPE+CHEEK_BLENDSHAPE+JAW_BLENDSHAPE+MOUTH_BLENDSHAPE


def list_all_image(rootdir):
    _files = []
    list = os.listdir(rootdir)
    for i in range(0, len(list)):
        path = os.path.join(rootdir, list[i])
        if os.path.isdir(path):
            _files.extend(list_all_image(path))
        if os.path.isfile(path):
            if path.split('.')[-1] in ['jpg', 'png', 'jpeg', 'JPG']:
                _files.append(path)
    return _files


def normalize_image_size(image, norm_length, norm_short_side=False):
    height, width, _ = image.shape
    if norm_short_side:
        if width < height:
            norm_rate = float(norm_length)/float(width)
            resize_w = int(norm_length)
            resize_h = int(float(height) * norm_rate)
            return cv2.resize(image, (resize_w, resize_h))
        else:
            norm_rate = float(norm_length)/float(height)
            resize_h = int(norm_length)
            resize_w = int(float(width) * norm_rate)
            return cv2.resize(image, (resize_w, resize_h))

    if width >= height:
        norm_rate = float(norm_length)/float(width)
        resize_w = int(norm_length)
        resize_h = int(float(height) * norm_rate)
        return cv2.resize(image, (resize_w, resize_h))
    else:
        norm_rate = float(norm_length)/float(height)
        resize_h = int(norm_length)
        resize_w = int(float(width) * norm_rate)
        return cv2.resize(image, (resize_w, resize_h))
