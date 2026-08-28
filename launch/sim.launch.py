import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    """Base simulation: Gazebo + world + robot + ROS<->Gazebo bridge.

    No control node is started here -- this is shared by both
    obstacle_avoidance.launch.py (autonomous) and manual_control.launch.py
    (teleop), which each just add whatever is driving /cmd_vel.
    """

    pkg_simple_robot = get_package_share_directory('simple_robot')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    world_path = os.path.join(pkg_simple_robot, 'worlds', 'obstacle_world.sdf')
    robot_path = os.path.join(pkg_simple_robot, 'models', 'robot.sdf')

    # Start Gazebo (Ignition Fortress) with the obstacle world, running.
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_path}'}.items(),
    )

    # Spawn the robot model into the running world.
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-file', robot_path,
            '-name', 'simple_robot',
            '-x', '0', '-y', '0', '-z', '0.0',
        ],
        output='screen',
    )

    # Bridge the topics between ROS 2 and Gazebo Transport. Without this,
    # /cmd_vel and /lidar exist on two separate, unconnected middlewares.
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            '/lidar@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
        ],
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription([
        gz_sim,
        spawn_robot,
        bridge,
    ])
