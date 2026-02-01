"""Video Recorder SuperSkill - Main exports."""

from .VideoRecorder import VideoRecorder, VideoResult
from .SlideRenderer import SlideRenderer
from .AudioGenerator import AudioGenerator
from .TimingSync import TimingSync, TimedSlide
from .VideoEncoder import VideoEncoder

__all__ = [
    'VideoRecorder',
    'VideoResult',
    'SlideRenderer',
    'AudioGenerator',
    'TimingSync',
    'TimedSlide',
    'VideoEncoder',
]
