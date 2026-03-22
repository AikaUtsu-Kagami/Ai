from __future__ import annotations

import json
from dataclasses import dataclass

from .robot import RobotCommand, parse_robot_command
from .vision import VisionSnapshot


SYSTEM_PROMPT = """
You are a real-time robot assistant.
Return strict JSON only with this schema:
{
  "reply": "string for spoken response",
  "robot_action": "forward|backward|left|right|stop|wave|null"
}
Decide robot_action only when user explicitly asks movement/gesture.
Keep replies concise and safe.
""".strip()


@dataclass
class BotDecision:
    reply: str
    robot_command: RobotCommand | None


class LocalChatBrain:
    def respond(self, user_text: str, snapshot: VisionSnapshot) -> BotDecision:
        text = user_text.lower()
        robot_command = None
        for action in ["forward", "backward", "left", "right", "stop", "wave"]:
            if action in text:
                robot_command = parse_robot_command(action)
                break

        if "who do you see" in text or "what do you see" in text:
            reply = f"I can currently see about {snapshot.faces_detected} face(s)."
        elif robot_command:
            reply = f"Got it. I will {robot_command.action.lower().replace('_', ' ')} now."
        else:
            reply = (
                "I'm active and monitoring vision and robot state. "
                "Tell me to move, stop, or ask what I can see."
            )
        return BotDecision(reply=reply, robot_command=robot_command)

    def proactive(self, snapshot: VisionSnapshot, idle_seconds: float) -> str | None:
        if idle_seconds < 10:
            return None
        if snapshot.faces_detected > 0:
            return "I can see someone nearby. I'm ready to help whenever you want."
        if idle_seconds > 25:
            return "I'm still here and watching the room. You can give me a task anytime."
        return None


class OpenAIChatBrain:
    def __init__(self, client, model: str) -> None:
        self.client = client
        self.model = model
        self.history: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    def respond(self, user_text: str, snapshot: VisionSnapshot) -> BotDecision:
        vision_context = (
            f"Vision status: faces_detected={snapshot.faces_detected}, "
            f"frame={snapshot.frame_width}x{snapshot.frame_height}."
        )

        self.history.append({"role": "user", "content": f"{user_text}\n{vision_context}"})

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            response_format={"type": "json_object"},
            temperature=0.4,
        )
        raw = completion.choices[0].message.content or '{"reply":"I did not catch that","robot_action":null}'
        parsed = json.loads(raw)

        reply = str(parsed.get("reply", "I did not catch that.")).strip()
        robot_action = parsed.get("robot_action")
        robot_command = parse_robot_command(robot_action)

        self.history.append({"role": "assistant", "content": raw})
        if len(self.history) > 20:
            self.history = [self.history[0], *self.history[-19:]]

        return BotDecision(reply=reply, robot_command=robot_command)

    def proactive(self, snapshot: VisionSnapshot, idle_seconds: float) -> str | None:
        if idle_seconds < 15:
            return None
        if snapshot.faces_detected > 0:
            return "I notice movement in front of me. Do you want me to do anything?"
        if idle_seconds > 30:
            return "System check complete. I'm awake and available for commands."
        return None
