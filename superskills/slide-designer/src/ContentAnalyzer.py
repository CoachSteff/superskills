from dataclasses import dataclass
from typing import List, Optional
import re


@dataclass
class SlideChunk:
    content: str
    suggested_type: str
    key_points: List[str]
    heading: Optional[str] = None


def analyze_script(script: str, target_slides: int = 5) -> List[SlideChunk]:
    words = script.split()
    total_words = len(words)
    
    if total_words < 30:
        target_slides = 3
    elif total_words > 150:
        target_slides = 7
    else:
        target_slides = min(7, max(3, total_words // 20))
    
    sentences = re.split(r'[.!?]+', script)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    chunks = []
    words_per_slide = total_words // target_slides
    
    current_chunk = []
    current_word_count = 0
    
    for sentence in sentences:
        sentence_words = len(sentence.split())
        
        if current_word_count > 0 and current_word_count + sentence_words > words_per_slide * 1.3:
            chunk_text = ' '.join(current_chunk)
            chunks.append(chunk_text)
            current_chunk = [sentence]
            current_word_count = sentence_words
        else:
            current_chunk.append(sentence)
            current_word_count += sentence_words
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    slide_chunks = []
    for idx, chunk in enumerate(chunks[:7]):
        content_type = detect_content_type(chunk)
        
        if idx == 0:
            content_type = "title"
        
        key_points = extract_bullets(chunk, max_bullets=5)
        heading = extract_heading(chunk)
        
        slide_chunks.append(SlideChunk(
            content=chunk,
            suggested_type=content_type,
            key_points=key_points,
            heading=heading
        ))
    
    return slide_chunks


def analyze_markdown(markdown: str) -> List[SlideChunk]:
    lines = markdown.split('\n')
    slide_chunks = []
    current_heading = None
    current_subheading = None
    current_bullets = []
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('# '):
            if current_heading or current_bullets or current_content:
                slide_type = "title" if len(slide_chunks) == 0 else "content"
                content = '\n'.join(current_content) if current_content else ''
                
                slide_chunks.append(SlideChunk(
                    content=content,
                    suggested_type=slide_type,
                    key_points=current_bullets,
                    heading=current_heading or current_subheading
                ))
            
            current_heading = line[2:].strip()
            current_subheading = None
            current_bullets = []
            current_content = [line[2:].strip()]
        
        elif line.startswith('## '):
            current_subheading = line[3:].strip()
            current_content.append(line[3:].strip())
        
        elif line.startswith('- ') or line.startswith('* '):
            bullet = line[2:].strip()
            current_bullets.append(bullet)
            current_content.append(bullet)
        
        else:
            current_content.append(line)
    
    if current_heading or current_bullets or current_content:
        slide_type = "title" if len(slide_chunks) == 0 else "content"
        content = '\n'.join(current_content) if current_content else ''
        
        slide_chunks.append(SlideChunk(
            content=content,
            suggested_type=slide_type,
            key_points=current_bullets,
            heading=current_heading or current_subheading
        ))
    
    return slide_chunks[:7]


def extract_bullets(text: str, max_bullets: int = 5) -> List[str]:
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    bullets = []
    for sentence in sentences[:max_bullets]:
        words = sentence.split()
        
        if len(words) > 12:
            words = words[:12]
        
        bullet = ' '.join(words)
        bullet = re.sub(r'^(the|a|an)\s+', '', bullet, flags=re.IGNORECASE)
        bullet = re.sub(r'\s+(the|a|an)\s+', ' ', bullet, flags=re.IGNORECASE)
        
        if bullet and len(bullet) > 5:
            bullets.append(bullet)
    
    return bullets[:max_bullets]


def extract_heading(text: str) -> str:
    sentences = re.split(r'[.!?]+', text)
    if not sentences:
        return "Slide"
    
    first_sentence = sentences[0].strip()
    words = first_sentence.split()
    
    if len(words) > 8:
        heading = ' '.join(words[:8])
    else:
        heading = first_sentence
    
    if len(heading) > 50:
        heading = heading[:47] + "..."
    
    return heading


def detect_content_type(text: str) -> str:
    text_lower = text.lower().strip()
    
    if text.strip().endswith('?'):
        return "question"
    
    if '"' in text and ('—' in text or ' - ' in text):
        return "quote"
    
    if len(text.split()) < 8:
        return "title"
    
    if re.search(r'^\s*[-*•]\s', text, re.MULTILINE):
        return "content"
    
    if 'image' in text_lower or 'diagram' in text_lower or 'picture' in text_lower:
        return "image"
    
    return "content"
