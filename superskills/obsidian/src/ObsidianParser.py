"""
Parser utilities for Obsidian Markdown files.
"""
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import yaml


def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """
    Extract YAML frontmatter from Markdown content.
    
    Args:
        content: Full Markdown content
        
    Returns:
        Tuple of (frontmatter_dict, content_without_frontmatter)
    """
    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    try:
        frontmatter = yaml.safe_load(parts[1]) or {}
        body = parts[2].lstrip('\n')
        return frontmatter, body
    except yaml.YAMLError:
        return {}, content


def serialize_frontmatter(frontmatter: Dict) -> str:
    """
    Convert frontmatter dict to YAML string with delimiters.
    
    Args:
        frontmatter: Frontmatter dictionary
        
    Returns:
        YAML string wrapped in --- delimiters
    """
    if not frontmatter:
        return ""

    yaml_content = yaml.dump(
        frontmatter,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False
    )
    return f"---\n{yaml_content}---\n"


def merge_frontmatter(existing: Dict, new: Dict, update_modified: bool = True) -> Dict:
    """
    Merge two frontmatter dictionaries.
    
    Args:
        existing: Existing frontmatter
        new: New frontmatter to merge
        update_modified: Whether to update modified timestamp
        
    Returns:
        Merged frontmatter dict
    """
    merged = existing.copy()

    for key, value in new.items():
        if key == 'tags' and key in merged:
            existing_tags = merged['tags'] if isinstance(merged['tags'], list) else []
            new_tags = value if isinstance(value, list) else []
            merged['tags'] = list(set(existing_tags + new_tags))
        else:
            merged[key] = value

    if update_modified:
        merged['modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return merged


def extract_headings(content: str) -> List[Tuple[int, str]]:
    """
    Extract headings from Markdown content.
    
    Args:
        content: Markdown content
        
    Returns:
        List of (level, text) tuples
    """
    headings = []
    heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    for match in heading_pattern.finditer(content):
        level = len(match.group(1))
        text = match.group(2).strip()
        headings.append((level, text))

    return headings


def extract_tags_from_frontmatter(frontmatter: Dict) -> List[str]:
    """
    Extract tags from frontmatter.
    
    Args:
        frontmatter: Frontmatter dictionary
        
    Returns:
        List of tags
    """
    tags = frontmatter.get('tags', [])

    if isinstance(tags, str):
        return [tags]
    elif isinstance(tags, list):
        return [str(tag) for tag in tags]
    else:
        return []


def extract_links(content: str) -> List[str]:
    """
    Extract wiki links from Markdown content.
    
    Args:
        content: Markdown content
        
    Returns:
        List of linked note titles/paths
    """
    links = []

    # Match [[Link]] or [[Link|Alias]]
    link_pattern = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')

    for match in link_pattern.finditer(content):
        link_target = match.group(1).strip()
        links.append(link_target)

    return links


def find_section(content: str, heading: str) -> Optional[Tuple[int, int]]:
    """
    Find the start and end position of a section under a heading.
    
    Args:
        content: Markdown content
        heading: Heading text to find (case-insensitive)
        
    Returns:
        Tuple of (start_index, end_index) or None if not found
    """
    heading_lower = heading.lower().strip('#').strip()

    heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    matches = list(heading_pattern.finditer(content))

    target_match = None
    target_level = None

    for match in matches:
        level = len(match.group(1))
        text = match.group(2).strip().lower()

        if text == heading_lower:
            target_match = match
            target_level = level
            break

    if not target_match:
        return None

    start_index = target_match.end()

    for match in matches:
        if match.start() <= target_match.start():
            continue

        level = len(match.group(1))
        if level <= target_level:
            return (start_index, match.start())

    return (start_index, len(content))


def update_link_in_content(content: str, old_target: str, new_target: str) -> str:
    """
    Update wiki links in content from old target to new target.
    
    Args:
        content: Markdown content
        old_target: Old link target
        new_target: New link target
        
    Returns:
        Updated content
    """
    old_escaped = re.escape(old_target)

    # Match [[old_target]] or [[old_target|Alias]]
    pattern = re.compile(
        r'\[\[' + old_escaped + r'(\|[^\]]+)?\]\]',
        re.IGNORECASE
    )

    def replacement(match):
        alias = match.group(1) or ''
        return f"[[{new_target}{alias}]]"

    return pattern.sub(replacement, content)


def get_title_from_content(content: str, frontmatter: Dict, filename: str) -> str:
    """
    Extract title from content in priority order.
    
    Args:
        content: Markdown content
        frontmatter: Frontmatter dict
        filename: Filename without extension
        
    Returns:
        Note title
    """
    if 'title' in frontmatter:
        return str(frontmatter['title'])

    headings = extract_headings(content)
    if headings and headings[0][0] == 1:
        return headings[0][1]

    return filename
