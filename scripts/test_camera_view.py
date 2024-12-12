#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2

class CameraSubscriber(Node):
    def __init__(self):
        super().__init__('camera_subscriber')
        # Set the QoS profile to handle the policy mismatch if necessary
        qos_profile = rclpy.qos.QoSProfile(depth=10)
        qos_profile.durability = rclpy.qos.DurabilityPolicy.VOLATILE  # Adjust based on publisher's setting
        
        # Subscription to the camera topic
        self.subscription = self.create_subscription(
            Image,
            '/tobii_glasses/front_camera',
            self.listener_callback,
            qos_profile)
        self.subscription  # Prevent unused variable warning

        # Subscription to the gaze position topic
        self.gaze_subscription = self.create_subscription(
            String,
            '/tobii_glasses/gaze_position',
            self.gaze_callback,
            qos_profile)
        self.gaze_subscription  # Prevent unused variable warning

        # Initialize CV bridge
        self.bridge = CvBridge()
        self.gaze_position = (0, 0)  # Initialize gaze position

    def listener_callback(self, msg):
        # Convert ROS Image message to OpenCV image
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, msg.encoding)
        except Exception as e:
            self.get_logger().error(f"Failed to convert image: {e}")
            return

        # Draw a circle at the gaze position
        height, width, _ = cv_image.shape
        x = int(self.gaze_position[0] * width)
        y = int(self.gaze_position[1] * height)
        cv2.circle(cv_image, (x, y), 10, (0, 255, 0), -1)

        # Display the image using OpenCV
        cv2.imshow("Camera Feed", cv_image)
        cv2.waitKey(1)  # Required to update the image window

    def gaze_callback(self, msg):
        # Parse the gaze position data
        try:
            x_str, y_str = msg.data.split(',')
            self.gaze_position = (float(x_str), float(y_str))
        except Exception as e:
            self.get_logger().error(f"Failed to parse gaze position: {e}")

def main(args=None):
    rclpy.init(args=args)
    camera_subscriber = CameraSubscriber()

    try:
        rclpy.spin(camera_subscriber)
    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup when closing
        camera_subscriber.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()