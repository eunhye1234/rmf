import rclpy
from vision_follower_node import VisionFollower
import time



def main(args=None):
    rclpy.init(args=args)
    node = VisionFollower()
    try:
        #노드의 __init__에서 스레드들이 시작됨
        #메인 스레드는 종료 신호를 기다리며 대기
        while rclpy.ok():
            time.sleep(1)
        rclpy.spin(node)

    except KeyboardInterrupt:
        node.get_logger().info('KeyboardInterrupt, shutting down...')
    finally:
        #노드의 destroy_node가 호출되며 스레드 정리
        node.destory_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()






# def main(args=None):
#     rclpy.init(args=args)
#     node = VisionFollower()
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         node.destory_node()
#         rclpy.shutdown()

# if __name__ == '__main__':
#     main()
