from typing import Callable, Dict, List, Any
from datetime import datetime


class EventHandler:
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
        self.event_log: List[dict] = []

    def register(self, event_type: str, handler: Callable):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    async def emit(self, event_type: str, data: Dict[str, Any]):
        self.event_log.append(
            {
                "event_type": event_type,
                "data": data,
                "timestamp": datetime.utcnow(),
            }
        )

        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                await handler(data)

    def get_event_log(self, limit: int = 100) -> List[dict]:
        return self.event_log[-limit:]
