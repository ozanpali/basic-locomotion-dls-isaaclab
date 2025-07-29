;; Auto-generated. Do not edit!


(when (boundp 'dls_msgs::rl_signal_out)
  (if (not (find-package "DLS_MSGS"))
    (make-package "DLS_MSGS"))
  (shadow 'rl_signal_out (find-package "DLS_MSGS")))
(unless (find-package "DLS_MSGS::RL_SIGNAL_OUT")
  (make-package "DLS_MSGS::RL_SIGNAL_OUT"))

(in-package "ROS")
;;//! \htmlinclude rl_signal_out.msg.html
(if (not (find-package "STD_MSGS"))
  (ros::roseus-add-msgs "std_msgs"))


(defclass dls_msgs::rl_signal_out
  :super ros::object
  :slots (_header _desired_joint_positions ))

(defmethod dls_msgs::rl_signal_out
  (:init
   (&key
    ((:header __header) (instance std_msgs::Header :init))
    ((:desired_joint_positions __desired_joint_positions) (make-array 12 :initial-element 0.0 :element-type :float))
    )
   (send-super :init)
   (setq _header __header)
   (setq _desired_joint_positions __desired_joint_positions)
   self)
  (:header
   (&rest __header)
   (if (keywordp (car __header))
       (send* _header __header)
     (progn
       (if __header (setq _header (car __header)))
       _header)))
  (:desired_joint_positions
   (&optional __desired_joint_positions)
   (if __desired_joint_positions (setq _desired_joint_positions __desired_joint_positions)) _desired_joint_positions)
  (:serialization-length
   ()
   (+
    ;; std_msgs/Header _header
    (send _header :serialization-length)
    ;; float64[12] _desired_joint_positions
    (* 8    12)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; std_msgs/Header _header
       (send _header :serialize s)
     ;; float64[12] _desired_joint_positions
     (dotimes (i 12)
       (sys::poke (elt _desired_joint_positions i) (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
       )
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; std_msgs/Header _header
     (send _header :deserialize buf ptr-) (incf ptr- (send _header :serialization-length))
   ;; float64[12] _desired_joint_positions
   (dotimes (i (length _desired_joint_positions))
     (setf (elt _desired_joint_positions i) (sys::peek buf ptr- :double)) (incf ptr- 8)
     )
   ;;
   self)
  )

(setf (get dls_msgs::rl_signal_out :md5sum-) "f8d521d926cc5906a32fd89020ac8289")
(setf (get dls_msgs::rl_signal_out :datatype-) "dls_msgs/rl_signal_out")
(setf (get dls_msgs::rl_signal_out :definition-)
      "Header header 

float64[12] desired_joint_positions
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



(provide :dls_msgs/rl_signal_out "f8d521d926cc5906a32fd89020ac8289")


