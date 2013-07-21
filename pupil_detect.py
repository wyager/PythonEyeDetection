#All the stuff here is for finding pupils in eyes
import cv2
import numpy
np = numpy

#Mask an image so all pixels outside feature circle are black
def mask_image_by_feature(image, feature):
    circle_mask_image = np.zeros(image.shape, dtype=np.uint8)
    cv2.circle(circle_mask_image, (int(feature.pt[0]), int(feature.pt[1])), int(feature.size/2), 1, -1)
    masked_image = (image * circle_mask_image).astype(np.uint8)
    return masked_image

#Find average brightness of pixels under a feature's circle
def find_average_brightness_of_feature(image, feature):
    feature_image = mask_image_by_feature(image, feature)
    total_value = feature_image.sum()
    area = np.pi * ((feature.size/2)**2)
    return total_value/area

#Sums up all the pixels under a feature's circle and averages them
#Darkest first
def sort_features_by_brightness(image, features):
    features_and_brightnesses = [(find_average_brightness_of_feature(image, feature), feature) for feature in features]
    features_and_brightnesses.sort(key = lambda x:x[0])
    return [fb[1] for fb in features_and_brightnesses]

def draw_circle_for_feature(image, feature, color=255, thickness=1):
    cv2.circle(image, (int(feature.pt[0]), int(feature.pt[1])), int(feature.size/2), color, thickness)

def find_pupil(gray_image, minsize=.1, maxsize=.5):
    detector = cv2.FeatureDetector_create('MSER')
    features_all = detector.detect(gray_image)
    features_big = [feature for feature in features_all if feature.size > gray_image.shape[0]*minsize]
    features_small = [feature for feature in features_big if feature.size < gray_image.shape[0]*maxsize]
    if len(features_small) == 0:
        return None
    features_sorted = sort_features_by_brightness(gray_image, features_small)
    pupil = features_sorted[0]
    return (int(pupil.pt[0]), int(pupil.pt[1]), int(pupil.size/2))

def circle_pupil(color_image, output_image = None):
    if output_image is None:
        output_image = color_image
    gray_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2GRAY)
    pupil_coords = find_pupil(gray_image)
    if pupil_coords is not None:
        cv2.circle(output_image, pupil_coords[:2], pupil_coords[2], (0,255,0),4)

def draw(photo):
    image_to_show = photo.copy()
    circle_pupil(image_to_show)
    cv2.imshow('Image', image_to_show)
    if cv2.waitKey(10) > 0: #If we got a key press in less than 10ms
        return 1
    return 0

def main():
    camera = cv2.VideoCapture(0)
    while(1):
        success, photo = camera.read()
        if draw(photo) > 0:
            break

if __name__ == '__main__':
    main()
