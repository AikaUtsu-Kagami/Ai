from robot_voice_vision_bot.chatbot import LocalChatBrain
from robot_voice_vision_bot.robot import parse_robot_command
from robot_voice_vision_bot.vision import VisionSnapshot


def test_parse_robot_command_known():
    cmd = parse_robot_command("forward")
    assert cmd is not None
    assert cmd.action == "MOVE_FORWARD"
    assert cmd.value == 30


def test_parse_robot_command_unknown():
    assert parse_robot_command("dance") is None


def test_local_brain_can_issue_robot_command():
    brain = LocalChatBrain()
    snap = VisionSnapshot(faces_detected=0, frame_width=640, frame_height=480)
    decision = brain.respond("please move forward", snap)
    assert decision.robot_command is not None
    assert decision.robot_command.action == "MOVE_FORWARD"


def test_local_brain_proactive_when_idle():
    brain = LocalChatBrain()
    snap = VisionSnapshot(faces_detected=0, frame_width=640, frame_height=480)
    msg = brain.proactive(snap, idle_seconds=30)
    assert msg is not None
