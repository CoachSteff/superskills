"""Social Media Publisher - Multi-platform posting via Postiz API."""

import os
from pathlib import Path
from typing import Optional, List, Literal
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
from enum import Enum


class Platform(Enum):
    """Supported social media platforms."""
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"


@dataclass
class PostResult:
    """Result from social media post."""
    post_id: str
    platform: str
    scheduled_time: Optional[str]
    status: str
    preview_url: Optional[str]


class SocialMediaPublisher:
    """Publish content to social media via Postiz API."""
    
    # Character limits per platform
    CHAR_LIMITS = {
        Platform.TWITTER: 280,
        Platform.LINKEDIN: 3000,
        Platform.INSTAGRAM: 2200,
        Platform.FACEBOOK: 63206
    }
    
    # Optimal posting times (EST)
    BEST_TIMES = {
        Platform.LINKEDIN: [
            {"day": "tuesday", "hour": 10},
            {"day": "wednesday", "hour": 12},
            {"day": "thursday", "hour": 9}
        ],
        Platform.TWITTER: [
            {"day": "monday", "hour": 9},
            {"day": "wednesday", "hour": 12},
            {"day": "friday", "hour": 9}
        ],
        Platform.INSTAGRAM: [
            {"day": "monday", "hour": 11},
            {"day": "wednesday", "hour": 14},
            {"day": "friday", "hour": 16}
        ]
    }
    
    def __init__(self):
        """Initialize social media publisher."""
        self.api_key = os.getenv("POSTIZ_API_KEY")
        self.workspace_id = os.getenv("POSTIZ_WORKSPACE_ID")
        
        if not self.api_key:
            raise ValueError("POSTIZ_API_KEY environment variable not set")
        if not self.workspace_id:
            raise ValueError("POSTIZ_WORKSPACE_ID environment variable not set")
        
        self.base_url = "https://api.postiz.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def optimize_for_platform(
        self,
        content: str,
        platform: Platform,
        max_length: Optional[int] = None
    ) -> str:
        """Optimize content for specific platform.
        
        Args:
            content: Original content
            platform: Target platform
            max_length: Override default character limit
            
        Returns:
            Optimized content string
        """
        limit = max_length or self.CHAR_LIMITS[platform]
        
        if len(content) <= limit:
            return content
        
        # Truncate with ellipsis
        truncated = content[:limit-3] + "..."
        return truncated
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text.
        
        Args:
            text: Text containing hashtags
            
        Returns:
            List of hashtag strings (without #)
        """
        import re
        hashtags = re.findall(r'#(\w+)', text)
        return hashtags
    
    def format_hashtags(
        self,
        hashtags: List[str],
        platform: Platform,
        max_tags: int = 5
    ) -> str:
        """Format hashtags for platform.
        
        Args:
            hashtags: List of hashtag strings (without #)
            platform: Target platform
            max_tags: Maximum number of hashtags to include
            
        Returns:
            Formatted hashtag string
        """
        # Limit to max_tags
        tags = hashtags[:max_tags]
        
        # Format based on platform
        if platform == Platform.TWITTER:
            # Twitter: inline hashtags
            return " ".join(f"#{tag}" for tag in tags)
        elif platform == Platform.LINKEDIN:
            # LinkedIn: end of post
            return "\n\n" + " ".join(f"#{tag}" for tag in tags)
        elif platform == Platform.INSTAGRAM:
            # Instagram: separate line
            return "\n\n" + " ".join(f"#{tag}" for tag in tags)
        else:
            return " ".join(f"#{tag}" for tag in tags)
    
    def post(
        self,
        content: str,
        platforms: List[Platform],
        image_path: Optional[str] = None,
        schedule_time: Optional[datetime] = None,
        hashtags: Optional[List[str]] = None,
        link: Optional[str] = None
    ) -> List[PostResult]:
        """Post content to social media platforms.
        
        Args:
            content: Post content/caption
            platforms: List of platforms to post to
            image_path: Optional path to image
            schedule_time: Optional scheduled posting time (None = post now)
            hashtags: Optional list of hashtags (without #)
            link: Optional link to include
            
        Returns:
            List of PostResult objects
        """
        results = []
        
        for platform in platforms:
            # Optimize content for platform
            optimized_content = self.optimize_for_platform(content, platform)
            
            # Add hashtags if provided
            if hashtags:
                hashtag_str = self.format_hashtags(hashtags, platform)
                optimized_content += hashtag_str
            
            # Add link if provided and platform supports
            if link and platform in [Platform.LINKEDIN, Platform.TWITTER]:
                optimized_content += f"\n\n{link}"
            
            # Build post data
            post_data = {
                "workspaceId": self.workspace_id,
                "platform": platform.value,
                "content": optimized_content,
            }
            
            # Add image if provided
            if image_path:
                # Upload image first (simplified - actual implementation may vary)
                post_data["media"] = [{"url": image_path}]
            
            # Add schedule time if provided
            if schedule_time:
                post_data["scheduledAt"] = schedule_time.isoformat()
            
            # Make API call
            try:
                response = requests.post(
                    f"{self.base_url}/posts",
                    headers=self.headers,
                    json=post_data
                )
                response.raise_for_status()
                
                result_data = response.json()
                
                results.append(PostResult(
                    post_id=result_data.get("id", "unknown"),
                    platform=platform.value,
                    scheduled_time=schedule_time.isoformat() if schedule_time else None,
                    status="scheduled" if schedule_time else "published",
                    preview_url=result_data.get("previewUrl")
                ))
                
            except Exception as e:
                print(f"Error posting to {platform.value}: {e}")
                results.append(PostResult(
                    post_id="",
                    platform=platform.value,
                    scheduled_time=None,
                    status=f"failed: {str(e)}",
                    preview_url=None
                ))
        
        return results
    
    def get_optimal_time(
        self,
        platform: Platform,
        days_ahead: int = 1
    ) -> datetime:
        """Get optimal posting time for platform.
        
        Args:
            platform: Target platform
            days_ahead: How many days in future
            
        Returns:
            Datetime for optimal posting
        """
        best_times = self.BEST_TIMES.get(platform, [])
        
        if not best_times:
            # Default to tomorrow 10am
            return datetime.now() + timedelta(days=days_ahead, hours=10)
        
        # Get first optimal time
        optimal = best_times[0]
        target_hour = optimal["hour"]
        
        # Calculate datetime
        target_date = datetime.now() + timedelta(days=days_ahead)
        target_date = target_date.replace(
            hour=target_hour,
            minute=0,
            second=0,
            microsecond=0
        )
        
        return target_date
    
    def preview_post(
        self,
        content: str,
        platform: Platform,
        hashtags: Optional[List[str]] = None
    ) -> dict:
        """Preview how post will look on platform.
        
        Args:
            content: Post content
            platform: Target platform
            hashtags: Optional hashtags
            
        Returns:
            Preview dict with formatted content and metadata
        """
        # Calculate character count of original content + hashtags
        preview_content = content
        if hashtags:
            hashtag_str = self.format_hashtags(hashtags, platform)
            preview_content += hashtag_str
        
        char_limit = self.CHAR_LIMITS[platform]
        original_char_count = len(preview_content)
        
        # Optimize if needed
        optimized = self.optimize_for_platform(content, platform)
        if hashtags:
            hashtag_str = self.format_hashtags(hashtags, platform)
            optimized += hashtag_str
        
        return {
            "platform": platform.value,
            "content": optimized,
            "character_count": original_char_count,
            "character_limit": char_limit,
            "within_limit": original_char_count <= char_limit,
            "optimal_time": self.get_optimal_time(platform).isoformat()
        }


if __name__ == "__main__":
    # Example usage
    publisher = SocialMediaPublisher()
    
    # Preview post
    preview = publisher.preview_post(
        content="Exciting news: New AI course launching next month! Learn how to build AI-native workflows that 10x your productivity. Early bird discount available.",
        platform=Platform.LINKEDIN,
        hashtags=["AIProductivity", "Superworker", "AILeadership"]
    )
    
    print("Preview:")
    print(f"Platform: {preview['platform']}")
    print(f"Content:\n{preview['content']}\n")
    print(f"Characters: {preview['character_count']}/{preview['character_limit']}")
    print(f"Optimal time: {preview['optimal_time']}")
