from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RobotCommand:
    action: str
    value: int = 0


class RobotTransport(Protocol):
    def write(self, payload: bytes) -> int:
        ...

    def close(self) -> None:
        ...


class SerialRobotController:
    def __init__(self, port: str, baud: int) -> None:
        self.port = port
        self.baud = baud
        self._transport: RobotTransport | None = None

    def connect(self) -> bool:
        if not self.port:
            return False
        import serial

        self._transport = serial.Serial(self.port, self.baud, timeout=1)
        return True

    def disconnect(self) -> None:
        if self._transport:
            self._transport.close()
            self._transport = None

    def send(self, command: RobotCommand) -> str:
        if not self._transport:
            return "robot_not_connected"
        line = f"{command.action}:{command.value}\n".encode("utf-8")
        self._transport.write(line)
        return line.decode("utf-8").strip()


def parse_robot_command(name: str | None) -> RobotCommand | None:
    if not name:
        return None

    normalized = name.strip().lower().replace(" ", "_")
    mapping = {
        "forward": RobotCommand("MOVE_FORWARD", 30),
        "backward": RobotCommand("MOVE_BACKWARD", 30),
        "left": RobotCommand("TURN_LEFT", 20),
        "right": RobotCommand("TURN_RIGHT", 20),
        "stop": RobotCommand("STOP", 0),
        "wave": RobotCommand("WAVE", 1),
    }
    return mapping.get(normalized)
