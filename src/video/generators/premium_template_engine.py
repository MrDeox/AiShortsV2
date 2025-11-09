"""
Engine de Templates Premium para Geração de Vídeos Profissionais

Sistema avançado de geração de templates visuais profissionais para maximização
de engajamento e monetização em diferentes plataformas.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import random
from datetime import datetime

from .visual_templates import (
    VisualTemplate, TextOverlay, TemplateType, TextStyle,
    VisualTemplateGenerator, template_generator
)

class Platform(Enum):
    """Plataformas suportadas."""
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM_REELS = "instagram_reels"
    FACEBOOK_REELS = "facebook_reels"

class MonetizationCategory(Enum):
    """Categorias de monetização."""
    TIKKOK_ENGAGING = "tikkok_engaging"
    SHORTS_EDUCATIONAL = "shorts_educational"
    REELS_PREMIUM = "reels_premium"

class EngagementElement(Enum):
    """Elementos de engajamento."""
    ARROW = "arrow"
    HIGHLIGHT = "highlight"
    PULSE = "pulse"
    CHECKMARK = "checkmark"
    FIRE = "fire"
    HEART = "heart"
    STAR = "star"

@dataclass
class BrandingElement:
    """Elemento de branding."""
    type: str  # "logo", "watermark", "badge"
    position: str  # "top_left", "top_right", "bottom_left", "bottom_right", "center"
    opacity: float = 0.8
    size: str = "medium"  # "small", "medium", "large"
    animation: str = "none"
    custom_path: Optional[str] = None

@dataclass
class PremiumStyle:
    """Configuração de estilo premium."""
    primary_color: str
    secondary_color: str
    accent_color: str
    text_style: TextStyle
    background_style: str
    animation_speed: str = "medium"  # "slow", "medium", "fast"
    transition_style: str = "smooth"

@dataclass
class PlatformSpecs:
    """Especificações por plataforma."""
    aspect_ratio: str
    resolution: str
    max_duration: float
    text_size_multiplier: float = 1.0
    padding_percent: float = 0.05

class PremiumTemplateEngine:
    """Engine para geração de templates premium profissionais."""
    
    def __init__(self):
        self.base_generator = template_generator
        self.platform_specs = self._initialize_platform_specs()
        self.premium_styles = self._initialize_premium_styles()
        self.engagement_library = self._initialize_engagement_library()
        self.branding_elements = self._initialize_branding_library()
        
    def _initialize_platform_specs(self) -> Dict[Platform, PlatformSpecs]:
        """Inicializa especificações por plataforma."""
        return {
            Platform.TIKTOK: PlatformSpecs(
                aspect_ratio="9:16",
                resolution="1080x1920",
                max_duration=60.0,
                text_size_multiplier=1.1,
                padding_percent=0.08
            ),
            Platform.YOUTUBE_SHORTS: PlatformSpecs(
                aspect_ratio="9:16", 
                resolution="1080x1920",
                max_duration=60.0,
                text_size_multiplier=1.0,
                padding_percent=0.06
            ),
            Platform.INSTAGRAM_REELS: PlatformSpecs(
                aspect_ratio="9:16",
                resolution="1080x1920", 
                max_duration=90.0,
                text_size_multiplier=1.05,
                padding_percent=0.07
            ),
            Platform.FACEBOOK_REELS: PlatformSpecs(
                aspect_ratio="9:16",
                resolution="1080x1920",
                max_duration=90.0,
                text_size_multiplier=1.0,
                padding_percent=0.06
            )
        }
    
    def _initialize_premium_styles(self) -> Dict[MonetizationCategory, PremiumStyle]:
        """Inicializa estilos premium por categoria de monetização."""
        return {
            MonetizationCategory.TIKKOK_ENGAGING: PremiumStyle(
                primary_color="#ff0050",
                secondary_color="#ffffff", 
                accent_color="#00f2ea",
                text_style=TextStyle.MONTSERRAT_BOLD,
                background_style="gradient_dynamic",
                animation_speed="fast",
                transition_style="energetic"
            ),
            MonetizationCategory.SHORTS_EDUCATIONAL: PremiumStyle(
                primary_color="#1a73e8",
                secondary_color="#ffffff",
                accent_color="#34a853", 
                text_style=TextStyle.OPEN_SANS_SEMI_BOLD,
                background_style="clean_minimal",
                animation_speed="medium",
                transition_style="educational"
            ),
            MonetizationCategory.REELS_PREMIUM: PremiumStyle(
                primary_color="#8338ec",
                secondary_color="#ffffff",
                accent_color="#ff006e",
                text_style=TextStyle.POPPINS_SEMI_BOLD,
                background_style="aesthetic_gradient", 
                animation_speed="smooth",
                transition_style="premium"
            )
        }
    
    def _initialize_engagement_library(self) -> Dict[EngagementElement, Dict]:
        """Inicializa biblioteca de elementos de engajamento."""
        return {
            EngagementElement.ARROW: {
                "style": "pointer_arrow",
                "color": "#ffffff",
                "size": "medium",
                "animation": "slide_in"
            },
            EngagementElement.HIGHLIGHT: {
                "style": "glow_highlight", 
                "color": "#ffff00",
                "size": "large",
                "animation": "pulse"
            },
            EngagementElement.PULSE: {
                "style": "radial_pulse",
                "color": "#ff6b6b", 
                "size": "large",
                "animation": "expand"
            },
            EngagementElement.CHECKMARK: {
                "style": "success_check",
                "color": "#4caf50",
                "size": "medium", 
                "animation": "bounce_in"
            },
            EngagementElement.FIRE: {
                "style": "flame_effect",
                "color": "#ff4500",
                "size": "medium",
                "animation": "flicker"
            },
            EngagementElement.HEART: {
                "style": "heart_beat",
                "color": "#e91e63", 
                "size": "medium",
                "animation": "heartbeat"
            },
            EngagementElement.STAR: {
                "style": "sparkle_star",
                "color": "#ffd700",
                "size": "small",
                "animation": "twinkle"
            }
        }
    
    def _initialize_branding_library(self) -> Dict[str, BrandingElement]:
        """Inicializa biblioteca de elementos de branding."""
        return {
            "premium_logo": BrandingElement(
                type="logo",
                position="bottom_right",
                opacity=0.9,
                size="medium",
                animation="subtle_float"
            ),
            "watermark": BrandingElement(
                type="watermark", 
                position="top_left",
                opacity=0.6,
                size="small",
                animation="fade_in"
            ),
            "premium_badge": BrandingElement(
                type="badge",
                position="top_right", 
                opacity=1.0,
                size="medium",
                animation="shine"
            )
        }
    
    def generate_premium_template(self, 
                                 category: str,
                                 content: Dict[str, Any], 
                                 platform: Platform,
                                 monetization_type: MonetizationCategory = None,
                                 custom_style: PremiumStyle = None) -> Dict[str, Any]:
        """
        Gera um template premium completo.
        
        Args:
            category: Categoria do conteúdo
            content: Conteúdo do vídeo (título, texto, etc.)
            platform: Plataforma alvo
            monetization_type: Tipo de monetização desejado
            custom_style: Estilo customizado (opcional)
            
        Returns:
            Configuração completa do template premium
        """
        if monetization_type is None:
            monetization_type = self._determine_monetization_type(platform)
        
        if custom_style is None:
            custom_style = self.premium_styles[monetization_type]
        
        platform_specs = self.platform_specs[platform]
        
        # Obter template base profissional
        base_template = self._get_professional_template(category, monetization_type)
        
        # Aplicar estilo premium
        styled_template = self._apply_premium_styling(
            base_template, custom_style, platform_specs
        )
        
        # Adicionar elementos de engajamento
        engagement_elements = self._add_engagement_elements(
            styled_template, monetization_type
        )
        
        # Adicionar branding
        branding = self._add_professional_branding(
            engagement_elements, monetization_type, platform
        )
        
        # Ajustar para plataforma específica
        platform_optimized = self._optimize_for_platform(
            branding, platform_specs, content
        )
        
        return {
            "template_config": platform_optimized,
            "platform_specs": platform_specs,
            "monetization_type": monetization_type,
            "custom_style": custom_style,
            "engagement_elements": engagement_elements.get("engagement_elements", []),
            "branding": branding.get("branding", []),
            "created_at": datetime.now().isoformat()
        }
    
    def _determine_monetization_type(self, platform: Platform) -> MonetizationCategory:
        """Determina o tipo de monetização baseado na plataforma."""
        platform_type_map = {
            Platform.TIKTOK: MonetizationCategory.TIKKOK_ENGAGING,
            Platform.YOUTUBE_SHORTS: MonetizationCategory.SHORTS_EDUCATIONAL,
            Platform.INSTAGRAM_REELS: MonetizationCategory.REELS_PREMIUM,
            Platform.FACEBOOK_REELS: MonetizationCategory.REELS_PREMIUM
        }
        return platform_type_map.get(platform, MonetizationCategory.SHORTS_EDUCATIONAL)
    
    def _get_professional_template(self, category: str, 
                                 monetization_type: MonetizationCategory) -> VisualTemplate:
        """Obtém template profissional baseado na categoria."""
        professional_categories = {
            "SPACE": "space_professional",
            "ANIMALS": "animals_professional", 
            "SCIENCE": "science_professional",
            "HISTORY": "history_professional",
            "NATURE": "nature_professional"
        }
        
        template_name = professional_categories.get(category.upper(), "professional_end")
        
        # Tentar obter template específico da categoria profissional
        template = self.base_generator.get_template(category, TemplateType.CONTENT_SLIDE, template_name)
        
        # Se não encontrar, usar template profissional genérico
        if template is None:
            template = self.base_generator.get_template("GENERAL", TemplateType.CONTENT_SLIDE, "professional_end")
        
        # Se ainda não encontrar, usar template de conteúdo genérico
        if template is None:
            template = self.base_generator.get_template("GENERAL", TemplateType.CONTENT_SLIDE)
        
        # Garantir que temos um template válido
        if template is None:
            # Criar template básico como fallback
            from .visual_templates import TextOverlay
            template = VisualTemplate(
                name="fallback_professional",
                category="GENERAL",
                template_type=TemplateType.CONTENT_SLIDE,
                background_color="#000000",
                text_overlays=[
                    TextOverlay(
                        text="",
                        position="center",
                        style=TextStyle.MONTSERRAT_SEMI_BOLD,
                        color="#ffffff",
                        font_size=40,
                        duration=4.0,
                        animation="fade"
                    )
                ],
                duration=4.0
            )
        
        return template
    
    def _apply_premium_styling(self, template: VisualTemplate,
                              style: PremiumStyle,
                              platform_specs: PlatformSpecs) -> Dict[str, Any]:
        """Aplica estilo premium ao template."""
        
        # Ajustar cores baseadas no estilo
        template.background_color = style.primary_color
        
        # Ajustar fontes baseado no estilo
        if template.text_overlays:
            for overlay in template.text_overlays:
                overlay.style = style.text_style
                
                # Ajustar cores de texto
                if overlay.position == "top":
                    overlay.color = style.secondary_color
                elif overlay.position == "center":
                    overlay.color = style.accent_color
                else:
                    overlay.color = style.secondary_color
                
                # Ajustar tamanhos baseado na plataforma
                overlay.font_size = int(overlay.font_size * platform_specs.text_size_multiplier)
                
                # Ajustar animações baseadas na velocidade
                if style.animation_speed == "fast":
                    overlay.fade_in = max(0.3, overlay.fade_in * 0.7)
                    overlay.fade_out = max(0.3, overlay.fade_out * 0.7)
                elif style.animation_speed == "slow":
                    overlay.fade_in = min(2.0, overlay.fade_in * 1.5)
                    overlay.fade_out = min(2.0, overlay.fade_out * 1.5)
        
        return {
            "template": template,
            "style_applied": style,
            "background_style": style.background_style,
            "transition_style": style.transition_style
        }
    
    def _add_engagement_elements(self, styled_template: Dict[str, Any],
                                monetization_type: MonetizationCategory) -> Dict[str, Any]:
        """Adiciona elementos de engajamento baseados no tipo de monetização."""
        
        template = styled_template["template"]
        
        # Elementos de engajamento baseados no tipo
        engagement_config = {
            MonetizationCategory.TIKKOK_ENGAGING: [
                EngagementElement.ARROW,
                EngagementElement.FIRE,
                EngagementElement.HEART,
                EngagementElement.PULSE
            ],
            MonetizationCategory.SHORTS_EDUCATIONAL: [
                EngagementElement.CHECKMARK,
                EngagementElement.HIGHLIGHT,
                EngagementElement.ARROW,
                EngagementElement.STAR
            ],
            MonetizationCategory.REELS_PREMIUM: [
                EngagementElement.HEART,
                EngagementElement.STAR,
                EngagementElement.PULSE,
                EngagementElement.HIGHLIGHT
            ]
        }
        
        selected_elements = engagement_config.get(monetization_type, [])
        
        # Criar configurações dos elementos
        engagement_elements = []
        for element in selected_elements:
            element_config = self.engagement_library.get(element, {})
            engagement_elements.append({
                "type": element,
                "config": element_config,
                "position": self._get_engagement_position(element, monetization_type)
            })
        
        return {
            **styled_template,
            "engagement_elements": engagement_elements
        }
    
    def _get_engagement_position(self, element: EngagementElement,
                                monetization_type: MonetizationCategory) -> str:
        """Determina posição ideal para elemento de engajamento."""
        position_map = {
            MonetizationCategory.TIKKOK_ENGAGING: {
                EngagementElement.ARROW: "center_bottom",
                EngagementElement.FIRE: "top_right", 
                EngagementElement.HEART: "bottom_right",
                EngagementElement.PULSE: "center"
            },
            MonetizationCategory.SHORTS_EDUCATIONAL: {
                EngagementElement.CHECKMARK: "center",
                EngagementElement.HIGHLIGHT: "around_text",
                EngagementElement.ARROW: "right_side",
                EngagementElement.STAR: "top_right"
            },
            MonetizationCategory.REELS_PREMIUM: {
                EngagementElement.HEART: "center_right",
                EngagementElement.STAR: "top_right",
                EngagementElement.PULSE: "around_elements",
                EngagementElement.HIGHLIGHT: "subtle_glow"
            }
        }
        
        return position_map.get(monetization_type, {}).get(element, "center")
    
    def _add_professional_branding(self, template_with_engagement: Dict[str, Any],
                                  monetization_type: MonetizationCategory,
                                  platform: Platform) -> Dict[str, Any]:
        """Adiciona elementos de branding profissional."""
        
        # Seleção de branding baseada no tipo
        branding_config = {
            MonetizationCategory.TIKKOK_ENGAGING: ["premium_logo", "watermark"],
            MonetizationCategory.SHORTS_EDUCATIONAL: ["premium_badge", "watermark"],
            MonetizationCategory.REELS_PREMIUM: ["premium_logo", "premium_badge"]
        }
        
        selected_branding = branding_config.get(monetization_type, ["watermark"])
        
        # Configurações de branding
        branding_elements = []
        for branding_key in selected_branding:
            branding_element = self.branding_elements[branding_key]
            
            # Ajustar baseado na plataforma
            if platform == Platform.TIKTOK:
                branding_element.opacity *= 0.8  # Menos visível no TikTok
            
            branding_elements.append({
                "type": branding_element.type,
                "position": branding_element.position,
                "opacity": branding_element.opacity,
                "size": branding_element.size,
                "animation": branding_element.animation,
                "custom_path": branding_element.custom_path
            })
        
        return {
            **template_with_engagement,
            "branding": branding_elements
        }
    
    def _optimize_for_platform(self, branded_template: Dict[str, Any],
                              platform_specs: PlatformSpecs,
                              content: Dict[str, Any]) -> Dict[str, Any]:
        """Otimiza template para plataforma específica."""
        
        template = branded_template["template"]
        
        # Ajustar duração baseada na plataforma
        template.duration = min(template.duration, platform_specs.max_duration)
        
        # Ajustar padding baseado na plataforma
        padding = platform_specs.padding_percent
        
        # Ajustar posições de texto baseado no padding
        if template.text_overlays:
            for overlay in template.text_overlays:
                if overlay.custom_position:
                    # Aplicar padding às posições customizadas
                    x, y = overlay.custom_position
                    overlay.custom_position = (
                        max(padding, min(1-padding, x)),
                        max(padding, min(1-padding, y))
                    )
        
        # Adicionar conteúdo específico
        if content.get("title") and template.text_overlays:
            template.text_overlays[0].text = content["title"]
        
        if content.get("subtitle") and len(template.text_overlays) > 1:
            template.text_overlays[1].text = content["subtitle"]
        
        if content.get("description") and len(template.text_overlays) > 2:
            template.text_overlays[2].text = content["description"]
        
        return {
            **branded_template,
            "template": template,
            "platform_optimizations": {
                "aspect_ratio": platform_specs.aspect_ratio,
                "resolution": platform_specs.resolution,
                "padding_applied": padding,
                "duration_adjusted": template.duration != branded_template["template"].duration
            }
        }
    
    def apply_professional_styling(self, 
                                  video_segments: List[Dict[str, Any]],
                                  category: str) -> List[Dict[str, Any]]:
        """
        Aplica styling profissional a segmentos de vídeo.
        
        Args:
            video_segments: Segmentos de vídeo para estilizar
            category: Categoria do conteúdo
            
        Returns:
            Segmentos estilizados profissionalmente
        """
        styled_segments = []
        
        for segment in video_segments:
            # Determinar tipo de monetização para o segmento
            monetization_type = self._determine_segment_monetization(segment)
            
            # Aplicar estilo premium
            styled_segment = self._apply_segment_styling(
                segment, category, monetization_type
            )
            
            styled_segments.append(styled_segment)
        
        return styled_segments
    
    def _determine_segment_monetization(self, segment: Dict[str, Any]) -> MonetizationCategory:
        """Determina tipo de monetização para um segmento."""
        content_type = segment.get("content_type", "neutral")
        
        if "engaging" in content_type.lower():
            return MonetizationCategory.TIKKOK_ENGAGING
        elif "educational" in content_type.lower():
            return MonetizationCategory.SHORTS_EDUCATIONAL
        else:
            return MonetizationCategory.REELS_PREMIUM
    
    def _apply_segment_styling(self, segment: Dict[str, Any],
                              category: str,
                              monetization_type: MonetizationCategory) -> Dict[str, Any]:
        """Aplica styling a um segmento específico."""
        
        # Criar conteúdo mock para geração do template
        content = {
            "title": segment.get("title", ""),
            "subtitle": segment.get("subtitle", ""),
            "description": segment.get("description", "")
        }
        
        # Gerar template premium
        platform = Platform.YOUTUBE_SHORTS  # Plataforma padrão
        premium_config = self.generate_premium_template(
            category, content, platform, monetization_type
        )
        
        return {
            **segment,
            "premium_styling": premium_config,
            "styling_applied": True
        }
    
    def add_engagement_elements(self, video_path: str,
                              elements: List[EngagementElement] = None) -> Dict[str, Any]:
        """
        Adiciona elementos de engajamento ao vídeo.
        
        Args:
            video_path: Caminho do vídeo
            elements: Elementos de engajamento a adicionar
            
        Returns:
            Configuração dos elementos adicionados
        """
        if elements is None:
            elements = [EngagementElement.ARROW, EngagementElement.HEART]
        
        engagement_config = []
        
        for element in elements:
            element_data = self.engagement_library.get(element, {})
            engagement_config.append({
                "element_type": element.value,
                "style": element_data.get("style", ""),
                "color": element_data.get("color", "#ffffff"),
                "size": element_data.get("size", "medium"),
                "animation": element_data.get("animation", "none"),
                "timing": self._get_element_timing(element, video_path)
            })
        
        return {
            "video_path": video_path,
            "engagement_elements": engagement_config,
            "total_elements": len(engagement_config),
            "processing_status": "pending"
        }
    
    def _get_element_timing(self, element: EngagementElement, video_path: str) -> Dict[str, float]:
        """Determina timing ideal para elemento de engajamento."""
        
        # Timing padrão baseado no tipo de elemento
        timing_map = {
            EngagementElement.ARROW: {"start": 1.0, "duration": 2.0},
            EngagementElement.HEART: {"start": 0.5, "duration": 1.5},
            EngagementElement.FIRE: {"start": 2.0, "duration": 3.0},
            EngagementElement.PULSE: {"start": 0.0, "duration": 4.0},
            EngagementElement.CHECKMARK: {"start": 1.5, "duration": 2.5},
            EngagementElement.HIGHLIGHT: {"start": 1.0, "duration": 3.5},
            EngagementElement.STAR: {"start": 0.8, "duration": 1.8}
        }
        
        return timing_map.get(element, {"start": 1.0, "duration": 2.0})
    
    def generate_variants_for_ab_testing(self,
                                        base_config: Dict[str, Any],
                                        variant_count: int = 3) -> List[Dict[str, Any]]:
        """
        Gera variantes para A/B testing.
        
        Args:
            base_config: Configuração base
            variant_count: Número de variantes a gerar
            
        Returns:
            Lista de configurações variantes
        """
        variants = []
        
        for i in range(variant_count):
            variant = self._create_variant(base_config, i)
            variants.append(variant)
        
        return variants
    
    def _create_variant(self, base_config: Dict[str, Any,], variant_index: int) -> Dict[str, Any]:
        """Cria uma variante da configuração base."""
        
        variant = {
            **base_config,
            "variant_id": f"variant_{variant_index + 1}",
            "created_at": datetime.now().isoformat()
        }
        
        # Variações baseadas no índice
        if variant_index == 0:  # Variante com cores mais vibrantes
            variant["style_modifications"] = {
                "color_saturation": 1.2,
                "animation_speed": "fast",
                "text_size": "large"
            }
        elif variant_index == 1:  # Variante mais minimalista
            variant["style_modifications"] = {
                "color_saturation": 0.8,
                "animation_speed": "slow", 
                "text_size": "medium",
                "remove_engagement": ["fire", "pulse"]
            }
        else:  # Variante premium
            variant["style_modifications"] = {
                "color_saturation": 1.0,
                "animation_speed": "smooth",
                "text_size": "large",
                "enhanced_branding": True,
                "premium_elements": True
            }
        
        return variant
    
    def get_template_analytics(self, template_config: Dict[str, Any]) -> Dict[str, Any]:
        """Gera análise do template para otimização."""
        
        return {
            "engagement_score": self._calculate_engagement_score(template_config),
            "platform_optimization": self._assess_platform_optimization(template_config),
            "branding_effectiveness": self._evaluate_branding(template_config),
            "monetization_potential": self._assess_monetization_potential(template_config),
            "recommendations": self._generate_optimization_recommendations(template_config)
        }
    
    def _calculate_engagement_score(self, config: Dict[str, Any]) -> float:
        """Calcula score de engajamento do template."""
        score = 0.0
        
        # Score baseado em elementos de engajamento
        engagement_count = len(config.get("engagement_elements", []))
        score += min(engagement_count * 0.2, 1.0)
        
        # Score baseado em animações
        template = config.get("template_config", {}).get("template")
        if template and template.text_overlays:
            animated_overlays = sum(1 for overlay in template.text_overlays 
                                  if overlay.animation != "none")
            score += min(animated_overlays * 0.15, 0.5)
        
        # Score baseado em branding
        branding_count = len(config.get("branding", []))
        score += min(branding_count * 0.1, 0.3)
        
        return min(score, 1.0)
    
    def _assess_platform_optimization(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia otimização para plataforma."""
        
        platform_specs = config.get("platform_specs")
        if not platform_specs:
            return {"optimization_level": "unknown"}
        
        template = config.get("template_config", {}).get("template")
        if not template:
            return {"optimization_level": "unknown"}
        
        # Verificar duração
        duration_score = 1.0 if template.duration <= platform_specs.max_duration else 0.7
        
        # Verificar texto
        text_score = 1.0
        if template.text_overlays:
            for overlay in template.text_overlays:
                if overlay.font_size > 60:  # Texto muito grande
                    text_score *= 0.9
        
        overall_score = (duration_score + text_score) / 2
        
        return {
            "optimization_level": "excellent" if overall_score > 0.9 else "good" if overall_score > 0.7 else "needs_improvement",
            "duration_score": duration_score,
            "text_score": text_score,
            "overall_score": overall_score
        }
    
    def _evaluate_branding(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia efetividade do branding."""
        
        branding_elements = config.get("branding", [])
        
        return {
            "branding_elements_count": len(branding_elements),
            "branding_diversity": len(set(elem.get("type", "") for elem in branding_elements)),
            "opacity_optimization": sum(elem.get("opacity", 0.8) for elem in branding_elements) / max(len(branding_elements), 1),
            "effectiveness_score": min(len(branding_elements) * 0.3, 1.0)
        }
    
    def _assess_monetization_potential(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia potencial de monetização."""
        
        monetization_type = config.get("monetization_type")
        engagement_score = self._calculate_engagement_score(config)
        platform_opt = self._assess_platform_optimization(config)
        
        # Score base por tipo de monetização
        base_scores = {
            MonetizationCategory.TIKKOK_ENGAGING: 0.8,
            MonetizationCategory.SHORTS_EDUCATIONAL: 0.7,
            MonetizationCategory.REELS_PREMIUM: 0.9
        }
        
        base_score = base_scores.get(monetization_type, 0.7)
        
        # Aplicar modificadores
        final_score = base_score * engagement_score * platform_opt.get("overall_score", 0.8)
        
        return {
            "potential_score": min(final_score, 1.0),
            "monetization_type": monetization_type.value if monetization_type else "unknown",
            "engagement_contribution": engagement_score,
            "platform_contribution": platform_opt.get("overall_score", 0.8)
        }
    
    def _generate_optimization_recommendations(self, config: Dict[str, Any]) -> List[str]:
        """Gera recomendações de otimização."""
        
        recommendations = []
        
        # Análise de engajamento
        engagement_score = self._calculate_engagement_score(config)
        if engagement_score < 0.6:
            recommendations.append("Adicionar mais elementos de engajamento (setas, destaques, etc.)")
        
        # Análise de plataforma
        platform_opt = self._assess_platform_optimization(config)
        if platform_opt.get("overall_score", 1.0) < 0.8:
            recommendations.append("Otimizar texto e duração para plataforma específica")
        
        # Análise de branding
        branding_eval = self._evaluate_branding(config)
        if branding_eval.get("branding_elements_count", 0) < 2:
            recommendations.append("Adicionar mais elementos de branding (logo, watermark)")
        
        # Análise de monetização
        monet_potential = self._assess_monetization_potential(config)
        if monet_potential.get("potential_score", 1.0) < 0.7:
            recommendations.append("Ajustar estilo para maximizar potencial de monetização")
        
        return recommendations

# Instância global do engine premium
premium_engine = PremiumTemplateEngine()

# Funções de conveniência
def generate_premium_template(category: str, content: Dict[str, Any], 
                            platform: Platform, 
                            monetization_type: MonetizationCategory = None) -> Dict[str, Any]:
    """Função de conveniência para gerar template premium."""
    return premium_engine.generate_premium_template(category, content, platform, monetization_type)

def apply_professional_styling(video_segments: List[Dict[str, Any]], 
                             category: str) -> List[Dict[str, Any]]:
    """Função de conveniência para aplicar styling profissional."""
    return premium_engine.apply_professional_styling(video_segments, category)

def add_engagement_elements(video_path: str, 
                          elements: List[EngagementElement] = None) -> Dict[str, Any]:
    """Função de conveniência para adicionar elementos de engajamento."""
    return premium_engine.add_engagement_elements(video_path, elements)

def generate_ab_test_variants(base_config: Dict[str, Any], 
                            variant_count: int = 3) -> List[Dict[str, Any]]:
    """Função de conveniência para gerar variantes A/B."""
    return premium_engine.generate_variants_for_ab_testing(base_config, variant_count)

if __name__ == "__main__":
print("=== Teste do Premium Template Engine ===")
    
    # Teste de geração de template premium
    content = {
        "title": "Descubra os Segredos do Espaço",
        "subtitle": "Uma jornada incrível pelas estrelas",
        "description": "Explore os mistérios do universo conosco!"
    }
    
    premium_config = generate_premium_template(
        "SPACE", 
        content, 
        Platform.TIKTOK,
        MonetizationCategory.TIKKOK_ENGAGING
    )
    
print(f"Template gerado: {premium_config['monetization_type'].value}")
print(f"Plataforma: {list(Platform)[list(Platform).index(Platform.TIKTOK)].value}")
print(f"Elementos de engajamento: {len(premium_config['engagement_elements'])}")
print(f"Elementos de branding: {len(premium_config['branding'])}")
    
    # Teste de análise do template
    analytics = premium_engine.get_template_analytics(premium_config)
print(f"\nAnálise do Template:")
print(f"Score de engajamento: {analytics['engagement_score']:.2f}")
print(f"Potencial de monetização: {analytics['monetization_potential']['potential_score']:.2f}")
print(f"Recomendações: {len(analytics['recommendations'])}")
    
    # Teste de geração de variantes A/B
    variants = generate_ab_test_variants(premium_config, 3)
print(f"\nVariantes A/B geradas: {len(variants)}")
    for i, variant in enumerate(variants):
print(f"  Variante {i+1}: {variant['variant_id']}")
