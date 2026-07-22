"""Builds the LangGraph StateGraph implementing the strict workflow:

START -> upload -> parser -> planner -> [parallel agents] -> assembly
-> validation -> (retry -> validation)* -> rendering -> evaluation -> END
"""
from langgraph.graph import END, StateGraph

from app.agents.achievements.achievements_agent import AchievementsAgent
from app.agents.certifications.certifications_agent import CertificationsAgent
from app.agents.education.education_agent import EducationAgent
from app.agents.experience.experience_agent import ExperienceAgent
from app.agents.links.links_agent import LinksAgent
from app.agents.projects.projects_agent import ProjectsAgent
from app.agents.skills.skills_agent import SkillsAgent
from app.agents.summary.summary_agent import SummaryAgent
from app.graph.executor import retry_failed_sections
from app.graph.router import route_after_validation
from app.nodes.assembly_node import assembly_node
from app.nodes.evaluation_node import evaluation_node
from app.nodes.parser_node import parser_node
from app.nodes.planner_node import planner_node
from app.nodes.rendering_node import rendering_node
from app.nodes.upload_node import upload_node
from app.nodes.validation_node import validation_node
from app.schemas.state_schema import ResumeCopilotState

_GENERATION_AGENTS = {
    "summary_node": SummaryAgent(),
    "skills_node": SkillsAgent(),
    "experience_node": ExperienceAgent(),
    "projects_node": ProjectsAgent(),
    "education_node": EducationAgent(),
    "certifications_node": CertificationsAgent(),
    "achievements_node": AchievementsAgent(),
    "links_node": LinksAgent(),
}


def build_graph():
    """Construct and compile the LangGraph StateGraph."""
    graph = StateGraph(ResumeCopilotState)

    graph.add_node("upload", upload_node)
    graph.add_node("parser", parser_node)
    graph.add_node("planner", planner_node)

    for node_name, agent in _GENERATION_AGENTS.items():
        graph.add_node(node_name, agent.run)

    graph.add_node("assembly", assembly_node)
    graph.add_node("validation", validation_node)
    graph.add_node("retry", retry_failed_sections)
    graph.add_node("rendering", rendering_node)
    graph.add_node("evaluation", evaluation_node)

    graph.set_entry_point("upload")
    graph.add_edge("upload", "parser")
    graph.add_edge("parser", "planner")

    # Fan-out: planner triggers all 8 agents to run in parallel.
    for node_name in _GENERATION_AGENTS:
        graph.add_edge("planner", node_name)

    # Fan-in: all agents converge on assembly.
    for node_name in _GENERATION_AGENTS:
        graph.add_edge(node_name, "assembly")

    graph.add_edge("assembly", "validation")

    graph.add_conditional_edges(
        "validation",
        route_after_validation,
        {"rendering": "rendering", "retry": "retry"},
    )
    graph.add_edge("retry", "validation")

    graph.add_edge("rendering", "evaluation")
    graph.add_edge("evaluation", END)

    return graph.compile()
