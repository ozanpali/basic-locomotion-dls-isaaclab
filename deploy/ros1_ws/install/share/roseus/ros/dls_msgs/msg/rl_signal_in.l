;; Auto-generated. Do not edit!


(when (boundp 'dls_msgs::rl_signal_in)
  (if (not (find-package "DLS_MSGS"))
    (make-package "DLS_MSGS"))
  (shadow 'rl_signal_in (find-package "DLS_MSGS")))
(unless (find-package "DLS_MSGS::RL_SIGNAL_IN")
  (make-package "DLS_MSGS::RL_SIGNAL_IN"))

(in-package "ROS")
;;//! \htmlinclude rl_signal_in.msg.html
(if (not (find-package "STD_MSGS"))
  (ros::roseus-add-msgs "std_msgs"))


(defclass dls_msgs::rl_signal_in
  :super ros::object
  :slots (_header _position _linear_velocity _orientation_quat _orientation_euler _angular_velocity _joint_positions _joint_velocities ))

(defmethod dls_msgs::rl_signal_in
  (:init
   (&key
    ((:header __header) (instance std_msgs::Header :init))
    ((:position __position) (make-array 3 :initial-element 0.0 :element-type :float))
    ((:linear_velocity __linear_velocity) (make-array 3 :initial-element 0.0 :element-type :float))
    ((:orientation_quat __orientation_quat) (make-array 4 :initial-element 0.0 :element-type :float))
    ((:orientation_euler __orientation_euler) (make-array 3 :initial-element 0.0 :element-type :float))
    ((:angular_velocity __angular_velocity) (make-array 3 :initial-element 0.0 :element-type :float))
    ((:joint_positions __joint_positions) (make-array 12 :initial-element 0.0 :element-type :float))
    ((:joint_velocities __joint_velocities) (make-array 12 :initial-element 0.0 :element-type :float))
    )
   (send-super :init)
   (setq _header __header)
   (setq _position __position)
   (setq _linear_velocity __linear_velocity)
   (setq _orientation_quat __orientation_quat)
   (setq _orientation_euler __orientation_euler)
   (setq _angular_velocity __angular_velocity)
   (setq _joint_positions __joint_positions)
   (setq _joint_velocities __joint_velocities)
   self)
  (:header
   (&rest __header)
   (if (keywordp (car __header))
       (send* _header __header)
     (progn
       (if __header (setq _header (car __header)))
       _header)))
  (:position
   (&optional __position)
   (if __position (setq _position __position)) _position)
  (:linear_velocity
   (&optional __linear_velocity)
   (if __linear_velocity (setq _linear_velocity __linear_velocity)) _linear_velocity)
  (:orientation_quat
   (&optional __orientation_quat)
   (if __orientation_quat (setq _orientation_quat __orientation_quat)) _orientation_quat)
  (:orientation_euler
   (&optional __orientation_euler)
   (if __orientation_euler (setq _orientation_euler __orientation_euler)) _orientation_euler)
  (:angular_velocity
   (&optional __angular_velocity)
   (if __angular_velocity (setq _angular_velocity __angular_velocity)) _angular_velocity)
  (:joint_positions
   (&optional __joint_positions)
   (if __joint_positions (setq _joint_positions __joint_positions)) _joint_positions)
  (:joint_velocities
   (&optional __joint_velocities)
   (if __joint_velocities (setq _joint_velocities __joint_velocities)) _joint_velocities)
  (:serialization-length
   ()
   (+
    ;; std_msgs/Header _header
    (send _header :serialization-length)
    ;; float64[3] _position
    (* 8    3)
    ;; float64[3] _linear_velocity
    (* 8    3)
    ;; float64[4] _orientation_quat
    (* 8    4)
    ;; float64[3] _orientation_euler
    (* 8    3)
    ;; float64[3] _angular_velocity
    (* 8    3)
    ;; float64[12] _joint_positions
    (* 8    12)
    ;; float64[12] _joint_velocities
    (* 8    12)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; std_msgs/Header _header
       (send _header :serialize s)
     ;; float64[3] _position
     (dotimes (i 3)
       (sys::poke (elt _position i) (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
       )
     ;; float64[3] _linear_velocity
     (dotimes (i 3)
       (sys::poke (elt _linear_velocity i) (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
       )
     ;; float64[4] _orientation_quat
     (dotimes (i 4)
       (sys::poke (elt _orientation_quat i) (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
       )
     ;; float64[3] _orientation_euler
     (dotimes (i 3)
       (sys::poke (elt _orientation_euler i) (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
       )
     ;; float64[3] _angular_velocity
     (dotimes (i 3)
       (sys::poke (elt _angular_velocity i) (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
       )
     ;; float64[12] _joint_positions
     (dotimes (i 12)
       (sys::poke (elt _joint_positions i) (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
       )
     ;; float64[12] _joint_velocities
     (dotimes (i 12)
       (sys::poke (elt _joint_velocities i) (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
       )
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; std_msgs/Header _header
     (send _header :deserialize buf ptr-) (incf ptr- (send _header :serialization-length))
   ;; float64[3] _position
   (dotimes (i (length _position))
     (setf (elt _position i) (sys::peek buf ptr- :double)) (incf ptr- 8)
     )
   ;; float64[3] _linear_velocity
   (dotimes (i (length _linear_velocity))
     (setf (elt _linear_velocity i) (sys::peek buf ptr- :double)) (incf ptr- 8)
     )
   ;; float64[4] _orientation_quat
   (dotimes (i (length _orientation_quat))
     (setf (elt _orientation_quat i) (sys::peek buf ptr- :double)) (incf ptr- 8)
     )
   ;; float64[3] _orientation_euler
   (dotimes (i (length _orientation_euler))
     (setf (elt _orientation_euler i) (sys::peek buf ptr- :double)) (incf ptr- 8)
     )
   ;; float64[3] _angular_velocity
   (dotimes (i (length _angular_velocity))
     (setf (elt _angular_velocity i) (sys::peek buf ptr- :double)) (incf ptr- 8)
     )
   ;; float64[12] _joint_positions
   (dotimes (i (length _joint_positions))
     (setf (elt _joint_positions i) (sys::peek buf ptr- :double)) (incf ptr- 8)
     )
   ;; float64[12] _joint_velocities
   (dotimes (i (length _joint_velocities))
     (setf (elt _joint_velocities i) (sys::peek buf ptr- :double)) (incf ptr- 8)
     )
   ;;
   self)
  )

(setf (get dls_msgs::rl_signal_in :md5sum-) "78b51508ca7b56859062573cc269aae1")
(setf (get dls_msgs::rl_signal_in :datatype-) "dls_msgs/rl_signal_in")
(setf (get dls_msgs::rl_signal_in :definition-)
      "Header header 

# system state
float64[3] position
float64[3] linear_velocity
float64[4] orientation_quat
float64[3] orientation_euler
float64[3] angular_velocity
float64[12] joint_positions
float64[12] joint_velocities
================================================================================
MSG: std_msgs/Header
# Standard metadata for higher-level stamped data types.
# This is generally used to communicate timestamped data 
# in a particular coordinate frame.
# 
# sequence ID: consecutively increasing ID 
uint32 seq
#Two-integer timestamp that is expressed as:
# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
# time-handling sugar is provided by the client library
time stamp
#Frame this data is associated with
string frame_id

")



(provide :dls_msgs/rl_signal_in "78b51508ca7b56859062573cc269aae1")


