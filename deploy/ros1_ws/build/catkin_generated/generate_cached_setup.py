# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import stat
import sys

# find the import for catkin's python package - either from source space or from an installed underlay
if os.path.exists(os.path.join('/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env/share/catkin/cmake', 'catkinConfig.cmake.in')):
    sys.path.insert(0, os.path.join('/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env/share/catkin/cmake', '..', 'python'))
try:
    from catkin.environment_cache import generate_environment_script
except ImportError:
    # search for catkin package in all workspaces and prepend to path
    for workspace in '/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/install;/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env'.split(';'):
        python_path = os.path.join(workspace, 'lib/python3.11/site-packages')
        if os.path.isdir(os.path.join(python_path, 'catkin')):
            sys.path.insert(0, python_path)
            break
    from catkin.environment_cache import generate_environment_script

code = generate_environment_script('/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/devel/env.sh')

output_filename = '/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/build/catkin_generated/setup_cached.sh'
with open(output_filename, 'w') as f:
    # print('Generate script for cached setup "%s"' % output_filename)
    f.write('\n'.join(code))

mode = os.stat(output_filename).st_mode
os.chmod(output_filename, mode | stat.S_IXUSR)
