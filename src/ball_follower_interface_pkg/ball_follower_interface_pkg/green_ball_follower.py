#!/usr/bin/env python3
from lark.parsers import lalr_interactive_parser
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

CENTER_REGION_THRESHOLD = 1/12
START_CENTER_X = 0
END_CENTER_X = 0
STOP_THRESHOLD = 250

class GreenBallFollower(Node):
    def __init__(self):
        super().__init__("green_ball_follower")

        self.bridge = CvBridge()
        self.image_sub = self.create_subscription(
            Image,
            "/camera/image_raw",
            self.image_callback,
            10
        )
        self.cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.images = {}

        self.get_logger().info("Green Ball Follower Node Started")

    def move(self, order):
        cv2.putText(self.cv_image, order, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
        twist = Twist()
        if order == "left":
            twist.angular.z = 0.3
        elif order == "right":
            twist.angular.z = -0.3
        elif order == "forward":
            twist.linear.x = 0.4
        elif order == 'lost':
            twist.angular.z = -0.3
        elif order == "stop":
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        self.cmd_pub.publish(twist)

    def display_images(self):
        self.images['feed'] = self.cv_image

        # Resize all stored views in self.images to 640x360 and convert single-channel masks to 3-channel BGR
        h, w = 360, 640
        img_feed = cv2.resize(self.images.get('feed', self.cv_image), (w, h))
        img_hsv = cv2.resize(self.images.get('hsv', np.zeros_like(self.cv_image)), (w, h))
        
        mask = self.images.get('mask', np.zeros((self.cv_image.shape[0], self.cv_image.shape[1]), dtype=np.uint8))
        img_mask = cv2.cvtColor(cv2.resize(mask, (w, h)), cv2.COLOR_GRAY2BGR)
        
        img_result = cv2.resize(self.images.get('result', np.zeros_like(self.cv_image)), (w, h))

        # Add small yellow titles (Yellow in BGR: (0, 255, 255)) horizontally centered
        yellow_color = (0, 255, 255)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2

        titles = [
            (img_feed, "Camera Feed"),
            (img_hsv, "HSV Space"),
            (img_mask, "Mask"),
            (img_result, "Result")
        ]

        for img, text in titles:
            (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
            x = (w - text_w) // 2
            cv2.putText(img, text, (x, 30), font, font_scale, yellow_color, thickness)

        # Combine all four images into a single window grid (2x2)
        top_row = np.hstack((img_feed, img_hsv))
        bottom_row = np.hstack((img_mask, img_result))
        combined = np.vstack((top_row, bottom_row))

        cv2.imshow("Green Ball Follower", combined)
        cv2.waitKey(1)

    def image_callback(self, msg: Image):
        global START_CENTER_X, END_CENTER_X
        try:
            # Convert ROS Image message to OpenCV image
            self.cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            START_CENTER_X = int(self.cv_image.shape[1]//2 - self.cv_image.shape[1]*CENTER_REGION_THRESHOLD // 2)
            END_CENTER_X = int(self.cv_image.shape[1]//2 + self.cv_image.shape[1]*CENTER_REGION_THRESHOLD // 2) 
        except Exception as e:
            self.get_logger().error(f"Failed to convert image: {e}")
            return

        center, radius = detect_green_ball(self, self.cv_image)
        if radius and center:
            cv2.circle(self.cv_image, (int(center[0]), int(center[1])), int(radius), (0, 255, 0), 2)
            cv2.circle(self.cv_image, (int(center[0]), int(center[1])), 3, (0, 0, 255), 3)
            if radius > STOP_THRESHOLD:
                self.move('stop')
            else:
                center_x, center_y = center
                center = (int(center_x), int(center_y))
                radius = int(radius)

                if(center_x < START_CENTER_X):
                    self.move("left")
                elif(center_x > END_CENTER_X):
                    self.move("right")
                else:
                    self.move("forward")
        else:
            self.move('lost')

        self.display_images()


def main(args=None):
    rclpy.init(args=args)
    node = GreenBallFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

def detect_green_ball(node, image):
    ''' 
        this function gets raw image as input, stores intermediate frames into node.images dict,
        and returns the center pixel (x, y) and radius of green ball
    '''
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    node.images['hsv'] = hsv

    blured = cv2.GaussianBlur(hsv, (25, 25), 0)
    low_green = np.array([40, 50, 50])
    high_green = np.array([80, 255, 255])
    mask = cv2.inRange(blured, low_green, high_green)
    node.images['mask'] = mask

    result = cv2.bitwise_and(image, image, mask=mask)
    node.images['result'] = result

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, 0

    # Assuming there is only one circle
    cnt = max(contours, key=cv2.contourArea)
    (center, radius) = cv2.minEnclosingCircle(cnt)

    return center, radius