#This is my extremely hackish iris and pupil tracker/detector.
import time
import cv2
import pupil_detect
#I don't use the face classifier. But I'm putting it here in case someone else
#wants to.
#faceCascadeClassifier = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
eyeCascadeClassifier = cv2.CascadeClassifier("haarcascade_eye.xml")


def detect_objects(image, objectClassifier, divider=4):
    #increase divider for more speed, less accuracy
    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    small_image = cv2.resize(gray_image, (gray_image.shape[1]/divider,gray_image.shape[0]/divider))
    min_object_size = (20,20)
    haar_scale = 1.2
    min_neighbors = 2
    haar_flags = 0
    objects = objectClassifier.detectMultiScale(small_image, haar_scale, min_neighbors, haar_flags, min_object_size)
    return objects*divider

class Eye():
    def __init__(self,x, y, x2, y2):
        self.x = x
        self.y = y
        self.x2 = x2
        self.y2 = y2
        self.width = x2 - x
        self.height = y2 - y
        self.topcorner = (x, y)
        self.bottomcorner = (x2, y2)
def draw(photo):
    image = photo.copy()
    image_to_show = image
    eyes = detect_objects(image, eyeCascadeClassifier)
    #################### Select the rightmost eye ##################
    rightmost_eye = None
    if eyes is not None:
        for eye in eyes:
            (x,y) = eye[0], eye[1]
            (x2,y2) = (eye[0] + eye[2]), (eye[1] + eye[3])
            if (rightmost_eye is None) or (x < rightmost_eye.x):
                rightmost_eye = Eye(x, y, x2, y2)
    ###############################################################
    ####### Extract the image of the rightmost eye ################
    eye_image = None
    if rightmost_eye is not None:
        eye_image = image[rightmost_eye.y:rightmost_eye.y2, rightmost_eye.x:rightmost_eye.x2]
    ###############################################################
    ### To assist in edge detection, try to "black out" sclera ####
    binary_eye_image = None
    if eye_image is not None:
        eye_histogram = [0]*256
        eye_image = cv2.cvtColor(eye_image, cv2.COLOR_RGB2GRAY)
        for i in xrange(256):
            value_count = (eye_image == i).sum()
            eye_histogram[i] = value_count
        count = 0
        index = 255
        while count < (eye_image.size*3/4):
            count += eye_histogram[index]
            index -= 1
        quarter_threshold = index
        #Multiply all parts of eye above bottom 1/4 brightness by 0
        #Might not work on people with light irises. Have not tried.
        binary_eye_image = cv2.equalizeHist((eye_image < quarter_threshold) * eye_image)
    ###############################################################
    ####### Look for circle (the iris). Save coordinates. ########
    relative_iris_coordinates = None
    if binary_eye_image is not None:
        eye_circles = cv2.HoughCircles(binary_eye_image, cv2.cv.CV_HOUGH_GRADIENT, 3, 500, maxRadius = binary_eye_image.shape[0]/5)
        if eye_circles is not None:
            #Usually gets the job done. Messy.
            circle = eye_circles[0][0]
            relative_iris_coordinates = (circle[0], circle[1])
    ###############################################################
    ######### Put blue dot on eye in big picture ##################
    absolute_iris_coordinates = None
    if relative_iris_coordinates is not None and rightmost_eye is not None:
        absolute_iris_coordinates = (int(relative_iris_coordinates[0]+rightmost_eye.x), int(relative_iris_coordinates[1]+rightmost_eye.y))
        cv2.circle(image_to_show, absolute_iris_coordinates, 5, (255,0,0), thickness=10)
    ###############################################################
    ####### Extract image of iris (and some surrounding) ##########
    iris_image = None
    if absolute_iris_coordinates is not None:
        x = absolute_iris_coordinates[0]
        y = absolute_iris_coordinates[1]
        #Should find a way to make these numbers adaptable.
        #It really messes things up when these arbitrary numbers don't work with
        #whatever image size or eye distance is actually being used.
        #YOU, DEAR READER, MUST CHANGE THESE FOR YOUR CAMERA
        #These numbers describe the guestimated shape of a captured image of an iris.
        #This program makes no effort to automatically find the size of the iris in
        #the captured image of the iris
        w = 60
        h = 60
        iris_image = photo[y-h:y+h,x-w:x+w]
        iris_image_to_show = cv2.resize(iris_image, (iris_image.shape[1]*2, iris_image.shape[0]*2))
        image_to_show[0:iris_image_to_show.shape[0], 00:00+iris_image_to_show.shape[1]] = iris_image_to_show
    ###############################################################
    ### Draw blue circle around iris. Draw green around pupil #####
    #Also, if the pupil and iris seem to be sensible shapes/sizes,
    #return the current iris_image (picture of the iris+surroundings)
    iris_picture = None
    if iris_image is not None:
        iris_gray = cv2.cvtColor(iris_image, cv2.COLOR_RGB2GRAY)
        iris_circles_image = iris_image.copy()
        iris_circles = cv2.HoughCircles(iris_gray, cv2.cv.CV_HOUGH_GRADIENT, 2, 100)
        if iris_circles is not None:
            circle=iris_circles[0][0]
            cv2.circle(iris_circles_image, (circle[0], circle[1]), circle[2], (255,0,0), thickness=2)
        pupil_coords = pupil_detect.find_pupil(iris_gray)
        if pupil_coords is not None:
            cv2.circle(iris_circles_image, pupil_coords[:2], pupil_coords[2], (0,255,0),4)
        if iris_circles is not None and pupil_coords is not None:
            ic = iris_circles[0][0]
            pc = pupil_coords
            #Check if pupil is within iris
            if abs(ic[0]-pc[0])<ic[2] and abs(ic[1]-pc[1])<ic[2] and pc[2]<ic[2]:
                iris_picture = iris_circles_image
        iris_circles_to_show = cv2.resize(iris_circles_image, (iris_circles_image.shape[1]*2,iris_circles_image.shape[0]*2))
        image_to_show[0:iris_circles_to_show.shape[0], 200:200+iris_circles_to_show.shape[1]] = iris_circles_to_show
    ###############################################################
    cv2.imshow('Image', image_to_show)
    if cv2.waitKey(10) > 0: #If we got a key press in less than 10ms
        #Also, cv2 has some weirdness where the image won't update without a waitKey()
        return True, iris_picture
    return False, iris_picture

def main():
    camera = cv2.VideoCapture(0)
    found_iris_counter = 0
    while(1):
        success, photo = camera.read()
        finished, iris_pic = draw(photo)
        if iris_pic is not None:
            timecode = time.strftime("%Y-%m-%d_%H;%M;%S", time.gmtime())
            cv2.imwrite("iris_pic_"+str(found_iris_counter)+"_"+timecode+".jpg", iris_pic)
            found_iris_counter += 1
        if finished:
            break

if __name__ == '__main__':
    main()
