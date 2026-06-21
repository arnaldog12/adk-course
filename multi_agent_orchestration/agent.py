"""Multi-Agent Orchestration for Content Publishing System."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import config_agent_utils

load_dotenv()

# Load agent from YAML configuration
config_path = Path(__file__).parent / "root_agent.yaml"
root_agent = config_agent_utils.from_config(str(config_path))
