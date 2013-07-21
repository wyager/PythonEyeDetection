Python Eye Detection

This is my simple and hackish eye/retina/pupil detector.

Disclaimer: I have absolutely no formal training or education in computer vision, and this is my first project to do anything of the sort. There is probably a lot to be improved upon here.

Operation is simple. Plug in a webcam and run `python eye_detect.py`. It will show the webcam image. If it sees your iris, it will superimpose a blue dot over it. It will also show (in a box in the upper left) what it thinks your eye is. It will show in another box to the upper slightly-less-left if it thinks it sees a pupil or an iris, and where it thinks the pupil (green) and iris (blue) are (at 2x magnification). If it thinks it sees a sensible pupil/iris combo, it will save a picture with a date stamp in the running directory.

Be sure to bring your eye pretty close to the camera, and to be well-lit.

It uses OpenCV cv2 (which uses numpy) to do all the matrix math, camera, and display stuff.

It's not very well-structured (I wrote this just for fun), but it works surprisingly well. On my computer, it captures a few good iris shots every second, and a decent number of them are very accurate in terms of delineating the iris and pupil boundaries. I'm not sure which eyes this will work with. I doubt it will work with very dark or very light irises.

Unfortunately, due to the hackish nature of this program, it will probably only work out of the box on webcams with a similar resolution to mine. If you want it to work on a different resolution (or angle) camera, you will have to tweak it.
