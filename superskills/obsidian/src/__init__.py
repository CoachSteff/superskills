"""
Obsidian skill package.
"""
from .ObsidianClient import ObsidianClient
from .ObsidianDocument import (
    ObsidianChangesPlan,
    ObsidianNote,
    ObsidianOperationResult,
    PlannedOperation,
)

__all__ = [
    'ObsidianClient',
    'ObsidianNote',
    'ObsidianOperationResult',
    'PlannedOperation',
    'ObsidianChangesPlan',
    'execute'
]


def execute(action: str, **kwargs) -> dict:
    """
    CLI execution wrapper for Obsidian skill.
    
    Args:
        action: Action to perform
        **kwargs: Action-specific arguments
        
    Returns:
        Result dictionary
    """
    vault_path = kwargs.get('vault_path')
    read_only = kwargs.get('read_only', False)

    client = ObsidianClient(vault_path=vault_path, read_only=read_only)

    if action == "list":
        notes = client.list_notes(
            folder=kwargs.get("folder"),
            recursive=kwargs.get("recursive", True)
        )
        return {"notes": [note.dict() for note in notes]}

    elif action == "get":
        note = client.get_note(kwargs["path"])
        return {"note": note.dict() if note else None}

    elif action == "search":
        notes = client.search_notes(
            query=kwargs["query"],
            search_in=kwargs.get("search_in", "both"),
            case_sensitive=kwargs.get("case_sensitive", False),
            limit=kwargs.get("limit", 50)
        )
        return {"results": [note.dict() for note in notes]}

    elif action == "find_by_tag":
        notes = client.find_by_tag(
            tag=kwargs["tag"],
            exact_match=kwargs.get("exact_match", False)
        )
        return {"results": [note.dict() for note in notes]}

    elif action == "find_by_tags":
        notes = client.find_by_tags(
            tags=kwargs["tags"],
            match_all=kwargs.get("match_all", True)
        )
        return {"results": [note.dict() for note in notes]}

    elif action == "find_backlinks":
        notes = client.find_backlinks(kwargs["path"])
        return {"backlinks": [note.dict() for note in notes]}

    elif action == "create":
        result = client.create_note(
            path=kwargs["path"],
            content=kwargs.get("content", ""),
            title=kwargs.get("title"),
            tags=kwargs.get("tags"),
            frontmatter=kwargs.get("frontmatter"),
            folder=kwargs.get("folder")
        )
        return result.dict()

    elif action == "update":
        result = client.update_note(
            path=kwargs["path"],
            content=kwargs.get("content"),
            frontmatter=kwargs.get("frontmatter"),
            merge_frontmatter_flag=kwargs.get("merge_frontmatter", True)
        )
        return result.dict()

    elif action == "update_section":
        result = client.update_section(
            path=kwargs["path"],
            heading=kwargs["heading"],
            new_content=kwargs["content"]
        )
        return result.dict()

    elif action == "append":
        result = client.append_content(
            path=kwargs["path"],
            content=kwargs["content"]
        )
        return result.dict()

    elif action == "move":
        result = client.move_note(
            source=kwargs["source"],
            destination=kwargs["destination"],
            update_links=kwargs.get("update_links")
        )
        return result.dict()

    elif action == "add_tag":
        result = client.add_tag(
            path=kwargs["path"],
            tag=kwargs["tag"]
        )
        return result.dict()

    elif action == "add_tags":
        result = client.add_tags(
            path=kwargs["path"],
            tags=kwargs["tags"]
        )
        return result.dict()

    elif action == "remove_tag":
        result = client.remove_tag(
            path=kwargs["path"],
            tag=kwargs["tag"]
        )
        return result.dict()

    elif action == "set_tags":
        result = client.set_tags(
            path=kwargs["path"],
            tags=kwargs["tags"]
        )
        return result.dict()

    elif action == "add_link":
        result = client.add_link(
            source_path=kwargs["path"],
            target_note=kwargs["target"],
            position=kwargs.get("position", "end"),
            heading=kwargs.get("heading")
        )
        return result.dict()

    elif action == "create_hub":
        result = client.create_hub(
            hub_path=kwargs["path"],
            title=kwargs["title"],
            linked_notes=kwargs["linked_notes"],
            description=kwargs.get("description"),
            group_by_tag=kwargs.get("group_by_tag")
        )
        return result.dict()

    elif action == "plan":
        plan = client.plan_changes(kwargs["operations"])
        return plan.dict()

    elif action == "apply_plan":
        results = client.apply_plan(kwargs["plan"])
        return {"results": [r.dict() for r in results]}

    else:
        return {
            "success": False,
            "message": f"Unknown action: {action}",
            "available_actions": [
                "list", "get", "search", "find_by_tag", "find_by_tags",
                "find_backlinks", "create", "update", "update_section",
                "append", "move", "add_tag", "add_tags", "remove_tag",
                "set_tags", "add_link", "create_hub", "plan", "apply_plan"
            ]
        }
