def broadcast_target(drone_id, target):
    message = {
        "type": "TARGET_DETECTED",
        "leader_id": drone_id,
        "target": target
    }
    return message