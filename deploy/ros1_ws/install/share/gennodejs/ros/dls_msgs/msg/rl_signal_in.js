// Auto-generated. Do not edit!

// (in-package dls_msgs.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;
let std_msgs = _finder('std_msgs');

//-----------------------------------------------------------

class rl_signal_in {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.header = null;
      this.position = null;
      this.linear_velocity = null;
      this.orientation_quat = null;
      this.orientation_euler = null;
      this.angular_velocity = null;
      this.joint_positions = null;
      this.joint_velocities = null;
    }
    else {
      if (initObj.hasOwnProperty('header')) {
        this.header = initObj.header
      }
      else {
        this.header = new std_msgs.msg.Header();
      }
      if (initObj.hasOwnProperty('position')) {
        this.position = initObj.position
      }
      else {
        this.position = new Array(3).fill(0);
      }
      if (initObj.hasOwnProperty('linear_velocity')) {
        this.linear_velocity = initObj.linear_velocity
      }
      else {
        this.linear_velocity = new Array(3).fill(0);
      }
      if (initObj.hasOwnProperty('orientation_quat')) {
        this.orientation_quat = initObj.orientation_quat
      }
      else {
        this.orientation_quat = new Array(4).fill(0);
      }
      if (initObj.hasOwnProperty('orientation_euler')) {
        this.orientation_euler = initObj.orientation_euler
      }
      else {
        this.orientation_euler = new Array(3).fill(0);
      }
      if (initObj.hasOwnProperty('angular_velocity')) {
        this.angular_velocity = initObj.angular_velocity
      }
      else {
        this.angular_velocity = new Array(3).fill(0);
      }
      if (initObj.hasOwnProperty('joint_positions')) {
        this.joint_positions = initObj.joint_positions
      }
      else {
        this.joint_positions = new Array(12).fill(0);
      }
      if (initObj.hasOwnProperty('joint_velocities')) {
        this.joint_velocities = initObj.joint_velocities
      }
      else {
        this.joint_velocities = new Array(12).fill(0);
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type rl_signal_in
    // Serialize message field [header]
    bufferOffset = std_msgs.msg.Header.serialize(obj.header, buffer, bufferOffset);
    // Check that the constant length array field [position] has the right length
    if (obj.position.length !== 3) {
      throw new Error('Unable to serialize array field position - length must be 3')
    }
    // Serialize message field [position]
    bufferOffset = _arraySerializer.float64(obj.position, buffer, bufferOffset, 3);
    // Check that the constant length array field [linear_velocity] has the right length
    if (obj.linear_velocity.length !== 3) {
      throw new Error('Unable to serialize array field linear_velocity - length must be 3')
    }
    // Serialize message field [linear_velocity]
    bufferOffset = _arraySerializer.float64(obj.linear_velocity, buffer, bufferOffset, 3);
    // Check that the constant length array field [orientation_quat] has the right length
    if (obj.orientation_quat.length !== 4) {
      throw new Error('Unable to serialize array field orientation_quat - length must be 4')
    }
    // Serialize message field [orientation_quat]
    bufferOffset = _arraySerializer.float64(obj.orientation_quat, buffer, bufferOffset, 4);
    // Check that the constant length array field [orientation_euler] has the right length
    if (obj.orientation_euler.length !== 3) {
      throw new Error('Unable to serialize array field orientation_euler - length must be 3')
    }
    // Serialize message field [orientation_euler]
    bufferOffset = _arraySerializer.float64(obj.orientation_euler, buffer, bufferOffset, 3);
    // Check that the constant length array field [angular_velocity] has the right length
    if (obj.angular_velocity.length !== 3) {
      throw new Error('Unable to serialize array field angular_velocity - length must be 3')
    }
    // Serialize message field [angular_velocity]
    bufferOffset = _arraySerializer.float64(obj.angular_velocity, buffer, bufferOffset, 3);
    // Check that the constant length array field [joint_positions] has the right length
    if (obj.joint_positions.length !== 12) {
      throw new Error('Unable to serialize array field joint_positions - length must be 12')
    }
    // Serialize message field [joint_positions]
    bufferOffset = _arraySerializer.float64(obj.joint_positions, buffer, bufferOffset, 12);
    // Check that the constant length array field [joint_velocities] has the right length
    if (obj.joint_velocities.length !== 12) {
      throw new Error('Unable to serialize array field joint_velocities - length must be 12')
    }
    // Serialize message field [joint_velocities]
    bufferOffset = _arraySerializer.float64(obj.joint_velocities, buffer, bufferOffset, 12);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type rl_signal_in
    let len;
    let data = new rl_signal_in(null);
    // Deserialize message field [header]
    data.header = std_msgs.msg.Header.deserialize(buffer, bufferOffset);
    // Deserialize message field [position]
    data.position = _arrayDeserializer.float64(buffer, bufferOffset, 3)
    // Deserialize message field [linear_velocity]
    data.linear_velocity = _arrayDeserializer.float64(buffer, bufferOffset, 3)
    // Deserialize message field [orientation_quat]
    data.orientation_quat = _arrayDeserializer.float64(buffer, bufferOffset, 4)
    // Deserialize message field [orientation_euler]
    data.orientation_euler = _arrayDeserializer.float64(buffer, bufferOffset, 3)
    // Deserialize message field [angular_velocity]
    data.angular_velocity = _arrayDeserializer.float64(buffer, bufferOffset, 3)
    // Deserialize message field [joint_positions]
    data.joint_positions = _arrayDeserializer.float64(buffer, bufferOffset, 12)
    // Deserialize message field [joint_velocities]
    data.joint_velocities = _arrayDeserializer.float64(buffer, bufferOffset, 12)
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += std_msgs.msg.Header.getMessageSize(object.header);
    return length + 320;
  }

  static datatype() {
    // Returns string type for a message object
    return 'dls_msgs/rl_signal_in';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return '78b51508ca7b56859062573cc269aae1';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    Header header 
    
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
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new rl_signal_in(null);
    if (msg.header !== undefined) {
      resolved.header = std_msgs.msg.Header.Resolve(msg.header)
    }
    else {
      resolved.header = new std_msgs.msg.Header()
    }

    if (msg.position !== undefined) {
      resolved.position = msg.position;
    }
    else {
      resolved.position = new Array(3).fill(0)
    }

    if (msg.linear_velocity !== undefined) {
      resolved.linear_velocity = msg.linear_velocity;
    }
    else {
      resolved.linear_velocity = new Array(3).fill(0)
    }

    if (msg.orientation_quat !== undefined) {
      resolved.orientation_quat = msg.orientation_quat;
    }
    else {
      resolved.orientation_quat = new Array(4).fill(0)
    }

    if (msg.orientation_euler !== undefined) {
      resolved.orientation_euler = msg.orientation_euler;
    }
    else {
      resolved.orientation_euler = new Array(3).fill(0)
    }

    if (msg.angular_velocity !== undefined) {
      resolved.angular_velocity = msg.angular_velocity;
    }
    else {
      resolved.angular_velocity = new Array(3).fill(0)
    }

    if (msg.joint_positions !== undefined) {
      resolved.joint_positions = msg.joint_positions;
    }
    else {
      resolved.joint_positions = new Array(12).fill(0)
    }

    if (msg.joint_velocities !== undefined) {
      resolved.joint_velocities = msg.joint_velocities;
    }
    else {
      resolved.joint_velocities = new Array(12).fill(0)
    }

    return resolved;
    }
};

module.exports = rl_signal_in;
