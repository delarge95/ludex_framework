"""
Agent Synergy System - Core Infrastructure

This module provides extraction and injection utilities for cross-agent data flow.
It enables agents to share outputs and influence each other's decisions.
"""

from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger(__name__)

# ============================================================================
# EXTRACTION FUNCTIONS (Agent Output → Structured Data)
# ============================================================================

def extract_world_physics_constants(world_lore: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract physics-relevant constants from WorldBuilder output.
    
    Args:
        world_lore: Output from WorldBuilder agent
        
    Returns:
        Dict with gravity, atmosphere, terrain properties
    """
    if not world_lore:
        return {"gravity": "Earth-like", "atmosphere": "Standard", "terrain": "Varied"}
    
    constants = {}
    
    # Extract gravity from world description
    description = world_lore.get("world_description", "").lower()
    if "low gravity" in description or "moon" in description or "space" in description:
        constants["gravity"] = "Low (Moon-like)"
    elif "high gravity" in description or "heavy" in description:
        constants["gravity"] = "High (Jupiter-like)"
    else:
        constants["gravity"] = "Earth-like"
    
    # Extract atmosphere
    if "dense fog" in description or "thick atmosphere" in description:
        constants["atmosphere"] = "Dense"
    elif "thin air" in description or "high altitude" in description:
        constants["atmosphere"] = "Thin"
    else:
        constants["atmosphere"] = "Standard"
    
    # Extract terrain
    geography = world_lore.get("geography", {})
    terrain_types = geography.get("terrain_types", [])
    if terrain_types:
        constants["terrain"] = ", ".join(terrain_types[:3])
    else:
        constants["terrain"] = "Varied"
    
    logger.info("extracted_world_physics_constants", constants=constants)
    return constants


def extract_art_performance_budgets(art_style_guide: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract performance budgets from ArtDirector output.
    
    Args:
        art_style_guide: Output from ArtDirector agent
        
    Returns:
        Dict with poly count, texture resolution targets
    """
    if not art_style_guide:
        return {"target_poly_count": "50k per character", "texture_resolution": "2K"}
    
    budgets = {}
    
    art_style = art_style_guide.get("art_style", "").lower()
    visual_fidelity = art_style_guide.get("visual_fidelity", "medium").lower()
    
    # Determine poly count based on art style
    if "pixel art" in art_style or "low poly" in art_style:
        budgets["target_poly_count"] = "5k-10k per character"
    elif "hyper-realistic" in art_style or "aaa" in art_style or visual_fidelity == "high":
        budgets["target_poly_count"] = "100k-150k per character"
    elif "stylized" in art_style or visual_fidelity == "medium":
        budgets["target_poly_count"] = "30k-50k per character"
    else:
        budgets["target_poly_count"] = "50k per character"
    
    # Determine texture resolution
    if "pixel art" in art_style:
        budgets["texture_resolution"] = "512x512"
    elif "hyper-realistic" in art_style or visual_fidelity == "high":
        budgets["texture_resolution"] = "4K"
    else:
        budgets["texture_resolution"] = "2K"
    
    logger.info("extracted_art_performance_budgets", budgets=budgets)
    return budgets


def extract_mechanics_audio_triggers(mechanics: List[Dict[str, Any]]) -> List[str]:
    """
    Extract audio trigger events from MechanicsDesigner output.
    
    Args:
        mechanics: List of mechanics from MechanicsDesigner
        
    Returns:
        List of event names that need audio
    """
    if not mechanics:
        return ["Jump", "Attack", "Take Damage", "Collect Item"]
    
    triggers = set()
    
    for mechanic in mechanics:
        name = mechanic.get("name", "")
        mechanic_type = mechanic.get("type", "").lower()
        
        # Add the mechanic itself as a trigger
        if name:
            triggers.add(name)
        
        # Add common sub-events based on mechanic type
        if mechanic_type == "combat":
            triggers.update(["Attack", "Parry", "Dodge", "Take Damage", "Critical Hit"])
        elif mechanic_type == "movement":
            triggers.update(["Jump", "Land", "Sprint", "Slide"])
        elif mechanic_type == "interaction":
            triggers.update(["Collect Item", "Open Door", "Activate Switch"])
    
    trigger_list = sorted(list(triggers))
    logger.info("extracted_mechanics_audio_triggers", count=len(trigger_list), triggers=trigger_list[:10])
    return trigger_list


def extract_narrative_level_beats(narrative_structure: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract story beats for level pacing from NarrativeArchitect.
    
    Args:
        narrative_structure: Output from NarrativeArchitect
        
    Returns:
        List of story beats with timing and intensity
    """
    if not narrative_structure:
        return [{"beat": "Introduction", "intensity": "low", "timing": "early"}]
    
    beats = []
    story_beats = narrative_structure.get("story_beats", [])
    
    for beat in story_beats:
        beats.append({
            "beat": beat.get("name", "Unknown"),
            "intensity": beat.get("intensity", "medium"),
            "timing": beat.get("timing", "mid")
        })
    
    logger.info("extracted_narrative_level_beats", count=len(beats))
    return beats


def extract_mechanics_animation_catalog(mechanics: List[Dict[str, Any]]) -> List[str]:
    """
    Extract required animations from mechanics.
    
    Args:
        mechanics: List of mechanics
        
    Returns:
        List of animation names needed
    """
    if not mechanics:
        return ["Idle", "Walk", "Run", "Jump"]
    
    animations = set(["Idle", "Walk", "Run"])  # Always include basics
    
    for mechanic in mechanics:
        name = mechanic.get("name", "")
        mechanic_type = mechanic.get("type", "").lower()
        
        if mechanic_type == "combat":
            animations.update(["Attack", "Block", "Dodge", "Hit Reaction", "Death"])
        elif mechanic_type == "movement":
            animations.update(["Jump", "Land", "Climb", "Slide"])
        
        # Add mechanic-specific animation
        if name:
            animations.add(f"{name} Animation")
    
    animation_list = sorted(list(animations))
    logger.info("extracted_mechanics_animation_catalog", count=len(animation_list))
    return animation_list


def extract_narrative_world_themes(narrative_structure: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract story themes to inform WorldBuilder.
    
    Args:
        narrative_structure: Output from NarrativeArchitect
        
    Returns:
        Dict with themes, tone, key story elements
    """
    if not narrative_structure:
        return {"themes": ["Adventure"], "tone": "Neutral", "key_elements": []}
    
    return {
        "themes": narrative_structure.get("themes", ["Adventure"]),
        "tone": narrative_structure.get("tone", "Neutral"),
        "key_elements": narrative_structure.get("key_story_elements", []),
        "setting_requirements": narrative_structure.get("setting", "Fantasy")
    }


def extract_world_environment_biomes(world_lore: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract biomes for EnvironmentArtist from WorldBuilder.
    
    Args:
        world_lore: Output from WorldBuilder
        
    Returns:
        List of biomes with visual characteristics
    """
    if not world_lore:
        return [{"name": "Forest", "mood": "Peaceful", "colors": "Green, Brown"}]
    
    geography = world_lore.get("geography", {})
    biomes = geography.get("biomes", [])
    
    if not biomes:
        # Fallback: extract from terrain types
        terrain_types = geography.get("terrain_types", ["Forest"])
        biomes = [{"name": t, "mood": "Unknown", "colors": "Unknown"} for t in terrain_types]
    
    logger.info("extracted_world_environment_biomes", count=len(biomes))
    return biomes


def extract_art_character_style(art_style_guide: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract character art requirements from ArtDirector.
    
    Args:
        art_style_guide: Output from ArtDirector
        
    Returns:
        Dict with art style, color palette, proportions
    """
    if not art_style_guide:
        return {"art_style": "Stylized", "color_palette": "Vibrant", "proportions": "Realistic"}
    
    return {
        "art_style": art_style_guide.get("art_style", "Stylized"),
        "color_palette": art_style_guide.get("color_palette", "Vibrant"),
        "proportions": art_style_guide.get("character_proportions", "Realistic"),
        "visual_pillars": art_style_guide.get("visual_pillars", [])
    }


def extract_character_visual_specs(character_design: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract character descriptions for CharacterArtist.
    
    Args:
        character_design: Output from CharacterDesigner
        
    Returns:
        List of characters with visual requirements
    """
    if not character_design:
        return [{"name": "Protagonist", "archetype": "Hero", "traits": []}]
    
    characters = character_design.get("characters", [])
    
    visual_specs = []
    for char in characters:
        visual_specs.append({
            "name": char.get("name", "Unknown"),
            "archetype": char.get("archetype", "Generic"),
            "personality": char.get("personality", ""),
            "visual_traits": char.get("visual_description", "")
        })
    
    logger.info("extracted_character_visual_specs", count=len(visual_specs))
    return visual_specs


def extract_ui_camera_requirements(ui_design: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract HUD/UI requirements that affect camera framing.
    
    Args:
        ui_design: Output from UIUXDesigner
        
    Returns:
        Dict with HUD layout, safe zones, camera constraints
    """
    if not ui_design:
        return {"hud_layout": "Minimalist", "safe_zones": "Standard", "constraints": []}
    
    return {
        "hud_layout": ui_design.get("hud_layout", "Minimalist"),
        "safe_zones": ui_design.get("safe_zones", "Standard"),
        "screen_space_usage": ui_design.get("screen_space_percentage", "15%"),
        "constraints": ui_design.get("camera_constraints", [])
    }


def extract_system_tech_stack(technical_stack: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract tech stack for NetworkArchitect and PerformanceAnalyst.
    
    Args:
        technical_stack: Output from SystemDesigner
        
    Returns:
        Dict with engine, platforms, architecture
    """
    if not technical_stack:
        return {"engine": "Unity", "platforms": ["PC"], "architecture": "Client-Server"}
    
    return {
        "engine": technical_stack.get("engine", "Unity"),
        "platforms": technical_stack.get("target_platforms", ["PC"]),
        "architecture": technical_stack.get("architecture", "Client-Server"),
        "middleware": technical_stack.get("middleware", [])
    }


def extract_mechanics_system_requirements(mechanics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract technical requirements from mechanics for SystemDesigner.
    
    Args:
        mechanics: List of mechanics
        
    Returns:
        Dict with required engine features and complexity
    """
    if not mechanics:
        return {"features": ["Physics"], "complexity": "Medium", "multiplayer": False}
    
    features = set()
    multiplayer_needed = False
    max_complexity = "Low"
    
    for mechanic in mechanics:
        mechanic_type = mechanic.get("type", "").lower()
        
        if "combat" in mechanic_type:
            features.add("Physics")
            features.add("Animation System")
        if "multiplayer" in mechanic_type or "coop" in mechanic_type:
            multiplayer_needed = True
            features.add("Networking")
        if "procedural" in mechanic.get("name", "").lower():
            features.add("Procedural Generation")
        
        # Track complexity
        complexity = mechanic.get("complexity", "medium")
        if complexity == "high" or complexity == "very_high":
            max_complexity = "High"
        elif complexity == "medium" and max_complexity == "Low":
            max_complexity = "Medium"
    
    return {
        "features": sorted(list(features)) if features else ["Basic Gameplay"],
        "complexity": max_complexity,
        "multiplayer": multiplayer_needed
    }


# ============================================================================
# INJECTION UTILITIES (Structured Data → Agent Input)
# ============================================================================

def inject_synergy_context(
    base_prompt: str,
    synergy_data: Dict[str, Any],
    synergy_type: str
) -> str:
    """
    Inject synergy data into an agent's system prompt.
    
    Args:
        base_prompt: Original system prompt
        synergy_data: Data from upstream agent
        synergy_type: Type of synergy (e.g., "world_physics", "art_performance")
        
    Returns:
        Enhanced prompt with synergy context
    """
    if not synergy_data:
        return base_prompt
    
    synergy_prompts = {
       "world_physics": f"""
**World Physics Context (from WorldBuilder)**:
- Gravity: {synergy_data.get('gravity', 'Unknown')}
- Atmosphere: {synergy_data.get('atmosphere', 'Unknown')}
- Terrain: {synergy_data.get('terrain', 'Unknown')}

Design physics systems that reflect these world properties.
""",
        "art_performance": f"""
**Performance Budgets (from ArtDirector)**:
- Target Poly Count: {synergy_data.get('target_poly_count', 'Unknown')}
- Texture Resolution: {synergy_data.get('texture_resolution', 'Unknown')}

Optimize performance recommendations to match these art fidelity targets.
""",
        "mechanics_audio": f"""
**Gameplay Events Requiring Audio (from MechanicsDesigner)**:
{', '.join(synergy_data.get('triggers', []))}

Design dynamic audio systems that respond to these gameplay events.
""",
        "narrative_level": f"""
**Story Beats for Level Pacing (from NarrativeArchitect)**:
{chr(10).join([f"- {beat['beat']} ({beat['intensity']} intensity, {beat['timing']} game)" for beat in synergy_data.get('beats', [])])}

Design levels that align with these narrative beats.
""",
        "mechanics_animation": f"""
**Required Animations (from MechanicsDesigner)**:
{', '.join(synergy_data.get('animations', []))}

Create an animation catalog that supports these mechanics.
""",
        "narrative_world": f"""
**Story Themes (from NarrativeArchitect)**:
- Themes: {', '.join(synergy_data.get('themes', []))}
- Tone: {synergy_data.get('tone', 'Unknown')}
- Setting: {synergy_data.get('setting_requirements', 'Unknown')}

Build a world that supports these narrative elements.
""",
        "world_environment": f"""
**World Biomes (from WorldBuilder)**:
{chr(10).join([f"- {biome.get('name', 'Unknown')}: {biome.get('mood', '')} ({biome.get('colors', '')})" for biome in synergy_data.get('biomes', [])])}

Design environments that match these world specifications.
""",
        "art_character": f"""
**Art Style (from ArtDirector)**:
- Style: {synergy_data.get('art_style', 'Unknown')}
- Color Palette: {synergy_data.get('color_palette', 'Unknown')}
- Proportions: {synergy_data.get('proportions', 'Unknown')}

Design characters that fit this visual direction.
""",
        "character_art": f"""
**Character Specifications (from CharacterDesigner)**:
{chr(10).join([f"- {char.get('name', 'Unknown')}: {char.get('archetype', '')} - {char.get('visual_traits', '')[:50]}" for char in synergy_data.get('characters', [])])}

Create visual designs for these characters.
""",
        "ui_camera": f"""
**HUD/UI Requirements (from UIUXDesigner)**:
- HUD Layout: {synergy_data.get('hud_layout', 'Unknown')}
- Screen Space Used: {synergy_data.get('screen_space_usage', 'Unknown')}
- Safe Zones: {synergy_data.get('safe_zones', 'Unknown')}

Design camera system that accommodates UI layout.
""",
        "system_network": f"""
**Tech Stack (from SystemDesigner)**:
- Engine: {synergy_data.get('engine', 'Unknown')}
- Platforms: {', '.join(synergy_data.get('platforms', []))}
- Architecture: {synergy_data.get('architecture', 'Unknown')}

Design network architecture compatible with this tech stack.
""",
        "mechanics_system": f"""
**Mechanics Requirements (from MechanicsDesigner)**:
- Required Features: {', '.join(synergy_data.get('features', []))}
- Complexity: {synergy_data.get('complexity', 'Unknown')}
- Multiplayer: {'Yes' if synergy_data.get('multiplayer') else 'No'}

Select tech stack that supports these gameplay needs.
"""
    }
    
    synergy_context = synergy_prompts.get(synergy_type, "")
    
    if synergy_context:
        enhanced_prompt = f"{base_prompt}\n\n{synergy_context}"
        logger.info("injected_synergy_context", synergy_type=synergy_type)
        return enhanced_prompt
    
    return base_prompt



# ============================================================================
# SYNERGY REGISTRY (Mapping of all connections)
# ============================================================================

SYNERGY_REGISTRY = {
    "forward_dependencies": [
        {"from": "MarketAnalyst", "to": "MechanicsDesigner", "data": "target_audience"},
        {"from": "MechanicsDesigner", "to": "SystemDesigner", "data": "core_mechanics"},
        {"from": "MechanicsDesigner", "to": "AnimationDirector", "data": "movement_mechanics"},
        {"from": "MechanicsDesigner", "to": "AudioDirector", "data": "gameplay_events"},
        {"from": "NarrativeArchitect", "to": "WorldBuilder", "data": "story_themes"},
        {"from": "NarrativeArchitect", "to": "LevelDesigner", "data": "story_beats"},
        {"from": "WorldBuilder", "to": "EnvironmentArtist", "data": "biomes"},
        {"from": "WorldBuilder", "to": "PhysicsEngineer", "data": "physics_constants"},
        {"from": "ArtDirector", "to": "CharacterArtist", "data": "art_style"},
        {"from": "ArtDirector", "to": "EnvironmentArtist", "data": "visual_mood"},
        {"from": "ArtDirector", "to": "PerformanceAnalyst", "data": "performance_budgets"},
        {"from": "CharacterDesigner", "to": "CharacterArtist", "data": "character_descriptions"},
        {"from": "UIUXDesigner", "to": "CameraDesigner", "data": "hud_requirements"},
        {"from": "SystemDesigner", "to": "PerformanceAnalyst", "data": "engine_choice"},
        {"from": "SystemDesigner", "to": "NetworkArchitect", "data": "tech_stack"},
    ],
    "feedback_loops": [
        {"agents": ["MechanicsDesigner", "TechnicalFeasibilityValidator"], "type": "feasibility_check"},
        {"agents": ["NarrativeArchitect", "LudonarrativeHarmonizer"], "type": "story_gameplay_alignment"},
        {"agents": ["MechanicsDesigner", "LudonarrativeHarmonizer"], "type": "mechanics_narrative_loop"},
        {"agents": ["ArtDirector", "PerformanceAnalyst"], "type": "visual_performance_balance"},
        {"agents": ["MechanicsDesigner", "LevelDesigner"], "type": "mechanics_level_loop"},
        {"agents": ["AudioDirector", "MechanicsDesigner"], "type": "audio_gameplay_loop"},
    ]
}
