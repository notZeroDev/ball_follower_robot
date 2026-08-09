# Ball Follower ROS 2 Workspace

A ROS 2 (Humble) mobile robot simulation workspace featuring differential drive control, Gazebo Harmonic simulation, and real-time computer vision tracking of a green ball using OpenCV.

---

## 📦 Packages Overview

This workspace contains three ROS 2 packages:

1. **`ball_follower_description`**:
   - Contains robot URDF/XACRO models (chassis, differential drive wheels, caster, and camera sensor).
   - Includes RViz configuration and visualization launch scripts.

2. **`ball_follower_bringup`**:
   - Contains launch configurations for Gazebo simulation and ROS-Gazebo bridge configurations.
   - Includes custom world definitions (`empty.sdf` with sensor pipeline support).

3. **`ball_follower_interface_pkg`**:
   - Python nodes for teleoperation and automated visual ball tracking:
     - `green_ball_follower`: Real-time HSV color segmentation and tracking for following a green ball.
     - `human_follower`: Person tracking node using YOLOv8.
     - Teleop nodes (`keyboard`, `keyboard_twist`, `ps3_twist`).

---

## ⚙️ Prerequisites

- **ROS 2**: Humble Hawksbill
- **Gazebo**: Gazebo Sim (Ignition / Gazebo Harmonic)
- **Python Libraries**:
  ```bash
  pip install opencv-python numpy cv_bridge ultralytics
  ```

---

## 🛠️ Build Instructions

1. Source ROS 2 setup:
   ```bash
   source /opt/ros/humble/setup.bash
   ```

2. Build the workspace:
   ```bash
   cd ~/ball_follower
   colcon build
   ```

3. Source the install overlay:
   ```bash
   source install/setup.bash
   ```

---

## 🚀 Running the Simulation & Nodes

### 1. Launch Robot in Gazebo & RViz
To launch the differential drive robot in Gazebo (empty world) with RViz visualization:
```bash
ros2 launch ball_follower_bringup ball_follower_gazebo.launch.py
```

### 2. Run the Green Ball Follower Node
To process camera images from `/camera/image_raw` and drive the robot towards a detected green ball:
```bash
ros2 run ball_follower_interface_pkg green_ball_follower
```

#### Node Visualization:
The `green_ball_follower` node presents a single **2x2 tiled window** combining:
- **Top-Left**: Camera Feed (with tracking circle overlays and status text)
- **Top-Right**: HSV Color Space view
- **Bottom-Left**: Binary Green Mask
- **Bottom-Right**: Masked Output Result

---

## 🛰️ ROS 2 Topics

- `/camera/image_raw` (`sensor_msgs/msg/Image`): Raw camera feed from the robot.
- `/cmd_vel` (`geometry_msgs/msg/Twist`): Robot velocity commands for differential drive steering.
- `/joint_states` (`sensor_msgs/msg/JointState`): Wheel joint states bridged from Gazebo.
- `/tf` (`tf2_msgs/msg/TFMessage`): Robot transform tree.
