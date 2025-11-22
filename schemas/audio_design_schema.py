from typing import List, Optional
from pydantic import BaseModel, Field

class MusicStyle(BaseModel):
    genre: str = Field(description="Primary genre of the music (e.g. Orchestral, Electronic)")
    mood: str = Field(description="Target mood (e.g. Epic, Dark)")
    instrumentation: List[str] = Field(description="Key instruments used")
    dynamic_system: str = Field(description="How music changes with gameplay")

class SFXItem(BaseModel):
    name: str
    type: str
    variations: Optional[int] = 1

class SFXCatalog(BaseModel):
    ui_sounds: List[SFXItem]
    combat_sfx: List[SFXItem]
    environmental_sfx: List[SFXItem]

class AudioDesignSchema(BaseModel):
    music_style: MusicStyle
    sfx_catalog: SFXCatalog
    voice_over_plan: str = Field(description="High level VO strategy")
    audio_middleware: str = Field(description="Recommended middleware (Wwise/FMOD)")
    technical_specs: str = Field(description="Sample rates, memory budget, etc.")
