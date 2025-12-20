"""
CLI command: discover - Help IDE AI understand skill capabilities
"""
import json
from typing import List, Dict, Tuple
from cli.core.skill_loader import SkillLoader


def discover_command(query: str = None, task: str = None, json_output: bool = False):
    """
    Discover skills based on query or task description.
    
    Args:
        query: Search query for skill capabilities
        task: Task description to find matching workflow
        json_output: Output in JSON format
    """
    if not query and not task:
        if json_output:
            print(json.dumps({
                'status': 'error',
                'error': 'Provide either --query or --task'
            }))
        else:
            print("Error: Provide either --query or --task")
        return 1
    
    loader = SkillLoader()
    skills = loader.discover_skills()
    
    if query:
        results = _search_skills(query, skills)
        
        if json_output:
            print(json.dumps({
                'status': 'success',
                'query': query,
                'results': results
            }, indent=2))
        else:
            print(f"Skills matching '{query}':\n")
            for result in results[:5]:
                print(f"  {result['name']:20} (score: {result['score']:.2f})")
                print(f"    {result['description']}")
                print(f"    Type: {result['type']}")
                if result.get('capabilities'):
                    print(f"    Capabilities: {', '.join(result['capabilities'][:3])}")
                print()
    
    elif task:
        workflow_suggestions = _suggest_workflow(task, skills)
        
        if json_output:
            print(json.dumps({
                'status': 'success',
                'task': task,
                'suggestions': workflow_suggestions
            }, indent=2))
        else:
            print(f"Workflow suggestions for: '{task}'\n")
            for suggestion in workflow_suggestions:
                print(f"  {suggestion['name']}")
                print(f"    Confidence: {suggestion['confidence']:.2f}")
                print(f"    Steps: {' → '.join(suggestion['steps'])}")
                print(f"    Use case: {suggestion['use_case']}")
                print()
    
    return 0


def _search_skills(query: str, skills: List) -> List[Dict]:
    """Search skills by query with enhanced relevance scoring."""
    query_lower = query.lower()
    results = []
    
    # Get query synonyms for better matching
    query_terms = _expand_query_terms(query_lower)
    
    for skill in skills:
        score = 0.0
        
        # Exact name match (highest priority)
        if query_lower == skill.name.lower():
            score += 15.0
        elif query_lower in skill.name.lower():
            score += 10.0
        
        # Get skill capabilities
        capabilities = _get_skill_capabilities(skill.name)
        
        # Exact capability tag match (high priority)
        for capability in capabilities:
            if query_lower == capability.lower():
                score += 12.0
            elif query_lower in capability.lower():
                score += 5.0
        
        # Synonym/related term matching
        for term in query_terms:
            for capability in capabilities:
                if term in capability.lower():
                    score += 7.0
            if term in skill.description.lower():
                score += 4.0
            if term in skill.name.lower():
                score += 6.0
        
        # Description keyword match
        if query_lower in skill.description.lower():
            score += 5.0
        
        # Multi-word query keyword matching
        keywords = _extract_keywords(query_lower)
        for keyword in keywords:
            if keyword in skill.description.lower():
                score += 2.0
            if keyword in skill.name.lower():
                score += 3.0
        
        if score > 0:
            results.append({
                'name': skill.name,
                'description': skill.description,
                'type': skill.skill_type,
                'score': score,
                'capabilities': capabilities,
                'has_profile': skill.has_profile
            })
    
    return sorted(results, key=lambda x: x['score'], reverse=True)


def _suggest_workflow(task: str, skills: List) -> List[Dict]:
    """Suggest workflows based on task description."""
    task_lower = task.lower()
    
    workflow_patterns = [
        {
            'name': 'content-creation',
            'keywords': ['write', 'article', 'blog', 'post', 'content', 'create'],
            'steps': ['researcher', 'strategist', 'author', 'editor'],
            'use_case': 'Research and write content from scratch'
        },
        {
            'name': 'podcast-generation',
            'keywords': ['podcast', 'audio', 'voice', 'narrate', 'voiceover'],
            'steps': ['copywriter', 'narrator'],
            'use_case': 'Create audio content from script'
        },
        {
            'name': 'training-material',
            'keywords': ['training', 'course', 'educational', 'transcribe', 'recording'],
            'steps': ['transcriber', 'author', 'editor'],
            'use_case': 'Transform recordings into training content'
        },
        {
            'name': 'client-engagement',
            'keywords': ['outreach', 'sales', 'lead', 'research', 'client', 'prospect'],
            'steps': ['scraper', 'researcher', 'copywriter', 'sales'],
            'use_case': 'Research and create personalized outreach'
        },
        {
            'name': 'custom-research-write',
            'keywords': ['analyze', 'research', 'investigate'],
            'steps': ['researcher', 'author'],
            'use_case': 'Research and summarize findings'
        },
        {
            'name': 'custom-edit-polish',
            'keywords': ['edit', 'improve', 'refine', 'polish', 'review'],
            'steps': ['editor', 'quality-control'],
            'use_case': 'Edit and improve existing content'
        },
        {
            'name': 'custom-design-content',
            'keywords': ['image', 'design', 'visual', 'graphic'],
            'steps': ['strategist', 'designer', 'copywriter'],
            'use_case': 'Create visual content with copy'
        }
    ]
    
    suggestions = []
    
    for pattern in workflow_patterns:
        confidence = 0.0
        
        for keyword in pattern['keywords']:
            if keyword in task_lower:
                confidence += 1.0
        
        if confidence > 0:
            suggestions.append({
                'name': pattern['name'],
                'confidence': min(confidence / len(pattern['keywords']), 1.0),
                'steps': pattern['steps'],
                'use_case': pattern['use_case']
            })
    
    return sorted(suggestions, key=lambda x: x['confidence'], reverse=True)


def _get_skill_capabilities(skill_name: str) -> List[str]:
    """Get capabilities for a skill with expanded terms."""
    capabilities = {
        # Core content creation
        'author': ['writing', 'ghostwriting', 'content-creation', 'brand-voice', 'articles', 'blog', 'documentation'],
        'copywriter': ['marketing-copy', 'sales-messaging', 'persuasive-writing', 'advertising', 'promotional'],
        'editor': ['editing', 'proofreading', 'quality-control', 'refinement', 'polish', 'review'],
        'strategist': ['strategy', 'planning', 'frameworks', 'analysis', 'positioning', 'roadmap'],
        
        # Voice and audio (narrator family)
        'narrator': ['voice-generation', 'text-to-speech', 'audio', 'narration', 'voiceover', 'tts', 'speech'],
        'narrator-podcast': ['podcast', 'voice', 'audio', 'narration', 'conversational', 'tts', 'speech'],
        'narrator-meditation': ['meditation', 'voice', 'audio', 'calm', 'mindfulness', 'tts', 'relaxation'],
        'narrator-educational': ['educational', 'voice', 'audio', 'training', 'learning', 'tts', 'instruction'],
        'narrator-marketing': ['marketing', 'voice', 'audio', 'promotional', 'advertising', 'tts', 'commercial'],
        'narrator-social': ['social-media', 'voice', 'audio', 'short-form', 'viral', 'tts', 'engaging'],
        
        # Audio processing
        'transcriber': ['transcription', 'speech-to-text', 'audio-processing', 'stt', 'audio-to-text'],
        
        # Research and data
        'researcher': ['research', 'analysis', 'web-search', 'data-gathering', 'investigation', 'sources'],
        'scraper': ['web-scraping', 'data-extraction', 'content-harvesting', 'crawling', 'automation'],
        
        # Visual content
        'designer': ['image-generation', 'ai-art', 'visual-design', 'brand-assets', 'graphics', 'visuals', 'illustration'],
        
        # Marketing and social
        'marketer': ['social-media', 'scheduling', 'multi-platform-posting', 'distribution', 'publishing'],
        'emailcampaigner': ['email', 'campaigns', 'newsletters', 'sendgrid', 'email-marketing', 'outreach'],
        
        # Coaching and consulting
        'coach': ['coaching', 'session-design', 'client-guidance', 'mentoring', 'facilitation'],
        'product': ['product-management', 'roadmap', 'features', 'prioritization', 'product-strategy'],
        'sales': ['sales', 'outreach', 'prospecting', 'business-development', 'lead-generation'],
        
        # Technical
        'developer': ['code-generation', 'debugging', 'software-development', 'programming', 'coding'],
        'translator': ['translation', 'localization', 'multilingual', 'language', 'internationalization'],
        
        # Business operations
        'risk-manager': ['risk-assessment', 'compliance', 'mitigation', 'risk-analysis', 'governance'],
        'compliance-manager': ['compliance', 'regulations', 'audit', 'governance', 'policy'],
        'legal': ['legal', 'contracts', 'agreements', 'legal-review', 'terms'],
        'process-engineer': ['process-improvement', 'optimization', 'lean', 'six-sigma', 'efficiency'],
        
        # Documentation and knowledge
        'knowledgebase': ['documentation', 'knowledge-management', 'wiki', 'information-architecture', 'kb'],
        'coursepackager': ['course-creation', 'pdf', 'training-materials', 'educational-content', 'learning'],
        'presenter': ['presentations', 'slides', 'powerpoint', 'keynote', 'slide-decks', 'ppt'],
        
        # Media production
        'videoeditor': ['video-editing', 'ffmpeg', 'video-processing', 'multimedia', 'video-production'],
    }
    
    return capabilities.get(skill_name, [])


def _extract_keywords(query: str) -> List[str]:
    """Extract meaningful keywords from query."""
    stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been'}
    
    words = query.lower().split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    return keywords


def _expand_query_terms(query: str) -> List[str]:
    """Expand query with synonyms and related terms for better matching."""
    synonyms = {
        'voice': ['audio', 'speech', 'tts', 'narration', 'voiceover', 'spoken'],
        'audio': ['voice', 'sound', 'speech', 'tts', 'narration'],
        'podcast': ['audio', 'voice', 'narration', 'voiceover', 'spoken'],
        'write': ['writing', 'content', 'author', 'compose', 'create'],
        'writing': ['write', 'content', 'author', 'compose', 'create'],
        'image': ['visual', 'graphic', 'picture', 'illustration', 'design'],
        'visual': ['image', 'graphic', 'picture', 'illustration', 'design'],
        'design': ['visual', 'image', 'graphic', 'create', 'layout'],
        'research': ['investigate', 'analyze', 'study', 'explore', 'search'],
        'edit': ['editing', 'review', 'polish', 'refine', 'improve'],
        'video': ['multimedia', 'film', 'recording', 'footage', 'media'],
        'translate': ['translation', 'localize', 'language', 'multilingual'],
        'code': ['coding', 'programming', 'development', 'software', 'script'],
        'email': ['mail', 'newsletter', 'campaign', 'message', 'outreach'],
        'presentation': ['slides', 'powerpoint', 'keynote', 'deck', 'ppt'],
        'course': ['training', 'educational', 'learning', 'tutorial', 'lesson'],
        'transcribe': ['transcription', 'speech-to-text', 'stt', 'audio-to-text'],
    }
    
    # Start with the original query terms
    expanded = set(_extract_keywords(query))
    
    # Add synonyms for each term
    for term in list(expanded):
        if term in synonyms:
            expanded.update(synonyms[term])
    
    return list(expanded)

