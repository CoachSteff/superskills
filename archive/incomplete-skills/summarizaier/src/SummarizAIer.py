"""
SummarizAIer.py - AI-powered text summarization using OpenAI.
"""
import os
from typing import Dict, List, Optional, Literal
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import json

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai not available - install with: pip install openai")


@dataclass
class SummaryResult:
    """Result from a summarization operation."""
    source_text: str
    summary: str
    summary_type: str
    word_count_original: int
    word_count_summary: int
    compression_ratio: float
    output_file: str = ""
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class SummarizAIer:
    """AI-powered text summarization using OpenAI."""
    
    def __init__(
        self,
        output_dir: str = "output/summaries",
        model: str = "gpt-4o-mini",
        verbose: bool = True
    ):
        """Initialize SummarizAIer.
        
        Args:
            output_dir: Directory to save summaries
            model: OpenAI model to use
            verbose: Enable verbose logging
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        self.model = model
        
        if not OPENAI_AVAILABLE:
            raise ImportError("openai is required. Install with: pip install openai")
        
        # Validate environment variable
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def summarize(
        self,
        text: str,
        style: Literal["concise", "detailed", "executive"] = "concise",
        max_length: Optional[int] = None,
        output_format: Literal["text", "json"] = "text"
    ) -> SummaryResult:
        """Summarize text.
        
        Args:
            text: Text to summarize
            style: Summary style (concise, detailed, executive)
            max_length: Maximum summary length in words
            output_format: Output format (text or json)
            
        Returns:
            SummaryResult with summary and metadata
        """
        if self.verbose:
            print(f"Summarizing {len(text.split())} words...")
        
        # Build prompt based on style
        if style == "concise":
            prompt = "Provide a brief, concise summary of the following text in 2-3 sentences:"
        elif style == "detailed":
            prompt = "Provide a detailed summary of the following text, covering all main points:"
        elif style == "executive":
            prompt = "Provide an executive summary of the following text, highlighting key insights and takeaways:"
        else:
            prompt = "Summarize the following text:"
        
        if max_length:
            prompt += f" Keep the summary under {max_length} words."
        
        prompt += f"\n\n{text}"
        
        # Generate summary
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional summarization assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        summary = response.choices[0].message.content.strip()
        
        # Calculate metrics
        word_count_original = len(text.split())
        word_count_summary = len(summary.split())
        compression_ratio = word_count_summary / word_count_original if word_count_original > 0 else 0
        
        result = SummaryResult(
            source_text=text[:500] + "..." if len(text) > 500 else text,
            summary=summary,
            summary_type=style,
            word_count_original=word_count_original,
            word_count_summary=word_count_summary,
            compression_ratio=compression_ratio
        )
        
        # Save summary
        output_file = self._save_summary(result, output_format)
        result.output_file = output_file
        
        if self.verbose:
            print(f"✓ Summary: {word_count_summary} words ({compression_ratio:.1%} of original)")
            print(f"✓ Saved to: {output_file}")
        
        return result
    
    def extract_key_points(
        self,
        text: str,
        num_points: int = 5,
        format_as_bullets: bool = True
    ) -> List[str]:
        """Extract key points from text.
        
        Args:
            text: Text to extract key points from
            num_points: Number of key points to extract
            format_as_bullets: Format as bullet points
            
        Returns:
            List of key points
        """
        if self.verbose:
            print(f"Extracting {num_points} key points...")
        
        prompt = f"Extract the {num_points} most important key points from the following text. "
        if format_as_bullets:
            prompt += "Format each point as a bullet point starting with '-'."
        else:
            prompt += "List each point on a new line."
        
        prompt += f"\n\n{text}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at identifying key information."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse key points
        if format_as_bullets:
            points = [
                line.strip('- ').strip()
                for line in content.split('\n')
                if line.strip().startswith('-') or line.strip().startswith('*')
            ]
        else:
            points = [line.strip() for line in content.split('\n') if line.strip()]
        
        if self.verbose:
            print(f"✓ Extracted {len(points)} key points")
        
        return points
    
    def extract_action_items(
        self,
        text: str,
        include_assignee: bool = False
    ) -> List[Dict[str, str]]:
        """Extract action items from text.
        
        Args:
            text: Text to extract action items from
            include_assignee: Include assignee information
            
        Returns:
            List of action item dicts
        """
        if self.verbose:
            print("Extracting action items...")
        
        prompt = "Extract all action items from the following text. "
        if include_assignee:
            prompt += "For each action item, identify the action and assignee (if mentioned). "
            prompt += "Format as: 'ACTION | ASSIGNEE' or 'ACTION | Unassigned' if no assignee."
        else:
            prompt += "List each action item on a new line starting with '-'."
        
        prompt += f"\n\n{text}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at identifying action items and tasks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse action items
        action_items = []
        for line in content.split('\n'):
            line = line.strip('- ').strip('* ').strip()
            if not line:
                continue
            
            if include_assignee and '|' in line:
                parts = line.split('|', 1)
                action_items.append({
                    "action": parts[0].strip(),
                    "assignee": parts[1].strip() if len(parts) > 1 else "Unassigned"
                })
            else:
                action_items.append({
                    "action": line,
                    "assignee": "Unassigned"
                })
        
        if self.verbose:
            print(f"✓ Extracted {len(action_items)} action items")
        
        # Save action items
        self._save_action_items(action_items)
        
        return action_items
    
    def generate_study_guide(
        self,
        text: str,
        include_questions: bool = True,
        num_questions: int = 5
    ) -> Dict[str, any]:
        """Generate a study guide from educational content.
        
        Args:
            text: Educational text to generate study guide from
            include_questions: Include practice questions
            num_questions: Number of practice questions
            
        Returns:
            Dict with study guide components
        """
        if self.verbose:
            print("Generating study guide...")
        
        # Generate main summary
        summary_result = self.summarize(text, style="detailed")
        
        # Extract key concepts
        key_points = self.extract_key_points(text, num_points=10)
        
        study_guide = {
            "summary": summary_result.summary,
            "key_concepts": key_points,
            "practice_questions": []
        }
        
        # Generate practice questions
        if include_questions:
            prompt = f"Based on the following text, create {num_questions} practice questions "
            prompt += "that test understanding of the key concepts. Format as numbered questions.\n\n"
            prompt += text
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            
            questions_text = response.choices[0].message.content.strip()
            questions = [
                line.strip()
                for line in questions_text.split('\n')
                if line.strip() and any(char.isdigit() for char in line[:3])
            ]
            
            study_guide["practice_questions"] = questions
        
        # Save study guide
        output_file = self._save_study_guide(study_guide)
        study_guide["output_file"] = output_file
        
        if self.verbose:
            print(f"✓ Study guide created with {len(key_points)} concepts")
            if include_questions:
                print(f"✓ Generated {len(study_guide['practice_questions'])} practice questions")
            print(f"✓ Saved to: {output_file}")
        
        return study_guide
    
    def _save_summary(
        self,
        result: SummaryResult,
        format: Literal["text", "json"]
    ) -> str:
        """Save summary to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == "text":
            output_file = self.output_dir / f"summary_{timestamp}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Summary ({result.summary_type})\n")
                f.write(f"{'=' * 50}\n\n")
                f.write(result.summary)
                f.write(f"\n\n{'=' * 50}\n")
                f.write(f"Original: {result.word_count_original} words\n")
                f.write(f"Summary: {result.word_count_summary} words\n")
                f.write(f"Compression: {result.compression_ratio:.1%}\n")
        
        elif format == "json":
            output_file = self.output_dir / f"summary_{timestamp}.json"
            data = {
                "summary": result.summary,
                "summary_type": result.summary_type,
                "word_count_original": result.word_count_original,
                "word_count_summary": result.word_count_summary,
                "compression_ratio": result.compression_ratio,
                "timestamp": result.timestamp
            }
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(output_file)
    
    def _save_action_items(self, action_items: List[Dict[str, str]]):
        """Save action items to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"action_items_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(action_items, f, indent=2, ensure_ascii=False)
    
    def _save_study_guide(self, study_guide: Dict) -> str:
        """Save study guide to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"study_guide_{timestamp}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Study Guide\n\n")
            f.write("## Summary\n\n")
            f.write(study_guide["summary"])
            f.write("\n\n## Key Concepts\n\n")
            for i, concept in enumerate(study_guide["key_concepts"], 1):
                f.write(f"{i}. {concept}\n")
            
            if study_guide.get("practice_questions"):
                f.write("\n## Practice Questions\n\n")
                for question in study_guide["practice_questions"]:
                    f.write(f"{question}\n")
        
        return str(output_file)


def summarize_text(
    text: str,
    output_dir: str = "output/summaries",
    **kwargs
) -> SummaryResult:
    """Convenience function to summarize text.
    
    Args:
        text: Text to summarize
        output_dir: Output directory
        **kwargs: Additional arguments for SummarizAIer
        
    Returns:
        SummaryResult
    """
    summarizer = SummarizAIer(output_dir=output_dir)
    return summarizer.summarize(text, **kwargs)
