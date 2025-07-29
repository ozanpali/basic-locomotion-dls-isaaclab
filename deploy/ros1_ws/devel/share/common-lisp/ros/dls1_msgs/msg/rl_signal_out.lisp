; Auto-generated. Do not edit!


(cl:in-package dls1_msgs-msg)


;//! \htmlinclude rl_signal_out.msg.html

(cl:defclass <rl_signal_out> (roslisp-msg-protocol:ros-message)
  ((header
    :reader header
    :initarg :header
    :type std_msgs-msg:Header
    :initform (cl:make-instance 'std_msgs-msg:Header))
   (desired_joint_positions
    :reader desired_joint_positions
    :initarg :desired_joint_positions
    :type (cl:vector cl:float)
   :initform (cl:make-array 12 :element-type 'cl:float :initial-element 0.0)))
)

(cl:defclass rl_signal_out (<rl_signal_out>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <rl_signal_out>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'rl_signal_out)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name dls1_msgs-msg:<rl_signal_out> is deprecated: use dls1_msgs-msg:rl_signal_out instead.")))

(cl:ensure-generic-function 'header-val :lambda-list '(m))
(cl:defmethod header-val ((m <rl_signal_out>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader dls1_msgs-msg:header-val is deprecated.  Use dls1_msgs-msg:header instead.")
  (header m))

(cl:ensure-generic-function 'desired_joint_positions-val :lambda-list '(m))
(cl:defmethod desired_joint_positions-val ((m <rl_signal_out>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader dls1_msgs-msg:desired_joint_positions-val is deprecated.  Use dls1_msgs-msg:desired_joint_positions instead.")
  (desired_joint_positions m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <rl_signal_out>) ostream)
  "Serializes a message object of type '<rl_signal_out>"
  (roslisp-msg-protocol:serialize (cl:slot-value msg 'header) ostream)
  (cl:map cl:nil #'(cl:lambda (ele) (cl:let ((bits (roslisp-utils:encode-double-float-bits ele)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 32) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 40) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 48) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 56) bits) ostream)))
   (cl:slot-value msg 'desired_joint_positions))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <rl_signal_out>) istream)
  "Deserializes a message object of type '<rl_signal_out>"
  (roslisp-msg-protocol:deserialize (cl:slot-value msg 'header) istream)
  (cl:setf (cl:slot-value msg 'desired_joint_positions) (cl:make-array 12))
  (cl:let ((vals (cl:slot-value msg 'desired_joint_positions)))
    (cl:dotimes (i 12)
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 32) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 40) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 48) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 56) bits) (cl:read-byte istream))
    (cl:setf (cl:aref vals i) (roslisp-utils:decode-double-float-bits bits)))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<rl_signal_out>)))
  "Returns string type for a message object of type '<rl_signal_out>"
  "dls1_msgs/rl_signal_out")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'rl_signal_out)))
  "Returns string type for a message object of type 'rl_signal_out"
  "dls1_msgs/rl_signal_out")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<rl_signal_out>)))
  "Returns md5sum for a message object of type '<rl_signal_out>"
  "f8d521d926cc5906a32fd89020ac8289")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'rl_signal_out)))
  "Returns md5sum for a message object of type 'rl_signal_out"
  "f8d521d926cc5906a32fd89020ac8289")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<rl_signal_out>)))
  "Returns full string definition for message of type '<rl_signal_out>"
  (cl:format cl:nil "Header header ~%~%float64[12] desired_joint_positions~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'rl_signal_out)))
  "Returns full string definition for message of type 'rl_signal_out"
  (cl:format cl:nil "Header header ~%~%float64[12] desired_joint_positions~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <rl_signal_out>))
  (cl:+ 0
     (roslisp-msg-protocol:serialization-length (cl:slot-value msg 'header))
     0 (cl:reduce #'cl:+ (cl:slot-value msg 'desired_joint_positions) :key #'(cl:lambda (ele) (cl:declare (cl:ignorable ele)) (cl:+ 8)))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <rl_signal_out>))
  "Converts a ROS message object to a list"
  (cl:list 'rl_signal_out
    (cl:cons ':header (header msg))
    (cl:cons ':desired_joint_positions (desired_joint_positions msg))
))
