import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    """Manual mode: just the base simulation (Gazebo + robot + bridge),
    with no controller node attached to /cmd_vel. Drive it yourself with,
    e.g. in another terminal:

        ros2 run teleop_twist_keyboard teleop_twist_keyboard

    teleop_twist_keyboard reads the keyboard directly, so it isn't
    launched from here -- ros2 launch doesn't give it an interactive
    terminal to read from.
    """

    pkg_simple_robot = get_package_share_directory('simple_robot')

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_simple_robot, 'launch', 'sim.launch.py')
        ),
    )

    return LaunchDescription([
        sim,
    ])
