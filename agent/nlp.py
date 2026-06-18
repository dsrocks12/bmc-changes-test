import re
from dataclasses import dataclass
from typing import Dict, Pattern, Optional, Any


@dataclass(frozen=True)
class IntentPattern:
    name: str
    pattern: Pattern[str]
    explanation: str
    confidence: float


@dataclass
class IntentResult:
    intent: str
    entities: Dict[str, str]
    confidence: float
    explanation: str


class IntentParser:
    """
    Lightweight NLP parser using regular expressions.
    Used to quickly and deterministically match intents and extract entities
    without calling the SLM.
    """

    def __init__(self) -> None:
        self.patterns = [
            # --- Workspace-specific/BMC-specific patterns first ---
            IntentPattern(
                name="get_server_agentless_hosts",
                pattern=re.compile(
                    r"(get|show|list|fetch)\s+(all\s+)?(the\s+)?agentless\s+hosts?(\s+(for|of|on)\s+(server\s+)?(?P<server>[a-zA-Z0-9_\-\.]+))?",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to fetch server agentless hosts.",
                confidence=0.95,
            ),
            IntentPattern(
                name="set_server_desired_state",
                pattern=re.compile(
                    r"(set|change|update)\s+(the\s+)?(desired\s+)?state\s+(of\s+)?(server\s+)?(?P<server>[a-zA-Z0-9_\-\.]+)\s*(to|=)\s*(?P<state>Up|Down|Recycle|Ignore)",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to set a server desired state.",
                confidence=0.96,
            ),
            IntentPattern(
                name="set_server_desired_state",
                pattern=re.compile(
                    r"\b(?P<action>recycle|start|stop|ignore)\s+(server\s+)?(?P<server>[a-zA-Z0-9_\-\.]+)",
                    re.IGNORECASE,
                ),
                explanation="Detected server state control action.",
                confidence=0.92,
            ),
            IntentPattern(
                name="analyze_agent_communication",
                pattern=re.compile(
                    r"(analyze|check|test)\s+(the\s+)?(communication|connection)\s+(between\s+)?(server\s+)?(?P<server>[a-zA-Z0-9_\-\.]+)\s+(and\s+)?(agent\s+)?(?P<agent>[a-zA-Z0-9_\-\.]+)",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to analyze agent communication.",
                confidence=0.95,
            ),
            # --- Standard ctm-aapi patterns ---
            IntentPattern(
                name="get_system_settings",
                pattern=re.compile(
                    r"(get|show|list|fetch)\s+(the\s+)?system\s+settings?(\s+for\s+(control-?m\s+)?(environment|server)?\s*(?P<server>[a-zA-Z0-9_\-\.]+)?)?",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to get Control-M system settings.",
                confidence=0.95,
            ),
            IntentPattern(
                name="set_variables",
                pattern=re.compile(
                    r"(set|update)\s+variable\s+values?.*?\s+on\s+(server\s+)?(?P<server>[a-zA-Z0-9_\-\.]+)(?:.*?\bpool\s+(?P<pool>[a-zA-Z0-9_\-\.]+))?.*?\bvariable\s+name\s+(?P<var_name>[a-zA-Z0-9_\-\.\\%]+)\s+value\s+(?P<var_value>.+)$",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to set Control-M variables from JSON input.",
                confidence=0.96,
            ),
            IntentPattern(
                name="get_variables",
                pattern=re.compile(
                    r"(get|show|list)\s+variables?(\s+for\s+(server\s+)?(?P<server>[a-zA-Z0-9_\-\.]+))?(\s+pool\s+(?P<pool>[a-zA-Z0-9_\-\.\*]+))?(\s+name\s+(?P<var_name>[a-zA-Z0-9_\-\.\*]+))?",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to list runtime variables.",
                confidence=0.9,
            ),
            IntentPattern(
                name="delete_variables",
                pattern=re.compile(
                    r"(delete|remove)\s+variables?.*?\s+(from|on)\s+(the\s+)?server\s+(?P<server>[a-zA-Z0-9_\-\.]+)(?:.*?\bpool\s+(?P<pool>[a-zA-Z0-9_\-\.]+))?.*?\bvariable\s+name\s+(?P<var_name>[a-zA-Z0-9_\-\.\\%]+)",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to delete runtime variable(s).",
                confidence=0.95,
            ),
            IntentPattern(
                name="run_job",
                pattern=re.compile(
                    r"(run|start|trigger)\s+(job\s+)?(?P<job>[a-zA-Z0-9_\-\.]+)(\s+in\s+folder\s+(?P<folder>[a-zA-Z0-9_\-\.]+))?",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to run/order a job.",
                confidence=0.88,
            ),
            IntentPattern(
                name="aapi_server_status",
                pattern=re.compile(
                    r"(get|show|check)\s+(the\s+)?(aapi|automation(\s+api)?)\s+server\s+status(\s+(for|of|on)\s+(server\s+)?(?P<server>[a-zA-Z0-9_\-\.]+))?",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to fetch Automation API server status.",
                confidence=0.94,
            ),
            IntentPattern(
                name="job_statistics",
                pattern=re.compile(
                    r"(get|show|fetch|list)\s+(the\s+)?job\s+statistics(\s+from|\s+for|\s+of)?\s+(a\s+)?(job(id)?\s+)?(?P<job>[a-zA-Z0-9_\-\.:]+)",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to fetch job statistics by job id.",
                confidence=0.93,
            ),
            IntentPattern(
                name="job_status",
                pattern=re.compile(
                    r"(status|state)\s+(of\s+)?(job\s+)?(?P<job>[a-zA-Z0-9_\-\.:]+)",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to fetch a job status.",
                confidence=0.84,
            ),
            IntentPattern(
                name="hold_job",
                pattern=re.compile(
                    r"(hold|pause)\s+(job\s+)?(?P<job>[a-zA-Z0-9_\-\.]+)",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to hold a job.",
                confidence=0.86,
            ),
            IntentPattern(
                name="release_job",
                pattern=re.compile(
                    r"(release|resume|free)\s+(job\s+)?(?P<job>[a-zA-Z0-9_\-\.]+)",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to release a held job.",
                confidence=0.86,
            ),
            IntentPattern(
                name="list_active_jobs",
                pattern=re.compile(
                    r"(list|show|get).*(all\s+)?(active|running).*(jobs?)",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to list running jobs.",
                confidence=0.8,
            ),
            IntentPattern(
                name="get_connection_profiles",
                pattern=re.compile(
                    r"(get|show|list)\s+(all\s+)?(the\s+)?((?P<scope>local|centralized)\s+)?(deployed\s+)?connection\s+profiles?(\s+for\s+(agent\s+)?(?P<agent>[a-zA-Z0-9_\-\.]+))?(\s+(of\s+)?type\s+(?P<type>[a-zA-Z0-9_\-\.]+))?(\s+name\s+(?P<name>[a-zA-Z0-9_\-\.\*]+))?",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to fetch connection profiles.",
                confidence=0.93,
            ),
            IntentPattern(
                name="get_connection_profiles",
                pattern=re.compile(
                    r"((?P<scope>local|centralized)\s+)?connection\s+profiles?\s+(for\s+(agent\s+)?(?P<agent>[a-zA-Z0-9_\-\.]+)\s+)?(of\s+)?type\s+(?P<type>[a-zA-Z0-9_\-\.]+)",
                    re.IGNORECASE,
                ),
                explanation="Detected connection profiles by type request.",
                confidence=0.9,
            ),
            IntentPattern(
                name="get_connection_profiles_status",
                pattern=re.compile(
                    r"(get|show|list)\s+(deployed\s+)?connection\s+profiles?\s+status(\s+with\s+name\s+(?P<name>[a-zA-Z0-9_\-\.\*]+))?(\s+(of\s+)?type\s+(?P<type>[a-zA-Z0-9_\-\.\*]+))?(\s+limit\s+(?P<limit>[0-9]+))?",
                    re.IGNORECASE,
                ),
                explanation="Detected request for deployed connection profile status.",
                confidence=0.94,
            ),
            IntentPattern(
                name="get_agent_parameters",
                pattern=re.compile(
                    r"(get|show|list)\s+(?P<parameter>[a-zA-Z0-9_\-\.]+)\s+parameter\s+(for|of)\s+(agent\s+)?(?P<agent>(?!agent\b)[a-zA-Z0-9_\-\.]+)",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to fetch one specific parameter for an agent.",
                confidence=0.96,
            ),
            IntentPattern(
                name="get_agent_parameters",
                pattern=re.compile(
                    r"(get|show|list)\s+(all\s+)?(?:agent\s+)?(parameters?|params?)\s+(for|of)\s+(agent\s+)?(?P<agent>(?!agent\b)[a-zA-Z0-9_\-\.]+)(\s+(on|for|in)\s+(server\s+)?(?P<server>[a-zA-Z0-9_\-\.]+))?",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to fetch parameters for a specific agent.",
                confidence=0.92,
            ),
            IntentPattern(
                name="test_agent_connectivity",
                pattern=re.compile(
                    r"(test|check|validate)\s+(the\s+)?(agent\s+)?(connectivity|connection)\s+(of\s+(agent\s+)?(?P<agent>[a-zA-Z0-9_\-\.]+))\s+(to\s+(the\s+)?(server\s+)?(?P<server>[a-zA-Z0-9_\-\.]+))",
                    re.IGNORECASE,
                ),
                explanation="Detected agent-first connectivity test request.",
                confidence=0.95,
            ),
            IntentPattern(
                name="test_agent_connectivity",
                pattern=re.compile(
                    r"(test|check|validate)\s+(the\s+)?(agent\s+)?(connectivity|connection)\s+(to\s+(the\s+)?)?(server\s+)?(?P<server>[a-zA-Z0-9_\-\.]+)\s+(from\s+(agent\s+)?|for\s+(agent\s+)?)(?P<agent>[a-zA-Z0-9_\-\.]+)",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to test agent connectivity to a server.",
                confidence=0.94,
            ),
            IntentPattern(
                name="test_agent_connectivity",
                pattern=re.compile(
                    r"(test|check|validate)\s+(agent\s+)?(?P<agent>(?!agent\b)[a-zA-Z0-9_\-\.]+)\s+(connectivity|connection)",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to test connectivity for a specific agent.",
                confidence=0.9,
            ),
            IntentPattern(
                name="ping_agent",
                pattern=re.compile(
                    r"(ping)\s+(to\s+the\s+agent|an\s+agent|agent)\.?\s*(?P<agent>[a-zA-Z0-9_\-\.]+)(\s+(on|in|from)\s+(server\s+)?(?P<server>[a-zA-Z0-9_\-\.]+))?",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to ping a specific agent.",
                confidence=0.94,
            ),
            IntentPattern(
                name="ping_agent",
                pattern=re.compile(
                    r"(ping)\s+(agent\s+)?(?P<agent>[a-zA-Z0-9_\-\.]+)",
                    re.IGNORECASE,
                ),
                explanation="Detected a compact request to ping an agent.",
                confidence=0.9,
            ),
            IntentPattern(
                name="get_agent_parameters",
                pattern=re.compile(
                    r"(get|show|list)\s+(agent\s+)?(?P<agent>(?!agent\b)[a-zA-Z0-9_\-\.]+)\s+(parameters?|params?)",
                    re.IGNORECASE,
                ),
                explanation="Detected an alternate phrasing for fetching agent parameters.",
                confidence=0.91,
            ),
            IntentPattern(
                name="list_agents",
                pattern=re.compile(
                    r"^\s*(list|show|get)\s+(all\s+)?agents?\s*$",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to list Control-M agents.",
                confidence=0.87,
            ),
            IntentPattern(
                name="set_agent_parameter",
                pattern=re.compile(
                    r"(set|change|update)\s+(?P<parameter>[a-zA-Z0-9_\-\.\\%]+)\s+(for|on)\s+(?:server\s+)?(?P<server>[a-zA-Z0-9_\-\.]+)\s+(?:and\s+)?(?:agent\s+)?(?P<agent>[a-zA-Z0-9_\-\.]+)\s+(to|=)\s*(?:value\s+)?(?P<value>[^\s]+)",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to set an agent parameter with explicit server and agent.",
                confidence=0.97,
            ),
            IntentPattern(
                name="set_agent_parameter",
                pattern=re.compile(
                    r"(set|change|update)\s+(?P<parameter>[a-zA-Z0-9_\-\.\\%]+)\s*(to|=)\s*(?:value\s+)?(?P<value>[^\s]+)\s+(for|on)\s+(?:server\s+)?(?P<server>[a-zA-Z0-9_\-\.]+)\s+(?:and\s+)?(?:agent\s+)?(?P<agent>[a-zA-Z0-9_\-\.]+)",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to set an agent parameter with explicit value, server, and agent.",
                confidence=0.97,
            ),
            IntentPattern(
                name="set_agent_parameter",
                pattern=re.compile(
                    r"(set|change|update)\s+(?P<parameter>[a-zA-Z0-9_\-\.\\%]+)\s+(for|on)\s+(?:agent\s+)?(?P<agent>[a-zA-Z0-9_\-\.]+)\s+(?:on|for\s+)?(?:server\s+)?(?P<server>[a-zA-Z0-9_\-\.]+)\s+(to|=)\s*(?:value\s+)?(?P<value>[^\s]+)",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to set an agent parameter with explicit agent, server, and value.",
                confidence=0.97,
            ),
            IntentPattern(
                name="set_agent_parameter",
                pattern=re.compile(
                    r"(set|change|update)\s+(?P<parameter>[a-zA-Z0-9_\-\.\\%]+)\s*(to|=)\s*(?:value\s+)?(?P<value>[^\s]+)\s+(for|on)\s+(?:agent\s+)?(?P<agent>[a-zA-Z0-9_\-\.]+)\s+(?:on|for\s+)?(?:server\s+)?(?P<server>[a-zA-Z0-9_\-\.]+)",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to set an agent parameter with explicit value, agent, and server.",
                confidence=0.97,
            ),
            IntentPattern(
                name="set_agent_parameter",
                pattern=re.compile(
                    r"(set|change|update)\s+(agent\s+)?parameter\s+(?P<parameter>[a-zA-Z0-9_\-\.]+)\s*(to|=)\s*(?:value\s+)?(?P<value>[^\s]+)(\s+(for|on)\s+(agent\s+)?(?P<agent>[a-zA-Z0-9_\-\.]+|all))?",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to set a Control-M agent parameter.",
                confidence=0.9,
            ),
            IntentPattern(
                name="set_agent_parameter",
                pattern=re.compile(
                    r"(set|change|update)\s+(?P<parameter>[a-zA-Z0-9_\-\.]+)\s+parameters?\s+(for|on)\s+(agent\s+)?(?P<agent>[a-zA-Z0-9_\-\.]+|all)\s*(to|=)\s*(?:value\s+)?(?P<value>[^\s]+)",
                    re.IGNORECASE,
                ),
                explanation="Detected set-parameter phrasing with explicit agent target.",
                confidence=0.95,
            ),
            IntentPattern(
                name="set_agent_parameter",
                pattern=re.compile(
                    r"(set|change|update)\s+(?P<parameter>[a-zA-Z0-9_\-\.]+)\s*(to|=)\s*(?:value\s+)?(?P<value>[^\s]+)(\s+(for|on)\s+(agent\s+)?(?P<agent>[a-zA-Z0-9_\-\.]+|all))?",
                    re.IGNORECASE,
                ),
                explanation="Detected a request to set an agent parameter.",
                confidence=0.83,
            ),
        ]

    def parse(self, message: str) -> IntentResult:
        text = message.strip()
        for candidate in self.patterns:
            match = candidate.pattern.search(text)
            if match:
                entities = {k: v for k, v in match.groupdict().items() if v}
                entities["_raw_message"] = text
                return IntentResult(
                    intent=candidate.name,
                    entities=entities,
                    confidence=candidate.confidence,
                    explanation=candidate.explanation,
                )

        return IntentResult(
            intent="unknown",
            entities={"_raw_message": text},
            confidence=0.1,
            explanation="Could not match an automation intent.",
        )


def map_nlp_to_api(intent: IntentResult, valid_api_ids: set) -> Optional[dict]:
    """
    Maps parsed NLP intent and entities to a registry API ID and parameters.
    """
    intent_name = intent.intent
    entities = intent.entities

    # Define how NLP intents map to our 6 registry APIs
    mapping = {
        "get_connection_profiles": "get_centralized_connection_profiles",
        "get_connection_profiles_status": "get_centralized_connection_profiles",
        "get_agent_parameters": "get_agent_parameters",
        "set_agent_parameter": "set_agent_parameter",
        "test_agent_connectivity": "analyze_agent_communication",
        "ping_agent": "analyze_agent_communication",
        "analyze_agent_communication": "analyze_agent_communication",
        "get_server_agentless_hosts": "get_server_agentless_hosts",
        "set_server_desired_state": "set_server_desired_state",
    }

    mapped_api = mapping.get(intent_name)
    if not mapped_api or mapped_api not in valid_api_ids:
        return None

    # Map entity parameters to those expected by registry APIs
    mapped_entities = {}
    
    # 1. server -> server
    if "server" in entities:
        mapped_entities["server"] = entities["server"]

    # 2. agent -> agent
    if "agent" in entities:
        mapped_entities["agent"] = entities["agent"]

    # 3. type -> type
    if "type" in entities:
        mapped_entities["type"] = entities["type"]

    # 4. name -> name
    if "name" in entities:
        mapped_entities["name"] = entities["name"]

    # 5. set_agent_parameter mapping: 'parameter' -> 'name', 'value' -> 'value'
    if mapped_api == "set_agent_parameter":
        if "parameter" in entities:
            mapped_entities["name"] = entities["parameter"]
        if "value" in entities:
            mapped_entities["value"] = entities["value"]

    # 6. set_server_desired_state state mapping
    if mapped_api == "set_server_desired_state":
        if "state" in entities:
            # Capitalize to match "Up", "Down", "Recycle", "Ignore" enum
            state_val = entities["state"].strip().capitalize()
            if state_val in ("Up", "Down", "Recycle", "Ignore"):
                mapped_entities["state"] = state_val
        elif "action" in entities:
            # Map action keywords to state enums
            action = entities["action"].lower()
            action_map = {
                "start": "Up",
                "stop": "Down",
                "recycle": "Recycle",
                "ignore": "Ignore",
            }
            if action in action_map:
                mapped_entities["state"] = action_map[action]

    return {
        "api_id": mapped_api,
        "extracted_entities": mapped_entities,
    }
