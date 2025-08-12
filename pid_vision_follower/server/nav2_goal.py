from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

class Nav2GoalSender:
    def __init__(self, node):
        self.node = node
        self.client = ActionClient(node, NavigateToPose, 'navigate_to_pose')
    
    def send_goal(self, target_pose):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.node.get_clock().now().to_msg()
        pose.pose.position.x = target_pose[0] / 100.0
        pose.pose.position.y = target_pose[1] / 100.0
        pose.pose.orientation.w = 1.0

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose

        self.client.wait_for_server()
        self.client.send_goal_async(goal_msg)
        self.node.get_logger().info("Nav2 goal 전송 완료")
