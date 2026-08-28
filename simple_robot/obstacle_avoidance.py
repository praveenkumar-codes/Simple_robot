import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

import math


class ObstacleAvoidance(Node):

    # Distance (m) that triggers an avoidance turn.
    SAFE_DISTANCE = 1.0

    # Must see this much clearance in front before resuming straight-ahead
    # motion. Kept higher than SAFE_DISTANCE (hysteresis) so the robot
    # actually swings clear of an obstacle's corner instead of stopping the
    # turn the instant the nose barely clears it.
    CLEAR_DISTANCE = 1.4

    # Half-width of the forward detection cone, in radians (~34 degrees).
    FRONT_ANGLE = 0.6

    # Side sectors (radians) used to judge which way is more open.
    SIDE_ANGLE_MIN = 0.6
    SIDE_ANGLE_MAX = 1.3

    FORWARD_SPEED = 0.4
    TURN_SPEED = 0.8

    # Small forward creep while turning so the robot actually arcs past the
    # obstacle instead of spinning in place next to it.
    TURN_FORWARD_CREEP = 0.1


    def __init__(self):

        super().__init__('obstacle_avoidance')

        self.subscription = self.create_subscription(
            LaserScan,
            '/lidar',
            self.lidar_callback,
            10
        )

        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # True while actively turning away from an obstacle. Kept as state
        # (rather than deciding fresh every single scan) so the turn
        # direction doesn't flip mid-maneuver and so it doesn't bail out of
        # the turn the moment the front is only just barely clear -- that
        # was what caused it to clip corners instead of avoiding them.
        self.avoiding = False
        self.turn_direction = 1.0  # +1 = turn left, -1 = turn right

        self.get_logger().info('Obstacle Avoidance Robot Started')


    def _sector_min(self, msg, angle_lo, angle_hi):

        distances = []

        for i, distance in enumerate(msg.ranges):

            angle = msg.angle_min + i * msg.angle_increment

            if angle_lo < angle < angle_hi and math.isfinite(distance):
                distances.append(distance)

        return min(distances) if distances else float('inf')


    def lidar_callback(self, msg):

        front = self._sector_min(msg, -self.FRONT_ANGLE, self.FRONT_ANGLE)

        cmd = Twist()

        if not self.avoiding:

            if front < self.SAFE_DISTANCE:

                # Just detected an obstacle -- pick whichever side has more
                # room and commit to turning that way, instead of always
                # turning left. Always-left steering is what was sending
                # the robot toward the *next* obstacle's corner rather than
                # around it.
                left = self._sector_min(msg, self.SIDE_ANGLE_MIN, self.SIDE_ANGLE_MAX)
                right = self._sector_min(msg, -self.SIDE_ANGLE_MAX, -self.SIDE_ANGLE_MIN)

                self.turn_direction = 1.0 if left >= right else -1.0
                self.avoiding = True

                self.get_logger().warn(
                    f'OBSTACLE DETECTED at {front:.2f} m! Turning '
                    f'{"left" if self.turn_direction > 0 else "right"}'
                )

            else:
                self.get_logger().info('PATH CLEAR - MOVING FORWARD')
                cmd.linear.x = self.FORWARD_SPEED
                cmd.angular.z = 0.0
                self.publisher.publish(cmd)
                return

        # Currently avoiding: keep turning until there is a solid clearance
        # margin ahead, not just barely enough to stop triggering.
        if front > self.CLEAR_DISTANCE:

            self.avoiding = False
            self.get_logger().info('CLEAR OF OBSTACLE - RESUMING FORWARD')
            cmd.linear.x = self.FORWARD_SPEED
            cmd.angular.z = 0.0

        else:
            cmd.linear.x = self.TURN_FORWARD_CREEP
            cmd.angular.z = self.turn_direction * self.TURN_SPEED

        self.publisher.publish(cmd)


def main(args=None):

    rclpy.init(args=args)

    node = ObstacleAvoidance()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
