from typing import Dict, Any, Optional
from enum import Enum


class PolicyAction(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"


class PolicyEngine:
    def __init__(self):
        self.policies: Dict[str, PolicyAction] = {
            "delete_memory": PolicyAction.ASK,
            "publish_research": PolicyAction.ASK,
            "send_external_communication": PolicyAction.ASK,
            "modify_research_profile": PolicyAction.ASK,
            "run_expensive_automation": PolicyAction.ASK,
            "execute_write_mcp": PolicyAction.ASK,
            "share_private_data": PolicyAction.DENY,
        }

    def check_policy(self, action: str, context: Optional[Dict[str, Any]] = None) -> PolicyAction:
        return self.policies.get(action, PolicyAction.ASK)

    def set_policy(self, action: str, policy: PolicyAction):
        self.policies[action] = policy

    def get_policies(self) -> Dict[str, str]:
        return {k: v.value for k, v in self.policies.items()}
