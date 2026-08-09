import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, LaunchConfiguration
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    bringup_pkg_share = get_package_share_directory('ball_follower_bringup')
    description_pkg_share = get_package_share_directory('ball_follower_description')
    ros_gz_sim_pkg_share = get_package_share_directory('ros_gz_sim')

    urdf_path = os.path.join(description_pkg_share, 'urdf', 'ball_follower.urdf.xacro')
    rviz_config_path = os.path.join(description_pkg_share, 'rviz', 'config.rviz')
    gazebo_config_path = os.path.join(bringup_pkg_share, 'config', 'gazebo_bringup.yaml')
    models_path = os.path.join(bringup_pkg_share, 'models')
    empty_world_path = os.path.join(bringup_pkg_share, 'worlds', 'empty.sdf')

    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=models_path
    )

    robot_description = ParameterValue(Command(['xacro ', urdf_path]), value_type=str)

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]
    )

    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path]
    )

    gz_sim_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_pkg_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'{empty_world_path} -r'}.items()
    )

    ros_gz_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': gazebo_config_path}]
    )

    gz_spawn_entity_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description']
    )

    return LaunchDescription([
        set_gz_resource_path,
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node,
        gz_sim_include,
        ros_gz_bridge_node,
        gz_spawn_entity_node
    ])
