"""Skill tool for executing custom commands."""

from nanocode.skills import SkillsManager
from nanocode.tools import Tool, ToolResult


class SkillTool(Tool):
    """Tool for executing custom skills/commands."""

    def __init__(self, skills_manager: SkillsManager):
        super().__init__(
            name="skill",
            description="Load a specialized skill that provides domain-specific instructions. When you recognize that a task matches one of the available skills listed below, use this tool to load the full skill instructions. The skill will inject detailed instructions and workflows into the conversation context. Use name=<skill-name> to load a skill, then FOLLOW its instructions.",
            parameters={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the skill to execute (e.g., mcp-builder, skill-creator, python-project-scaffold)",
                    },
                    "input": {
                        "type": "string",
                        "description": "The user's actual request to pass to the skill (e.g., 'build an MCP server for my API').",
                    },
                },
                "required": ["name"],
            },
        )
        self.skills_manager = skills_manager

    async def execute(
        self, name: str = None, input: str = None, **kwargs
    ) -> ToolResult:
        """Execute a skill by name."""
        if not name:
            return ToolResult(
                success=False, content=None, error="Skill name is required"
            )

        try:
            self.skills_manager.get_skill(name)

            context = {
                "input": input or "",
                "kwargs": kwargs,
            }

            result = await self.skills_manager.execute_skill(
                name, {"input": input}, context
            )

            return ToolResult(success=True, content=result)
        except Exception as e:
            return ToolResult(success=False, content=None, error=str(e))


class ListSkillsTool(Tool):
    """Tool for listing available skills."""

    def __init__(self, skills_manager: SkillsManager):
        super().__init__(
            name="list_skills",
            description="[DEPRECATED] Use the 'skill' tool directly instead. When you want to use a skill, call skill(name='<skill-name>', input='<your-request>') directly without listing first.",
            parameters={
                "type": "object",
                "properties": {},
            },
        )
        self.skills_manager = skills_manager

    async def execute(self, **kwargs) -> ToolResult:
        """List all available skills."""
        try:
            skills = self.skills_manager.list_skills()
            lines = [
                "Use the 'skill' tool directly instead of listing. Example:",
                "  skill(name='mcp-builder', input='build a server for my API')",
                "",
                "Available skills (use skill tool, don't call list_skills):",
            ]
            for s in skills:
                lines.append(f"  - {s['name']}: {s['description']}")

            return ToolResult(success=True, content="\n".join(lines))
        except Exception as e:
            return ToolResult(success=False, content=None, error=str(e))


def register_skill_tools(registry, skills_manager: SkillsManager):
    """Register skill-related tools."""
    registry.register(SkillTool(skills_manager))
    registry.register(ListSkillsTool(skills_manager))
