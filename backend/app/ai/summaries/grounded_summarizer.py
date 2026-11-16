from typing import Any
from app.models.user import User


class GroundedSummarizer:
    @staticmethod
    def generate_candidate_summary(user: User) -> str:
        """Generate a concise profile summary grounded entirely in verified profile data."""
        name = user.profile.display_name if user.profile else "Developer"
        skills = [s.skill_name for s in (user.skills or [])]
        projects = [p.name for p in (user.projects or [])]
        domains = (user.profile.domains_of_interest if user.profile else []) or []

        skill_text = ", ".join(skills[:5]) if skills else "various technical capabilities"
        domain_text = ", ".join(domains[:3]) if domains else "technology solutions"
        project_count = len(projects)

        summary = (
            f"{name} is an active builder focusing on {domain_text} with core competencies in {skill_text}. "
            f"Demonstrated project portfolio includes {project_count} project(s)"
        )
        if projects:
            summary += f", including '{projects[0]}'."
        else:
            summary += "."

        return f"[AI-Generated Summary] {summary}"

    @staticmethod
    def generate_project_summary(name: str, description: str, technologies: list[str]) -> str:
        tech_text = ", ".join(technologies) if technologies else "modern stack"
        return f"[AI-Generated Summary] Project '{name}' utilizes {tech_text} to solve: {description}"
