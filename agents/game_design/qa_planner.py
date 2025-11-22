"""
QA Planner Agent for LUDEX Framework (Sprint 16)

Defines QA testing strategy including test phases, playtesting strategy,
bug tracking recommendations, and certification requirements.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def qa_planner_node(state: GameDesignState) -> GameDesignState:
    """
    QA Planner Agent Node.
    Role: Define comprehensive QA and testing strategy.
    """
    logger.info("qa_planner_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.6
        )
        
        mechanics = state.get("mechanics", [])
        target_platforms = state.get("target_platforms", [])
        
        system_msg = SystemMessage(content="""You are a **QA Lead** for game development.

Design comprehensive QA strategy to ensure quality and smooth launch.

Output JSON:
```json
{
  "test_phases": {
    "alpha": {
      "duration": "4 weeks",
      "focus": "Core gameplay loop, critical bugs",
      "testers": "Internal team (5-10 people)",
      "success_criteria": "No game-breaking bugs, core loop is fun"
    },
    "closed_beta": {
      "duration": "6 weeks",
      "focus": "Balance, progression, multiplayer stability",
      "testers": "External 100-500 players (NDA)",
      "success_criteria": "Positive feedback on retention, <5 critical bugs"
    },
    "open_beta": {
      "duration": "2 weeks",
      "focus": "Server load testing, final polish",
      "testers": "Public 10k+ players",
      "success_criteria": "Server stability, <10 known bugs at launch"
    }
  },
  "playtesting_strategy": {
    "frequency": "Weekly playtests from alpha onwards",
    "session_structure": [
      "Pre-test survey (expectations)",
      "30-60 min gameplay session",
      "Post-test survey (experience, bugs, fun factor)",
      "Optional interview (5-10 players)"
    ],
    "metrics_tracked": [
      "Session length",
      "Completion rate",
      "Drop-off points",
      "Fun rating (1-10 scale)"
    ],
    "iteration_cycle": "Implement fixes within 1 sprint, re-test next week"
  },
  "bug_tracking": {
    "recommended_tool": "Jira / Linear / GitHub Issues",
    "priority_levels": [
      {"level": "P0 - Critical", "example": "Game crashes on startup", "fix_time": "<24h"},
      {"level": "P1 - High", "example": "Progression blocker", "fix_time": "<1 week"},
      {"level": "P2 - Medium", "example": "UI visual bug", "fix_time": "<2 weeks"},
      {"level": "P3 - Low", "example": "Minor typo", "fix_time": "Nice to have"}
    ],
    "bug_workflow": "New → In Progress → Code Review → QA Verification → Closed",
    "regression_testing": "Re-test all P0/P1 bugs after every build"
  },
  "certification_requirements": {
    "pc_steam": [
      "Steam Partner Agreement compliance",
      "Age rating (ESRB/PEGI)",
      "Privacy policy for data collection"
    ],
    "console_ps5_xbox": [
      "Technical Requirements Checklist (TRC/XR)",
      "Submission builds 4-6 weeks before launch",
      "Age rating certification",
      "Accessibility features (per platform guidelines)"
    ],
    "mobile_ios_android": [
      "App Store Review Guidelines compliance",
      "Google Play policies compliance",
      "COPPA compliance if targeting children",
      "In-app purchase disclosure"
    ]
  },
  "automated_testing": {
    "unit_tests": "Core gameplay systems (damage calculation, inventory)",
    "integration_tests": "Save/load, multiplayer matchmaking",
    "performance_tests": "FPS profiling on target hardware",
    "ci_cd_pipeline": "Run tests on every commit, block merge if tests fail"
  },
  "launch_readiness_checklist": [
    "All P0/P1 bugs resolved",
    "Performance targets met on min-spec hardware",
    "Localization complete and tested",
    "Server infrastructure stress-tested",
    "Day-one patch prepared (if needed)",
    "Community management team briefed"
  ]
}
```""")
        
        human_msg = HumanMessage(content=f"""Define QA strategy for:
**Mechanics**: {mechanics}
**Platforms**: {target_platforms}

Create:
1. Test phases (alpha, beta, open beta)
2. Playtesting strategy with metrics
3. Bug tracking workflow
4. Certification requirements per platform
5. Launch readiness checklist""")
        
        result = await safe_agent_invoke(
            agent_name="QAPlanner",
            llm=llm,
            messages=[system_msg, human_msg],
            state=state,
            tools=[]
        )
        
        if result is None:
            return state
        
        output = result.get("content", "{}")
        if "```json" in output:
            output = output.split("```json")[1].split("```")[0].strip()
        
        import json
        try:
            qa_plan = json.loads(output)
        except json.JSONDecodeError:
            qa_plan = {"raw_output": output}
        
        logger.info("qa_planner_completed")
        
        return {
            **state,
            "qa_plan": qa_plan
        }
    
    except Exception as e:
        logger.exception("qa_planner_error", error=str(e))
        return state
