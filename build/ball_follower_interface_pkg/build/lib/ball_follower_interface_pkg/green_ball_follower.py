#!/usr/bin/env python3
from lark.parsers import lalr_interactive_parser
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np


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

        self.get_logger().info("Green Ball Follower Node Started")

    def image_callback(self, msg: Image):
        try:
            # Convert ROS Image message to OpenCV image
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f"Failed to convert image: {e}")
            return

        # TODO: Add green ball detection and tracking logic here
        
        # Display image frame (optional)
        cv2.line(cv_image,(cv_image.shape[1]//3, 0), (cv_image.shape[1]//3, cv_image.shape[0]), (0,255, 0), 10)
        cv2.line(cv_image,(2*cv_image.shape[1]//3, 0), (2*cv_image.shape[1]//3, cv_image.shape[0]), (0,255, 0), 10)



        

        cv2.imshow("Camera Feed", cv_image)
        center, radius = detect_green_ball(cv_image)

        if center is not None:
            center = (int(center[0]), int(center[1]))
            radius = int(radius)
            cv2.circle(cv_image, center, radius, (0, 255, 0), 2)
            cv2.circle(cv_image, center, 3, (0, 0, 255), 3)

        cv2.imshow("Camera Feed", cv_image)
        cv2.waitKey(1)


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

def detect_green_ball(image):
    ''' 
        this function get raw image as input and return the center pixel (x, y) and radius of green ball
    '''
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    cv2.imshow("hsv", hsv)

    blured = cv2.GaussianBlur(hsv, (25, 25), 0)
    low_green = np.array([40, 50, 50])
    high_green = np.array([80, 255, 255])
    mask = cv2.inRange(blured, low_green, high_green)
    cv2.imshow('mask', mask)
    result = cv2.bitwise_and(image, image, mask=mask)
    cv2.imshow('result', result)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, 0

    # Assuming there is only one circle
    cnt = max(contours, key=cv2.contourArea)

    return cv2.minEnclosingCircle(cnt)