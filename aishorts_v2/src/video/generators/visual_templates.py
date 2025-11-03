"""
Templates visuais para geração de conteúdo de vídeo curto

Contém templates organizados por categoria (SPACE, ANIMALS, etc.) com sobreposições
de texto, efeitos de transição e estilos visuais.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import colorsys

class TemplateType(Enum):
    """Tipos de template visuais."""
    TITLE_SLIDE = "title_slide"
    CONTENT_SLIDE = "content_slide"
    TRANSITION = "transition"
    END_CARD = "end_card"
    BACKGROUND = "background"

class TextStyle(Enum):
    """Estilos de texto."""
    MODERN_SANS = "modern_sans"
    ELEGANT_SERIF = "elegant_serif"
    TECHNICAL_MONO = "technical_mono"
    PLAYFUL_ROUND = "playful_round"
    SCIENTIFIC_BOLD = "scientific_bold"

@dataclass
class TextOverlay:
    """Configuração de sobreposição de texto."""
    text: str
    position: str  # "top", "center", "bottom", "custom"
    style: TextStyle
    color: str
    font_size: int
    duration: float
    fade_in: float = 0.5
    fade_out: float = 0.5
    animation: str = "none"  # "fade", "slide_up", "zoom", "typewriter"
    custom_position: Optional[tuple] = None

@dataclass
class VisualTemplate:
    """Template visual completo."""
    name: str
    category: str
    template_type: TemplateType
    background_color: str
    background_image: Optional[str] = None
    text_overlays: List[TextOverlay] = None
    transitions: List[str] = None
    duration: float = 5.0
    audio_cue: Optional[str] = None

class VisualTemplateGenerator:
    """Gerador de templates visuais."""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.color_palettes = self._initialize_color_palettes()
        self.transition_effects = self._initialize_transition_effects()
    
    def _initialize_templates(self) -> List[VisualTemplate]:
        """Inicializa todos os templates visuais."""
        templates = []
        
        # =================== SPACE ===================
        
        # Template de título - SPACE
        space_title = VisualTemplate(
            name="space_title",
            category="SPACE",
            template_type=TemplateType.TITLE_SLIDE,
            background_color="#000428",
            text_overlays=[
                TextOverlay(
                    text="",
                    position="center",
                    style=TextStyle.MODERN_SANS,
                    color="#ffffff",
                    font_size=72,
                    duration=3.0,
                    animation="zoom"
                )
            ],
            transitions=["fade", "zoom"],
            duration=3.0,
            audio_cue="space_whoosh"
        )
        templates.append(space_title)
        
        # Template de conteúdo - SPACE
        space_content = VisualTemplate(
            name="space_content",
            category="SPACE",
            template_type=TemplateType.CONTENT_SLIDE,
            background_color="#004e92",
            text_overlays=[
                TextOverlay(
                    text="",
                    position="top",
                    style=TextStyle.SCIENTIFIC_BOLD,
                    color="#e0f7ff",
                    font_size=48,
                    duration=4.0,
                    animation="slide_down"
                ),
                TextOverlay(
                    text="",
                    position="bottom",
                    style=TextStyle.MODERN_SANS,
                    color="#ffffff",
                    font_size=32,
                    duration=4.0,
                    animation="fade"
                )
            ],
            transitions=["slide", "dissolve"],
            duration=4.0
        )
        templates.append(space_content)
        
        # =================== ANIMALS ===================
        
        # Template de título - ANIMALS
        animals_title = VisualTemplate(
            name="animals_title",
            category="ANIMALS",
            template_type=TemplateType.TITLE_SLIDE,
            background_color="#ff6b6b",
            text_overlays=[
                TextOverlay(
                    text="",
                    position="center",
                    style=TextStyle.PLAYFUL_ROUND,
                    color="#ffffff",
                    font_size=64,
                    duration=2.5,
                    animation="bounce"
                )
            ],
            transitions=["bounce", "fade"],
            duration=2.5,
            audio_cue="animal_sound"
        )
        templates.append(animals_title)
        
        # Template de conteúdo - ANIMALS
        animals_content = VisualTemplate(
            name="animals_content",
            category="ANIMALS",
            template_type=TemplateType.CONTENT_SLIDE,
            background_color="#4ecdc4",
            text_overlays=[
                TextOverlay(
                    text="",
                    position="center",
                    style=TextStyle.PLAYFUL_ROUND,
                    color="#2c3e50",
                    font_size=40,
                    duration=4.0,
                    animation="typewriter"
                ),
                TextOverlay(
                    text="",
                    position="bottom",
                    style=TextStyle.MODERN_SANS,
                    color="#ffffff",
                    font_size=28,
                    duration=3.0,
                    animation="slide_up"
                )
            ],
            transitions=["morph", "cut"],
            duration=4.0
        )
        templates.append(animals_content)
        
        # =================== SCIENCE ===================
        
        # Template de título - SCIENCE
        science_title = VisualTemplate(
            name="science_title",
            category="SCIENCE",
            template_type=TemplateType.TITLE_SLIDE,
            background_color="#2c3e50",
            text_overlays=[
                TextOverlay(
                    text="",
                    position="center",
                    style=TextStyle.SCIENTIFIC_BOLD,
                    color="#3498db",
                    font_size=68,
                    duration=3.5,
                    animation="glitch"
                )
            ],
            transitions=["slide", "wipe"],
            duration=3.5,
            audio_cue="science_beep"
        )
        templates.append(science_title)
        
        # Template de conteúdo - SCIENCE
        science_content = VisualTemplate(
            name="science_content",
            category="SCIENCE",
            template_type=TemplateType.CONTENT_SLIDE,
            background_color="#34495e",
            text_overlays=[
                TextOverlay(
                    text="",
                    position="top",
                    style=TextStyle.TECHNICAL_MONO,
                    color="#ecf0f1",
                    font_size=44,
                    duration=4.5,
                    animation="slide_right"
                ),
                TextOverlay(
                    text="",
                    position="center",
                    style=TextStyle.MODERN_SANS,
                    color="#3498db",
                    font_size=36,
                    duration=4.5,
                    animation="fade"
                )
            ],
            transitions=["dissolve", "slide"],
            duration=4.5
        )
        templates.append(science_content)
        
        # =================== HISTORY ===================
        
        # Template de título - HISTORY
        history_title = VisualTemplate(
            name="history_title",
            category="HISTORY",
            template_type=TemplateType.TITLE_SLIDE,
            background_color="#8B4513",
            text_overlays=[
                TextOverlay(
                    text="",
                    position="center",
                    style=TextStyle.ELEGANT_SERIF,
                    color="#D2B48C",
                    font_size=66,
                    duration=4.0,
                    animation="old_film"
                )
            ],
            transitions=["sepia", "fade"],
            duration=4.0,
            audio_cue="vintage_ambience"
        )
        templates.append(history_title)
        
        # Template de conteúdo - HISTORY
        history_content = VisualTemplate(
            name="history_content",
            category="HISTORY",
            template_type=TemplateType.CONTENT_SLIDE,
            background_color="#D2B48C",
            text_overlays=[
                TextOverlay(
                    text="",
                    position="top",
                    style=TextStyle.ELEGANT_SERIF,
                    color="#8B4513",
                    font_size=42,
                    duration=5.0,
                    animation="typewriter"
                ),
                TextOverlay(
                    text="",
                    position="bottom",
                    style=TextStyle.MODERN_SANS,
                    color="#654321",
                    font_size=30,
                    duration=4.0,
                    animation="slide_up"
                )
            ],
            transitions=["sepia", "slide"],
            duration=5.0
        )
        templates.append(history_content)
        
        # =================== NATURE ===================
        
        # Template de título - NATURE
        nature_title = VisualTemplate(
            name="nature_title",
            category="NATURE",
            template_type=TemplateType.TITLE_SLIDE,
            background_color="#228B22",
            text_overlays=[
                TextOverlay(
                    text="",
                    position="center",
                    style=TextStyle.MODERN_SANS,
                    color="#90EE90",
                    font_size=62,
                    duration=3.0,
                    animation="flow"
                )
            ],
            transitions=["fade", "dissolve"],
            duration=3.0,
            audio_cue="nature_sounds"
        )
        templates.append(nature_title)
        
        # Template de conteúdo - NATURE
        nature_content = VisualTemplate(
            name="nature_content",
            category="NATURE",
            template_type=TemplateType.CONTENT_SLIDE,
            background_color="#90EE90",
            text_overlays=[
                TextOverlay(
                    text="",
                    position="center",
                    style=TextStyle.ORGANIC_SANS,
                    color="#228B22",
                    font_size=38,
                    duration=4.5,
                    animation="float"
                ),
                TextOverlay(
                    text="",
                    position="bottom",
                    style=TextStyle.MODERN_SANS,
                    color="#006400",
                    font_size=28,
                    duration=3.5,
                    animation="fade"
                )
            ],
            transitions=["dissolve", "fade"],
            duration=4.5
        )
        templates.append(nature_content)
        
        # =================== END CARDS ===================
        
        # End card genérico
        generic_end = VisualTemplate(
            name="generic_end",
            category="GENERAL",
            template_type=TemplateType.END_CARD,
            background_color="#2c3e50",
            text_overlays=[
                TextOverlay(
                    text="Acompanhe para mais!",
                    position="center",
                    style=TextStyle.MODERN_SANS,
                    color="#ffffff",
                    font_size=48,
                    duration=3.0,
                    animation="pulse"
                ),
                TextOverlay(
                    text="@aishorts",
                    position="bottom",
                    style=TextStyle.PLAYFUL_ROUND,
                    color="#3498db",
                    font_size=36,
                    duration=3.0,
                    animation="fade"
                )
            ],
            transitions=["fade", "zoom"],
            duration=3.0
        )
        templates.append(generic_end)
        
        return templates
    
    def _initialize_color_palettes(self) -> Dict[str, List[str]]:
        """Inicializa paletas de cores por categoria."""
        return {
            "SPACE": ["#000428", "#004e92", "#ffffff", "#e0f7ff", "#87ceeb"],
            "ANIMALS": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#ffeaa7"],
            "SCIENCE": ["#2c3e50", "#3498db", "#ecf0f1", "#34495e", "#1abc9c"],
            "HISTORY": ["#8B4513", "#D2B48C", "#F5F5DC", "#654321", "#CD853F"],
            "NATURE": ["#228B22", "#90EE90", "#98FB98", "#006400", "#ADFF2F"],
            "GENERAL": ["#2c3e50", "#3498db", "#ffffff", "#ecf0f1", "#95a5a6"]
        }
    
    def _initialize_transition_effects(self) -> Dict[str, List[str]]:
        """Inicializa efeitos de transição por categoria."""
        return {
            "SPACE": ["fade", "slide", "zoom", "dissolve", "glitch"],
            "ANIMALS": ["cut", "fade", "morph", "bounce", "swing"],
            "SCIENCE": ["dissolve", "wipe", "slide", "glitch", "data_stream"],
            "HISTORY": ["sepia", "fade", "slide", "old_film", "vintage"],
            "NATURE": ["fade", "dissolve", "slide", "flow", "organic"],
            "GENERAL": ["fade", "slide", "zoom", "dissolve"]
        }
    
    def get_template(self, category: str, template_type: TemplateType, 
                    name: str = None) -> Optional[VisualTemplate]:
        """
        Obtém um template específico.
        
        Args:
            category: Categoria do conteúdo
            template_type: Tipo de template
            name: Nome específico do template (opcional)
            
        Returns:
            Template encontrado ou None
        """
        category = category.upper()
        
        # Filtrar templates pela categoria e tipo
        filtered_templates = [
            t for t in self.templates 
            if t.category.upper() == category and t.template_type == template_type
        ]
        
        # Se nome especificado, retornar o template específico
        if name:
            for template in filtered_templates:
                if template.name == name:
                    return template
        
        # Se não há nome específico, retornar o primeiro da lista
        return filtered_templates[0] if filtered_templates else None
    
    def get_templates_by_category(self, category: str) -> List[VisualTemplate]:
        """Obtém todos os templates de uma categoria."""
        category = category.upper()
        return [t for t in self.templates if t.category.upper() == category]
    
    def get_templates_by_type(self, template_type: TemplateType) -> List[VisualTemplate]:
        """Obtém todos os templates de um tipo específico."""
        return [t for t in self.templates if t.template_type == template_type]
    
    def generate_custom_text_overlay(self, text: str, category: str, 
                                   position: str = "center") -> TextOverlay:
        """
        Gera uma sobreposição de texto customizada baseada na categoria.
        
        Args:
            text: Texto a ser exibido
            category: Categoria do conteúdo
            position: Posição do texto
            
        Returns:
            TextOverlay configurado
        """
        category = category.upper()
        palette = self.color_palettes.get(category, self.color_palettes["GENERAL"])
        
        # Mapear categorias para estilos
        style_map = {
            "SPACE": TextStyle.MODERN_SANS,
            "ANIMALS": TextStyle.PLAYFUL_ROUND,
            "SCIENCE": TextStyle.SCIENTIFIC_BOLD,
            "HISTORY": TextStyle.ELEGANT_SERIF,
            "NATURE": TextStyle.MODERN_SANS,
            "GENERAL": TextStyle.MODERN_SANS
        }
        
        # Selecionar cor (primeira cor da paleta)
        color = palette[1] if len(palette) > 1 else palette[0]
        
        return TextOverlay(
            text=text,
            position=position,
            style=style_map.get(category, TextStyle.MODERN_SANS),
            color=color,
            font_size=36,  # Tamanho padrão
            duration=3.0,  # Duração padrão
            animation="fade"
        )
    
    def get_color_palette(self, category: str) -> List[str]:
        """Obtém paleta de cores para uma categoria."""
        return self.color_palettes.get(category.upper(), self.color_palettes["GENERAL"])
    
    def get_transition_effects(self, category: str) -> List[str]:
        """Obtém efeitos de transição disponíveis para uma categoria."""
        return self.transition_effects.get(category.upper(), self.transition_effects["GENERAL"])
    
    def create_sequence_template(self, category: str, content_parts: List[str],
                               sequence_type: str = "educational") -> List[VisualTemplate]:
        """
        Cria uma sequência de templates para uma história educacional.
        
        Args:
            category: Categoria do conteúdo
            content_parts: Partes do conteúdo (título, conteúdo 1, conteúdo 2, etc.)
            sequence_type: Tipo de sequência (educational, storytelling, etc.)
            
        Returns:
            Lista de templates na sequência
        """
        templates = []
        category = category.upper()
        
        # Template de título
        title_template = self.get_template(category, TemplateType.TITLE_SLIDE)
        if title_template and content_parts:
            title_template.text_overlays[0].text = content_parts[0]
            templates.append(title_template)
        
        # Templates de conteúdo
        content_templates = self.get_templates_by_category(category)
        content_templates = [t for t in content_templates if t.template_type == TemplateType.CONTENT_SLIDE]
        
        for i, part in enumerate(content_parts[1:], 1):
            if i <= len(content_templates):
                template = content_templates[i-1].__class__(**content_templates[i-1].__dict__)
                if template.text_overlays:
                    # Definir texto no primeiro overlay
                    template.text_overlays[0].text = part
                    templates.append(template)
        
        # Template de final (opcional)
        end_template = self.get_template("GENERAL", TemplateType.END_CARD)
        if end_template and sequence_type == "educational":
            templates.append(end_template)
        
        return templates
    
    def generate_background_variation(self, category: str, base_color: str = None) -> str:
        """
        Gera uma variação de cor de fundo baseada na categoria.
        
        Args:
            category: Categoria do conteúdo
            base_color: Cor base (opcional)
            
        Returns:
            Cor de fundo em hexadecimal
        """
        palette = self.get_color_palette(category)
        
        if base_color:
            # Gerar variação da cor base
            try:
                # Converter hex para RGB
                base_rgb = tuple(int(base_color[i:i+2], 16) for i in (1, 3, 5))
                # Gerar nova cor com leve variação
                h, s, v = colorsys.rgb_to_hsv(*[x/255.0 for x in base_rgb])
                new_v = min(1.0, v * 1.1)  # Aumentar valor em 10%
                new_rgb = colorsys.hsv_to_rgb(h, s, new_v)
                return f"#{int(new_rgb[0]*255):02x}{int(new_rgb[1]*255):02x}{int(new_rgb[2]*255):02x}"
            except:
                pass
        
        # Retornar segunda cor da paleta (geralmente mais clara)
        return palette[1] if len(palette) > 1 else palette[0]

# Classe complementar para diferentes estilos de fonte
class TextStyle(Enum):
    """Estilos de texto expandidos."""
    MODERN_SANS = "modern_sans"
    ELEGANT_SERIF = "elegant_serif"
    TECHNICAL_MONO = "technical_mono"
    PLAYFUL_ROUND = "playful_round"
    SCIENTIFIC_BOLD = "scientific_bold"
    ORGANIC_SANS = "organic_sans"

# Instância global do gerador
template_generator = VisualTemplateGenerator()

# Função de conveniência
def get_template(category: str, template_type: TemplateType, name: str = None) -> Optional[VisualTemplate]:
    """Função de conveniência para obter templates."""
    return template_generator.get_template(category, template_type, name)

def generate_text_overlay(text: str, category: str, position: str = "center") -> TextOverlay:
    """Função de conveniência para gerar sobreposições de texto."""
    return template_generator.generate_custom_text_overlay(text, category, position)

def get_category_palette(category: str) -> List[str]:
    """Função de conveniência para obter paletas de cores."""
    return template_generator.get_color_palette(category)

if __name__ == "__main__":
    print("=== Teste do Gerador de Templates Visuais ===")
    
    # Teste de obtenção de template
    space_title = get_template("SPACE", TemplateType.TITLE_SLIDE)
    print(f"Template SPACE Título: {space_title.name if space_title else 'None'}")
    
    # Teste de geração de texto
    text_overlay = generate_text_overlay("Teste de Texto", "ANIMALS", "center")
    print(f"Texto overlay: {text_overlay.text}, Cor: {text_overlay.color}")
    
    # Teste de paleta de cores
    palette = get_category_palette("SCIENCE")
    print(f"Paleta SCIENCE: {palette}")
    
    # Teste de sequência
    content = ["Título do Vídeo", "Primeiro Fato", "Segundo Fato", "Conclusão"]
    sequence = template_generator.create_sequence_template("SPACE", content)
    print(f"Sequência criada com {len(sequence)} templates")