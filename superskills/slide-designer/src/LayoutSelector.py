from typing import List, Optional
import re


def select_layout(
    slide_chunk: 'SlideChunk',
    previous_layouts: List[str],
    position: str
) -> str:
    if position == "first":
        return "title"
    
    if position == "last":
        if slide_chunk.suggested_type == "question":
            return "question"
        return slide_chunk.suggested_type if slide_chunk.suggested_type == "title" else "content"
    
    suggested = slide_chunk.suggested_type
    
    if len(previous_layouts) >= 2:
        if previous_layouts[-1] == previous_layouts[-2] == suggested:
            if suggested == "content":
                return "question"
            elif suggested == "question":
                return "content"
    
    if suggested == "question" and previous_layouts and previous_layouts[-1] == "question":
        return "content"
    
    if suggested == "title" and previous_layouts and previous_layouts[-1] == "title":
        return "content"
    
    framework = detect_framework(slide_chunk.content)
    if framework:
        return "content"
    
    return suggested


def detect_framework(text: str) -> Optional[str]:
    text_upper = text.upper()
    
    frameworks = [
        'CRAFT',
        'CODE',
        'PARA',
        '4D',
        'SMART',
        'SWOT',
        'OKR',
        'GROW'
    ]
    
    for framework in frameworks:
        if framework in text_upper:
            return framework
    
    return None


def enforce_variety(layouts: List[str]) -> List[str]:
    if len(layouts) < 2:
        return layouts
    
    adjusted = layouts.copy()
    
    for i in range(1, len(adjusted)):
        if adjusted[i] == "question" and adjusted[i-1] == "question":
            adjusted[i] = "content"
        
        elif adjusted[i] == "title" and adjusted[i-1] == "title":
            adjusted[i] = "content"
    
    for i in range(2, len(adjusted)):
        if adjusted[i] == adjusted[i-1] == adjusted[i-2]:
            if adjusted[i] == "content":
                adjusted[i] = "question"
            elif adjusted[i] == "question":
                adjusted[i] = "content"
            else:
                adjusted[i] = "content"
    
    return adjusted
