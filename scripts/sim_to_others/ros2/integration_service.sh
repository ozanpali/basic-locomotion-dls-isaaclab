#!/bin/bash
source /opt/integration_service/setup.bash &
integration-service dls2_msgs/msg/fastdds_ros2__baseState.yaml &
integration-service dls2_msgs/msg/fastdds_ros2__blindState.yaml &
integration-service dls2_msgs/msg/fastdds_ros2__controlSignal.yaml &
integration-service dls2_msgs/msg/fastdds_ros2__trajectoryGenerator.yaml