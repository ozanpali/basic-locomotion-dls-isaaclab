# generated from genmsg/cmake/pkg-genmsg.cmake.em

message(STATUS "dls1_msgs: 2 messages, 0 services")

set(MSG_I_FLAGS "-Idls1_msgs:/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg;-Istd_msgs:/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env/share/std_msgs/cmake/../msg;-Igeometry_msgs:/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env/share/geometry_msgs/cmake/../msg;-Iactionlib_msgs:/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env/share/actionlib_msgs/cmake/../msg")

# Find all generators
find_package(gencpp REQUIRED)
find_package(geneus REQUIRED)
find_package(genlisp REQUIRED)
find_package(gennodejs REQUIRED)
find_package(genpy REQUIRED)

add_custom_target(dls1_msgs_generate_messages ALL)

# verify that message/service dependencies have not changed since configure



get_filename_component(_filename "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_in.msg" NAME_WE)
add_custom_target(_dls1_msgs_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "dls1_msgs" "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_in.msg" "std_msgs/Header"
)

get_filename_component(_filename "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_out.msg" NAME_WE)
add_custom_target(_dls1_msgs_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "dls1_msgs" "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_out.msg" "std_msgs/Header"
)

#
#  langs = gencpp;geneus;genlisp;gennodejs;genpy
#

### Section generating for lang: gencpp
### Generating Messages
_generate_msg_cpp(dls1_msgs
  "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_in.msg"
  "${MSG_I_FLAGS}"
  "/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/dls1_msgs
)
_generate_msg_cpp(dls1_msgs
  "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_out.msg"
  "${MSG_I_FLAGS}"
  "/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/dls1_msgs
)

### Generating Services

### Generating Module File
_generate_module_cpp(dls1_msgs
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/dls1_msgs
  "${ALL_GEN_OUTPUT_FILES_cpp}"
)

add_custom_target(dls1_msgs_generate_messages_cpp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_cpp}
)
add_dependencies(dls1_msgs_generate_messages dls1_msgs_generate_messages_cpp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_in.msg" NAME_WE)
add_dependencies(dls1_msgs_generate_messages_cpp _dls1_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_out.msg" NAME_WE)
add_dependencies(dls1_msgs_generate_messages_cpp _dls1_msgs_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(dls1_msgs_gencpp)
add_dependencies(dls1_msgs_gencpp dls1_msgs_generate_messages_cpp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS dls1_msgs_generate_messages_cpp)

### Section generating for lang: geneus
### Generating Messages
_generate_msg_eus(dls1_msgs
  "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_in.msg"
  "${MSG_I_FLAGS}"
  "/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/dls1_msgs
)
_generate_msg_eus(dls1_msgs
  "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_out.msg"
  "${MSG_I_FLAGS}"
  "/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/dls1_msgs
)

### Generating Services

### Generating Module File
_generate_module_eus(dls1_msgs
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/dls1_msgs
  "${ALL_GEN_OUTPUT_FILES_eus}"
)

add_custom_target(dls1_msgs_generate_messages_eus
  DEPENDS ${ALL_GEN_OUTPUT_FILES_eus}
)
add_dependencies(dls1_msgs_generate_messages dls1_msgs_generate_messages_eus)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_in.msg" NAME_WE)
add_dependencies(dls1_msgs_generate_messages_eus _dls1_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_out.msg" NAME_WE)
add_dependencies(dls1_msgs_generate_messages_eus _dls1_msgs_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(dls1_msgs_geneus)
add_dependencies(dls1_msgs_geneus dls1_msgs_generate_messages_eus)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS dls1_msgs_generate_messages_eus)

### Section generating for lang: genlisp
### Generating Messages
_generate_msg_lisp(dls1_msgs
  "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_in.msg"
  "${MSG_I_FLAGS}"
  "/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/dls1_msgs
)
_generate_msg_lisp(dls1_msgs
  "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_out.msg"
  "${MSG_I_FLAGS}"
  "/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/dls1_msgs
)

### Generating Services

### Generating Module File
_generate_module_lisp(dls1_msgs
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/dls1_msgs
  "${ALL_GEN_OUTPUT_FILES_lisp}"
)

add_custom_target(dls1_msgs_generate_messages_lisp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_lisp}
)
add_dependencies(dls1_msgs_generate_messages dls1_msgs_generate_messages_lisp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_in.msg" NAME_WE)
add_dependencies(dls1_msgs_generate_messages_lisp _dls1_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_out.msg" NAME_WE)
add_dependencies(dls1_msgs_generate_messages_lisp _dls1_msgs_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(dls1_msgs_genlisp)
add_dependencies(dls1_msgs_genlisp dls1_msgs_generate_messages_lisp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS dls1_msgs_generate_messages_lisp)

### Section generating for lang: gennodejs
### Generating Messages
_generate_msg_nodejs(dls1_msgs
  "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_in.msg"
  "${MSG_I_FLAGS}"
  "/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/dls1_msgs
)
_generate_msg_nodejs(dls1_msgs
  "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_out.msg"
  "${MSG_I_FLAGS}"
  "/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/dls1_msgs
)

### Generating Services

### Generating Module File
_generate_module_nodejs(dls1_msgs
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/dls1_msgs
  "${ALL_GEN_OUTPUT_FILES_nodejs}"
)

add_custom_target(dls1_msgs_generate_messages_nodejs
  DEPENDS ${ALL_GEN_OUTPUT_FILES_nodejs}
)
add_dependencies(dls1_msgs_generate_messages dls1_msgs_generate_messages_nodejs)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_in.msg" NAME_WE)
add_dependencies(dls1_msgs_generate_messages_nodejs _dls1_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_out.msg" NAME_WE)
add_dependencies(dls1_msgs_generate_messages_nodejs _dls1_msgs_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(dls1_msgs_gennodejs)
add_dependencies(dls1_msgs_gennodejs dls1_msgs_generate_messages_nodejs)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS dls1_msgs_generate_messages_nodejs)

### Section generating for lang: genpy
### Generating Messages
_generate_msg_py(dls1_msgs
  "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_in.msg"
  "${MSG_I_FLAGS}"
  "/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/dls1_msgs
)
_generate_msg_py(dls1_msgs
  "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_out.msg"
  "${MSG_I_FLAGS}"
  "/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/dls1_msgs
)

### Generating Services

### Generating Module File
_generate_module_py(dls1_msgs
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/dls1_msgs
  "${ALL_GEN_OUTPUT_FILES_py}"
)

add_custom_target(dls1_msgs_generate_messages_py
  DEPENDS ${ALL_GEN_OUTPUT_FILES_py}
)
add_dependencies(dls1_msgs_generate_messages dls1_msgs_generate_messages_py)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_in.msg" NAME_WE)
add_dependencies(dls1_msgs_generate_messages_py _dls1_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/deploy/ros1_ws/src/dls1_msgs/msg/rl_signal_out.msg" NAME_WE)
add_dependencies(dls1_msgs_generate_messages_py _dls1_msgs_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(dls1_msgs_genpy)
add_dependencies(dls1_msgs_genpy dls1_msgs_generate_messages_py)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS dls1_msgs_generate_messages_py)



if(gencpp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/dls1_msgs)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/dls1_msgs
    DESTINATION ${gencpp_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_cpp)
  add_dependencies(dls1_msgs_generate_messages_cpp std_msgs_generate_messages_cpp)
endif()
if(TARGET geometry_msgs_generate_messages_cpp)
  add_dependencies(dls1_msgs_generate_messages_cpp geometry_msgs_generate_messages_cpp)
endif()
if(TARGET actionlib_msgs_generate_messages_cpp)
  add_dependencies(dls1_msgs_generate_messages_cpp actionlib_msgs_generate_messages_cpp)
endif()

if(geneus_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/dls1_msgs)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/dls1_msgs
    DESTINATION ${geneus_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_eus)
  add_dependencies(dls1_msgs_generate_messages_eus std_msgs_generate_messages_eus)
endif()
if(TARGET geometry_msgs_generate_messages_eus)
  add_dependencies(dls1_msgs_generate_messages_eus geometry_msgs_generate_messages_eus)
endif()
if(TARGET actionlib_msgs_generate_messages_eus)
  add_dependencies(dls1_msgs_generate_messages_eus actionlib_msgs_generate_messages_eus)
endif()

if(genlisp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/dls1_msgs)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/dls1_msgs
    DESTINATION ${genlisp_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_lisp)
  add_dependencies(dls1_msgs_generate_messages_lisp std_msgs_generate_messages_lisp)
endif()
if(TARGET geometry_msgs_generate_messages_lisp)
  add_dependencies(dls1_msgs_generate_messages_lisp geometry_msgs_generate_messages_lisp)
endif()
if(TARGET actionlib_msgs_generate_messages_lisp)
  add_dependencies(dls1_msgs_generate_messages_lisp actionlib_msgs_generate_messages_lisp)
endif()

if(gennodejs_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/dls1_msgs)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/dls1_msgs
    DESTINATION ${gennodejs_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_nodejs)
  add_dependencies(dls1_msgs_generate_messages_nodejs std_msgs_generate_messages_nodejs)
endif()
if(TARGET geometry_msgs_generate_messages_nodejs)
  add_dependencies(dls1_msgs_generate_messages_nodejs geometry_msgs_generate_messages_nodejs)
endif()
if(TARGET actionlib_msgs_generate_messages_nodejs)
  add_dependencies(dls1_msgs_generate_messages_nodejs actionlib_msgs_generate_messages_nodejs)
endif()

if(genpy_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/dls1_msgs)
  install(CODE "execute_process(COMMAND \"/home/iit.local/gturrisi/mambaforge/envs/basic_locomotion_dls_isaaclab_ros1_env/bin/python3.11\" -m compileall \"${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/dls1_msgs\")")
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/dls1_msgs
    DESTINATION ${genpy_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_py)
  add_dependencies(dls1_msgs_generate_messages_py std_msgs_generate_messages_py)
endif()
if(TARGET geometry_msgs_generate_messages_py)
  add_dependencies(dls1_msgs_generate_messages_py geometry_msgs_generate_messages_py)
endif()
if(TARGET actionlib_msgs_generate_messages_py)
  add_dependencies(dls1_msgs_generate_messages_py actionlib_msgs_generate_messages_py)
endif()
