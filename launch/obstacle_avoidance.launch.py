import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    """Automatic mode: base simulation + the obstacle_avoidance node
    driving /cmd_vel on its own. For manual/keyboard control instead, use
    manual_control.launch.py."""

    pkg_simple_robot = get_package_share_directory('simple_robot')

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_simple_robot, 'launch', 'sim.launch.py')
        ),
    )

    obstacle_avoidance = Node(
        package='simple_robot',
        executable='obstacle_avoidance',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription([
        sim,
        obstacle_avoidance,
    ])
