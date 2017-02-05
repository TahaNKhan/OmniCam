import cv2
import time
import datetime


class Camera(object):
    frame = None

    def __init__(self, port):
        # initialize camera
        # port = port number of camera (first is 0)
        self.cam = cv2.VideoCapture(port)
        time.sleep(0.25)

    def __del__(self):
        # cleanup the camera and close any open windows
        self.cam.release()

    def get_jpeg(self):
        ret, jpeg = cv2.imencode('.jpg', self.frame)
        return jpeg.tobytes()

    def start_recording(self):
        # initialize the first frame in the video stream
        # other frames are compared to this frame to test if motion is detected
        firstFrame = None

        minArea = 500
        record = False

        # loop over the frames of the video
        while True:
            # grab the current frame
            grabbed, self.frame = self.cam.read()
            text = ""

            # if the frame could not be grabbed, then we have reached the end of the video
            if not grabbed:
                break

            # convert it to grayscale, and blur it
            gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            # if the first frame is None, initialize it
            if firstFrame is None:
                firstFrame = gray
                continue

            # compute the absolute difference between the current frame and first frame
            frameDelta = cv2.absdiff(firstFrame, gray)
            thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

            # dilate the thresholded image to fill in holes, then find contours on thresholded image
            thresh = cv2.dilate(thresh, None, iterations = 2)
            (_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # loop over the contours
            for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < minArea:
                    continue

                # compute the bounding box for the contour, draw it on the frame, and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "!!! INTRUDER ALERT !!!"


            # draw the text and timestamp on the frame
            timeNow = datetime.datetime.now().strftime("%b-%d-%Y_%I:%M:%S %p")
            cv2.putText(self.frame, format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(self.frame, timeNow.replace("_", " ").replace("-", " "), (10, self.frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (10, 255, 255), 1)

            # show the frame for local testing
            # cv2.imshow("OmniCam", self.frame)

            # start recording if motion is detected
            if text == "!!! INTRUDER ALERT !!!" and not record:
                codec = cv2.VideoWriter_fourcc(*"XVID")
                out = cv2.VideoWriter(timeNow.replace(":", "-").replace(" ", "_") + ".avi", codec, 15.0, (640, 480))
                record = True

            # write frame when motion is detected
            if text == "!!! INTRUDER ALERT !!!" and record:
                # write captured frames to file
                out.write(self.frame)

            # stop recording when motion is no longer detected
            if text == "" and record:
                out.release()
                record = False

            # if the `q` key is pressed, break from the loop
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
