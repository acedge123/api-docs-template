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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "scope": self.scope,
            "description": self.description,
            "params_schema": self.params_schema,
            "supports_dry_run": self.supports_dry_run,
        }


@dataclass
class Pack:
    """Pack = actions + handlers"""
    name: str
    actions: List[ActionDef]
    handlers: Dict[str, Any]  # name -> handler callable
