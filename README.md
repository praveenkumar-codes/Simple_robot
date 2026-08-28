# Simple_robot
simple_robot
Setup Guide & Glossary
ROS 2 Humble  ·  Gazebo (Ignition Fortress)  ·  Ubuntu 22.04

Part 1 — Installation Guide
Commands for setting up a fresh Ubuntu 22.04 machine to build and run the simple_robot package, from ROS 2 itself through to manual teleop control.
1. ROS 2 Humble
Skip this step if ROS 2 Humble is already installed.
sudo apt update && sudo apt install -y curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update
sudo apt install -y ros-humble-desktop

2. Gazebo (Ignition Fortress) + the ROS 2 bridge
sudo apt install -y \
  ros-humble-ros-gz \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz-bridge \
  ros-humble-ros-gz-interfaces

3. Teleop for manual control
sudo apt install -y ros-humble-teleop-twist-keyboard

4. Source ROS 2 automatically
Add this once so every new terminal has ROS 2 available:
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

5. Build and source the workspace
cd ~/ros2_ws
colcon build --packages-select simple_robot
source install/setup.bash

Rebuild with colcon build any time you edit the SDF files, the launch files, or the Python node.
6. Verify the setup
ign gazebo --version          # should print "Gazebo Sim, version 6.x.x"
ros2 pkg list | grep ros_gz   # should list ros_gz, ros_gz_bridge, ros_gz_sim, ...
ros2 pkg list | grep teleop   # should list teleop_twist_keyboard

7. Sanity-check that Gazebo actually renders
Do this before trusting any other symptom — the gpu_lidar sensor needs real GPU/display rendering, and a machine without it fails silently.
ign gazebo ~/ros2_ws/src/simple_robot/worlds/obstacle_world.sdf

A window with the ground plane and two red boxes should appear.
8. Run it
Automatic (obstacle avoidance):
ros2 launch simple_robot obstacle_avoidance.launch.py

Manual (two terminals):
ros2 launch simple_robot manual_control.launch.py
# in a second terminal:
ros2 run teleop_twist_keyboard teleop_twist_keyboard


Part 2 — Glossary of Terms
Grouped by category and tied to the actual files and commands used in the simple_robot package, rather than generic definitions.
Gazebo / simulation terms
Term
Meaning
World
The simulated environment itself — ground, lighting, obstacles, physics settings. One .sdf file describes one world. (worlds/obstacle_world.sdf)
Model
One "thing" placed in a world — could be the robot, a box, the ground. Has its own links/joints. (<model name="simple_robot">, <model name="obstacle_1">)
Link
One rigid body inside a model — a single solid chunk that doesn’t bend. A model is usually several links connected by joints. (base_link, left_wheel, right_wheel, caster_wheel, lidar_link)
Joint
The connection between two links, defining how they can move relative to each other. (left_joint/right_joint are revolute; lidar_joint/caster_joint are fixed)
SDF (Simulation Description Format)
The XML format Gazebo uses to describe worlds and models — the .sdf files themselves. (robot.sdf, obstacle_world.sdf)
Collision vs. Visual
Two geometry definitions per link: <collision> is what physics bumps into (invisible, used for contact/friction); <visual> is only what renders on screen.
Inertial
A link’s mass and how that mass is distributed (moment of inertia) — determines how hard it is to push or spin.
Friction (mu, mu2)
How grippy a collision surface is in two perpendicular directions. Wheels use mu=10.0 (high grip); the caster uses mu=0.01 (near-frictionless, so it slides freely).
Sensor
A link can carry a sensor definition that generates data during simulation. (<sensor type="gpu_lidar"> on lidar_link)
Plugin
Compiled code Gazebo loads to add behavior plain SDF can’t express, e.g. turning velocity commands into wheel torque. (the DiffDrive plugin)
gz / ign
The Gazebo command-line tool. ign is the older name (Ignition-era, used by the installed Fortress version); newer Gazebo uses gz.
Spawn
Adding a model into an already-running world at runtime, rather than baking it into the world file. (the "create" node in the launch files)

ROS 2 terms
Term
Meaning
Node
One running program that does one job within the ROS 2 graph. (obstacle_avoidance, parameter_bridge, the create spawner)
Topic
A named channel that nodes publish messages to and subscribe to — nodes never call each other directly. (/cmd_vel, /lidar, /clock)
Publisher / Subscriber
A node writing to a topic is a publisher; a node reading from it is a subscriber. Many-to-many is allowed.
Message type
The fixed data structure carried on a topic. (geometry_msgs/msg/Twist on /cmd_vel, sensor_msgs/msg/LaserScan on /lidar)
Package
A unit of installable ROS 2 code, described by package.xml and setup.py. (simple_robot)
Workspace
A folder containing one or more packages under src/, plus the build/ and install/ folders colcon generates. (~/ros2_ws)
colcon build
The tool that compiles/installs everything in a workspace’s src/ into build/ and install/.
source install/setup.bash
Loads the just-built workspace into the current shell. Needed in every new terminal before ros2 launch/run.
Launch file
A Python script (*.launch.py) that starts a group of nodes together with one command. (sim.launch.py, obstacle_avoidance.launch.py, manual_control.launch.py)
ros2 topic list / echo / hz
CLI tools to inspect topics live: list what exists, print messages as they arrive, or measure publish rate.

ROS 2 ↔ Gazebo bridge
Term
Meaning
ros_gz_bridge
A package that translates messages between ROS 2’s pub/sub system and Gazebo’s own separate one ("Gazebo Transport"). Without it, a shared topic name is not a shared connection.
parameter_bridge
The executable from ros_gz_bridge that you run, specifying which topics to bridge and direction (@ = both ways, [ = Gazebo→ROS, ] = ROS→Gazebo).
/clock
A topic Gazebo publishes simulated time on. Bridging it lets ROS 2 nodes use sim time instead of wall-clock time.
use_sim_time
A parameter on a ROS 2 node telling it to read its clock from /clock instead of the OS, so timestamps stay in sync with the simulation.

Control terms
Term
Meaning
cmd_vel
Short for "command velocity" — the topic convention almost every ROS mobile robot uses to receive drive commands, as a Twist message.
Twist
A message type with two 3D vectors: linear (m/s) and angular (rad/s). Ground robots typically only use linear.x and angular.z.
DiffDrive plugin
The Gazebo plugin that reads Twist commands and converts them into left/right wheel joint velocities, simulating a differential-drive robot.
Teleop
Short for "tele-operation" — a human remotely driving the robot in real time, as opposed to autonomous control.
teleop_twist_keyboard
A ROS 2 package that reads the keyboard in a terminal and publishes Twist messages to /cmd_vel accordingly.
Lidar / LaserScan
Lidar = a sensor measuring distance by sweeping a laser and timing the reflection. LaserScan is the ROS 2 message carrying that sweep as an array of distances.
Reactive obstacle avoidance
The control style obstacle_avoidance.py uses: no map, no planning — read the latest sensor data, make one decision, act, repeat every scan.
