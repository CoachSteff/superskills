"""
Skill discovery and loading system.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cli.utils.logger import get_logger
from cli.utils.master_briefing import MasterBriefingLoader
from cli.utils.paths import get_skills_dir


@dataclass
class SkillInfo:
    name: str
    description: str
    skill_type: str  # "prompt" or "python"
    path: Path
    has_profile: bool
    python_module: Optional[str] = None
    parent_skill: Optional[str] = None  # For hierarchical display


class SkillLoader:
    PYTHON_SKILLS = {
        'narrator': 'superskills.narrator.src.Voiceover:VoiceoverGenerator',
        'narrator-podcast': 'superskills.narrator.src.Voiceover:VoiceoverGenerator',
        'narrator-meditation': 'superskills.narrator.src.Voiceover:VoiceoverGenerator',
        'narrator-educational': 'superskills.narrator.src.Voiceover:VoiceoverGenerator',
        'narrator-marketing': 'superskills.narrator.src.Voiceover:VoiceoverGenerator',
        'narrator-social': 'superskills.narrator.src.Voiceover:VoiceoverGenerator',
        'transcriber': 'superskills.transcriber.src.Transcriber:Transcriber',
        'designer': 'superskills.designer.src.ImageGenerator:ImageGenerator',
        'scraper': 'superskills.scraper.src.WebScraper:WebScraper',
        'craft': 'superskills.craft.src.CraftClient:CraftClient',
        'marketer': 'superskills.marketer.src.SocialMediaPublisher:SocialMediaPublisher',
        'presenter': 'superskills.presenter.src.Presenter:Presenter',
        'videoeditor': 'superskills.videoeditor.src.VideoEditor:VideoEditor',
        'coursepackager': 'superskills.coursepackager.src.CoursePackager:CoursePackager',
        'emailcampaigner': 'superskills.emailcampaigner.src.EmailCampaigner:EmailCampaigner',
        'obsidian': 'superskills.obsidian.src.ObsidianClient:ObsidianClient',
    }

    def __init__(self):
        self.skills_dir = get_skills_dir()
        self._skill_cache: Dict[str, SkillInfo] = {}
        self.master_briefing_loader = MasterBriefingLoader()
        self.logger = get_logger()

    def discover_skills(self) -> List[SkillInfo]:
        skills = []

        for item in self.skills_dir.iterdir():
            if not item.is_dir():
                continue

            if item.name.startswith('.') or item.name == 'cli':
                continue

            skill_md = item / "SKILL.md"
            if not skill_md.exists():
                continue

            skill_info = self._load_skill_info(item)
            if skill_info:
                skills.append(skill_info)
                self._skill_cache[skill_info.name] = skill_info

                # Discover subskills (nested skills within parent skill directory)
                for subdir in item.iterdir():
                    if not subdir.is_dir():
                        continue
                    if subdir.name.startswith('.') or subdir.name == 'src':
                        continue

                    subskill_md = subdir / "SKILL.md"
                    if subskill_md.exists():
                        subskill_info = self._load_skill_info(subdir, parent_skill=skill_info.name)
                        if subskill_info:
                            skills.append(subskill_info)
                            self._skill_cache[subskill_info.name] = subskill_info

        return sorted(skills, key=lambda s: s.name)

    def _load_skill_info(self, skill_path: Path, parent_skill: Optional[str] = None) -> Optional[SkillInfo]:
        skill_md = skill_path / "SKILL.md"

        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()

            metadata = self._parse_frontmatter(content)
            if not metadata:
                return None

            name = metadata.get('name', skill_path.name)
            description = metadata.get('description', 'No description')

            skill_type = 'python' if name in self.PYTHON_SKILLS else 'prompt'
            python_module = self.PYTHON_SKILLS.get(name) if skill_type == 'python' else None

            profile_md = skill_path / "PROFILE.md"
            profile_template = skill_path / "PROFILE.md.template"
            has_profile = profile_md.exists() or profile_template.exists()

            return SkillInfo(
                name=name,
                description=description,
                skill_type=skill_type,
                path=skill_path,
                has_profile=has_profile,
                python_module=python_module,
                parent_skill=parent_skill
            )

        except Exception as e:
            print(f"Warning: Failed to load skill from {skill_path}: {e}")
            return None

    def _parse_frontmatter(self, content: str) -> Optional[Dict]:
        if not content.startswith('---'):
            return None

        parts = content.split('---', 2)
        if len(parts) < 3:
            return None

        try:
            return yaml.safe_load(parts[1])
        except Exception:
            return None

    def get_skill(self, skill_name: str) -> Optional[SkillInfo]:
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]

        self.discover_skills()
        return self._skill_cache.get(skill_name)

    def load_skill_content(self, skill_name: str) -> Dict[str, Any]:
        """
        Load skill content with hierarchical profile system.

        Returns:
            Dict with keys: 'skill', 'master_briefing', 'profile'
        """
        skill_info = self.get_skill(skill_name)
        if not skill_info:
            raise ValueError(f"Skill not found: {skill_name}")

        # 1. Load SKILL.md (required - base role definition)
        skill_md_path = skill_info.path / "SKILL.md"
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            skill_content = f.read()

        # 2. Load Master Briefing (optional - global brand voice)
        master_briefing_content = None
        try:
            master_briefing = self.master_briefing_loader.load()
            if master_briefing:
                master_briefing_content = self.master_briefing_loader.format_for_prompt()
                self.logger.debug(f"Master Briefing loaded ({len(master_briefing_content)} chars)")
        except Exception as e:
            self.logger.debug(f"Master Briefing not available: {e}")

        # 3. Load skill-specific PROFILE.md (optional - specific customization)
        profile_content = None
        profile_md = skill_info.path / "PROFILE.md"
        profile_template = skill_info.path / "PROFILE.md.template"

        if profile_md.exists():
            with open(profile_md, 'r', encoding='utf-8') as f:
                profile_content = f.read()
            self.logger.debug(f"Skill profile loaded: {skill_name}")
        elif profile_template.exists():
            # Fallback to template if no custom profile
            with open(profile_template, 'r', encoding='utf-8') as f:
                profile_content = f.read()
            self.logger.debug(f"Using profile template: {skill_name}")

        return {
            'skill': skill_content,
            'master_briefing': master_briefing_content,
            'profile': profile_content
        }

    def list_skills(self, skill_type: Optional[str] = None) -> List[SkillInfo]:
        skills = self.discover_skills()

        if skill_type:
            skills = [s for s in skills if s.skill_type == skill_type]

        return skills
