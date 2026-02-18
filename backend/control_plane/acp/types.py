"""
ACP types — mirrors spec/
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ActionDef:
    """Action definition — spec/action-def.json"""

    name: str
    scope: str
    description: str
    params_schema: Dict[str, Any]
    supports_dry_run: bool
    billable: bool = True  # TWEAK #4: Whether this action should be billed
    billing_unit: Optional[str] = None  # TWEAK #4: "call" | "token" | "row" | "sec" | None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "scope": self.scope,
            "description": self.description,
            "params_schema": self.params_schema,
            "supports_dry_run": self.supports_dry_run,
            "billable": self.billable,
            "billing_unit": self.billing_unit,
        }


@dataclass
class Pack:
    """Pack = actions + handlers"""

    name: str
    actions: List[ActionDef]
    handlers: Dict[str, Any]  # name -> handler callable
