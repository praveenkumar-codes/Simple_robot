# simple_robot

A differential-drive robot simulated in **Gazebo (Ignition Fortress)** with a 2D lidar, drivable either **manually** (keyboard teleop) or **autonomously** (a reactive obstacle-avoidance node), built as a ROS 2 Humble package.

<p>
  <img alt="ROS 2" src="https://img.shields.io/badge/ROS_2-Humble-22314E?logo=ros&logoColor=white">
  <img alt="Gazebo" src="https://img.shields.io/badge/Gazebo-Ignition_Fortress-orange">
  <img alt="Ubuntu" src="https://img.shields.io/badge/Ubuntu-22.04-E95420?logo=ubuntu&logoColor=white">
</p>

## What's in the box

- A two-wheeled robot (`models/robot.sdf`) — differential drive, a front lidar, and a caster wheel for stability.
- An obstacle course world (`worlds/obstacle_world.sdf`) — a ground plane and two boxes to drive around.
- A reactive obstacle-avoidance node (`simple_robot/obstacle_avoidance.py`) — reads the lidar, steers away from whichever side is more open.
- Three launch files for the two ways to run it: fully automatic, or manual keyboard control.

## Package layout

```
simple_robot/
├── launch/
│   ├── sim.launch.py                 # shared base: Gazebo + spawn robot + ROS↔Gazebo bridge
│   ├── obstacle_avoidance.launch.py  # sim.launch.py + the autonomous avoidance node
│   └── manual_control.launch.py      # sim.launch.py only, for teleop
├── models/
│   └── robot.sdf                     # the robot: base, wheels, caster, lidar, diff-drive plugin
├── worlds/
│   └── obstacle_world.sdf            # ground + two obstacles
├── simple_robot/
│   └── obstacle_avoidance.py         # the reactive control node
├── docs/
│   └── simple_robot_setup_guide.docx # this README, as a printable Word doc
└── test/                             # ament lint/copyright/pep257 checks
```

## Prerequisites

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo (Ignition Fortress) + `ros_gz` bridge packages
- `teleop_twist_keyboard` (for manual control)
- A working GPU/display — the lidar sensor needs real rendering to produce data

### Install everything

```bash
# ROS 2 Humble (skip if already installed)
sudo apt update && sudo apt install -y curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update && sudo apt install -y ros-humble-desktop

# Gazebo + the ROS 2 bridge
sudo apt install -y \
  ros-humble-ros-gz \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz-bridge \
  ros-humble-ros-gz-interfaces

# Manual control
sudo apt install -y ros-humble-teleop-twist-keyboard

# Source ROS 2 in every new terminal
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## Build

```bash
cd ~/ros2_ws
colcon build --packages-select simple_robot
source install/setup.bash
```

Rebuild any time you edit the SDF files, the launch files, or `obstacle_avoidance.py`.

**Sanity-check Gazebo can actually render before anything else**, since a machine without a GPU fails silently later on:

```bash
ign gazebo ~/ros2_ws/src/simple_robot/worlds/obstacle_world.sdf
```

A window with the ground plane and two red boxes should appear.

## Run it

### Autonomous — obstacle avoidance

```bash
ros2 launch simple_robot obstacle_avoidance.launch.py
```

Starts Gazebo, spawns the robot, bridges the ROS 2 ↔ Gazebo topics, and starts the avoidance node. The robot drives forward until its lidar sees something within `1.0 m` ahead, then turns toward whichever side has more room until it has `1.4 m` of clearance again.

### Manual — keyboard teleop

Terminal 1:
```bash
ros2 launch simple_robot manual_control.launch.py
```

Terminal 2:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

| Key | Action |
|---|---|
| `i` / `,` | forward / backward |
| `j` / `l` | turn left / right in place |
| `u` `o` `m` `.` | forward/backward + curve |
| `k` | stop |
| `q`/`z`, `w`/`x`, `e`/`c` | adjust speed (both / linear / angular) |

Don't run both launch files at once — both the avoidance node and your keyboard would publish to `/cmd_vel`.

## How it works

```
   lidar sensor  ──/lidar──▶  obstacle_avoidance  ──/cmd_vel──▶  diff_drive plugin
   (gz gpu_lidar)              (ROS 2 node)                       (wheel motors)
```

- **`/lidar`** (`sensor_msgs/LaserScan`) — a 360° distance sweep from the robot's lidar, bridged from Gazebo into ROS 2.
- **`obstacle_avoidance`** — subscribes to `/lidar`, checks a ~34° cone directly ahead, decides to go straight or turn, publishes the decision.
- **`/cmd_vel`** (`geometry_msgs/Twist`) — the drive command, bridged back into Gazebo where the `DiffDrive` plugin turns it into wheel motion.

A `ros_gz_bridge parameter_bridge` node (started by `sim.launch.py`) is what connects these two topic names across ROS 2 and Gazebo's own separate transport — without it the node and the simulator can't see each other at all.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Gazebo window never opens, or crashes | No GPU/display | Run on a machine with a real GPU |
| Robot doesn't move, `/cmd_vel` is empty | Bridge not running, or two launch files running at once | `pkill -f "ign gazebo"`, relaunch a single launch file |
| Robot drives into obstacles without turning | `/lidar` has no data (GPU rendering issue) | `ros2 topic hz /lidar` — if silent, same fix as row 1 |
| Inconsistent behavior between runs | Leftover simulator process from a previous run | `pkill -f "ign gazebo"` before every relaunch |

## Further reading

- [`docs/simple_robot_setup_guide.docx`](docs/simple_robot_setup_guide.docx) — this installation guide plus a full glossary of ROS 2/Gazebo terms, as a printable document.

## License

TODO — declare a license in `package.xml` and here.
