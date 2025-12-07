"""
Integration test - verify profile loading in actual code
(Uses project venv: /Users/steffvanhaverbeke/Development/01_projects/superskills/.venv)
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")

# Add superskills to path so we can import narrator.src
superskills_dir = Path(__file__).parent.parent
if str(superskills_dir) not in sys.path:
    sys.path.insert(0, str(superskills_dir))

print("="*60)
print("INTEGRATION TEST - Voice Profile Loading")
print("="*60)

# Test 1: VoiceConfig standalone
print("\n1. Testing VoiceConfig module...")
try:
    from narrator.src.VoiceConfig import VoiceConfig
    vc = VoiceConfig()
    profiles = vc.get_available_profiles()
    print(f"   ✓ VoiceConfig loaded")
    print(f"   ✓ Available profiles: {profiles}")
    
    for profile_name in profiles:
        profile = vc.get_profile(profile_name)
        settings = vc.get_voice_settings(profile_name)
        print(f"   ✓ {profile_name}: {profile['voice_name']} (speed={settings['speed']})")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Check if API key is set
print("\n2. Checking environment...")
api_key = os.getenv("ELEVENLABS_API_KEY")
if api_key:
    print(f"   ✓ ELEVENLABS_API_KEY is set ({len(api_key)} chars)")
else:
    print("   ⚠ ELEVENLABS_API_KEY not set - cannot test actual generation")
    print("   💡 Set it in .env file to test voice generation")

# Test 3: Initialize generators (requires API key)
print("\n3. Testing generator initialization...")
try:
    from narrator.src.Voiceover import VoiceoverGenerator
    from narrator.src.Podcast import PodcastGenerator, PodcastSegment
    
    # Test VoiceoverGenerator
    gen = VoiceoverGenerator(profile_type="narration")
    print(f"   ✓ VoiceoverGenerator initialized with 'narration' profile")
    print(f"     - Voice: {gen.profile['voice_name']}")
    print(f"     - Model: {gen.profile['model']}")
    
    gen_podcast = VoiceoverGenerator(profile_type="podcast")
    print(f"   ✓ VoiceoverGenerator initialized with 'podcast' profile")
    print(f"     - Voice: {gen_podcast.profile['voice_name']}")
    
    # Test PodcastGenerator
    pod_gen = PodcastGenerator(profile_type="meditation")
    print(f"   ✓ PodcastGenerator initialized with 'meditation' profile")
    
    # Test content type mapping
    print("\n4. Testing content type mapping...")
    mapping = VoiceoverGenerator.CONTENT_TYPE_TO_PROFILE
    for content_type, profile in mapping.items():
        print(f"   ✓ {content_type:12} → {profile}")
    
except ValueError as e:
    if "ELEVENLABS_API_KEY" in str(e):
        print(f"   ⚠ Cannot initialize generators: {e}")
        print("   💡 This is expected if API key is not set")
    else:
        print(f"   ❌ Error: {e}")
        raise
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    print("   💡 Run: pip install elevenlabs pydub python-dotenv")
    sys.exit(1)

print("\n" + "="*60)
print("✓ INTEGRATION TEST COMPLETE!")
print("="*60)

if not api_key:
    print("\n⚠ To test actual voice generation:")
    print("  1. Add ELEVENLABS_API_KEY to your .env file")
    print("  2. Run a generation test")
else:
    print("\n✓ Ready for voice generation!")
    print("  Example:")
    print("    generator = VoiceoverGenerator(profile_type='podcast')")
    print("    result = generator.generate(script='Hello world', content_type='podcast')")
