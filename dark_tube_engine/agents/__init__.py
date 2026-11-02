"""
DARK TUBE ENGINE — Agentes Especializados
9 agentes comunicando via contratos JSON com DARK MANAGER
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
from .image_engine import ImageEngineAgent
from .video_generator import VideoGeneratorAgent
from .cinematic_director import CinematicDirectorAgent
from .video_editor_pro import VideoEditorProAgent
from .motion_graphics import MotionGraphicsAgent
from .audio_master import AudioMasterAgent
from .visual_consistency import VisualConsistencyAgent
from .asset_manager import AssetManagerAgent
from .creative_qa import CreativeQAAgent
from .dark_manager import DarkManager

__all__ = [
    "ImageEngineAgent", "VideoGeneratorAgent", "CinematicDirectorAgent",
    "VideoEditorProAgent", "MotionGraphicsAgent", "AudioMasterAgent",
    "VisualConsistencyAgent", "AssetManagerAgent", "CreativeQAAgent",
    "DarkManager"
]
