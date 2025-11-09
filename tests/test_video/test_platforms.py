"""
Testes para funcionalidades de plataformas de vídeo

Testa configurações de plataforma, otimização e templates visuais.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Imports do projeto (ajustados para layout real do snapshot 1bd09aa)
from src.config.video_platforms import (
    Platform,
    VideoFormat,
    VideoCodec,
    AudioCodec,
    VideoSpecs,
    QualityPreset,
    VideoPlatformConfig,
    video_config,
    get_category_config,
    get_timing_preset,
    TIMING_PRESETS,
    CONTENT_CATEGORY_CONFIGS,
)

from src.video.processing.platform_optimizer import (
    PlatformOptimizer,
    VideoProcessingError,
    optimize_video,
)

from src.video.generators.visual_templates import (
    VisualTemplate,
    VisualTemplateGenerator,
    TextOverlay,
    TemplateType,
    TextStyle,
    template_generator,
    get_template,
    generate_text_overlay,
)


class TestVideoPlatformConfig:
    """Testes para VideoPlatformConfig."""
    
    def test_init_platform_configs(self):
        """Testa inicialização das configurações de plataforma."""
        config = VideoPlatformConfig()
        
        # Verificar se todas as plataformas foram inicializadas
        assert Platform.TIKTOK in config.platforms
        assert Platform.YOUTUBE_SHORTS in config.platforms
        assert Platform.INSTAGRAM_REELS in config.platforms
        
        # Verificar especificações do TikTok
        tiktok_specs = config.get_platform_specs(Platform.TIKTOK)
        assert tiktok_specs.name == "TikTok"
        assert tiktok_specs.resolution == (1080, 1920)
        assert tiktok_specs.aspect_ratio == "9:16"
        assert tiktok_specs.duration_max == 600  # 10 minutos
        assert tiktok_specs.fps == 30
    
    def test_get_platform_specs(self):
        """Testa obtenção de especificações de plataforma."""
        specs = video_config.get_platform_specs(Platform.TIKTOK)
        
        assert isinstance(specs, VideoSpecs)
        assert specs.name == "TikTok"
        assert specs.resolution_str == "1080x1920"
    
    def test_get_quality_preset(self):
        """Testa obtenção de preset de qualidade."""
        preset = video_config.get_quality_preset("Média")
        assert preset.name == "Média"
        assert preset.bitrate_kbps == 3000
        
        # Teste de preset inexistente (deve retornar padrão)
        default_preset = video_config.get_quality_preset("Inexistente")
        assert default_preset.name == "Média"
    
    def test_get_safe_zone(self):
        """Testa obtenção de zona segura."""
        safe_zone = video_config.get_safe_zone(Platform.TIKTOK)
        
        assert "top_margin_pct" in safe_zone
        assert "bottom_margin_pct" in safe_zone
        assert "side_margin_pct" in safe_zone
        assert safe_zone["top_margin_pct"] == 10
        assert safe_zone["bottom_margin_pct"] == 15
    
    def test_validate_video_for_platform(self):
        """Testa validação de vídeo para plataforma."""
        # Criar arquivo temporário para teste
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            result = video_config.validate_video_for_platform(temp_path, Platform.TIKTOK)
            
            assert "valid" in result
            assert "score" in result
            assert "checks" in result
            assert "recommendations" in result
            assert isinstance(result["checks"], dict)
            assert isinstance(result["recommendations"], list)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_content_category_configs(self):
        """Testa configurações de categoria de conteúdo."""
        space_config = get_category_config("SPACE")
        assert "transition_effects" in space_config
        assert "text_overlay_style" in space_config
        assert "color_palette" in space_config
        assert "timing_preset" in space_config
        assert space_config["timing_preset"] == "educational"
        
        # Teste categoria inexistente (deve retornar config de SPACE)
        default_config = get_category_config("NONEXISTENT")
        assert default_config == CONTENT_CATEGORY_CONFIGS["SPACE"]
    
    def test_timing_presets(self):
        """Testa presets de timing."""
        educational = get_timing_preset("educational")
        assert "hook_duration" in educational
        assert "value_delivery_segments" in educational
        assert educational["hook_duration"] == 3
        
        # Teste preset inexistente
        default_timing = get_timing_preset("nonexistent")
        assert default_timing == TIMING_PRESETS["educational"]


class TestPlatformOptimizer:
    """Testes para PlatformOptimizer."""
    
    def test_init(self):
        """Testa inicialização do otimizador."""
        optimizer = PlatformOptimizer()
        
        assert optimizer.config is not None
        assert optimizer.temp_dir is not None
        assert os.path.exists(optimizer.temp_dir)
    
    def test_adjust_timing(self):
        """Testa ajuste de timing."""
        optimizer = PlatformOptimizer()
        
        # Simular vídeo de 30 segundos para TikTok
        with patch.object(optimizer, '_get_video_duration', return_value=30.0):
            result = optimizer.adjust_timing("dummy_path.mp4", Platform.TIKTOK, "SPACE")
            
            assert result["success"] == True
            assert "current_duration" in result
            assert "optimized_timing" in result
            assert "recommendations" in result
            assert result["current_duration"] == 30.0
    
    def test_apply_platform_settings(self):
        """Testa aplicação de configurações de plataforma."""
        optimizer = PlatformOptimizer()
        
        # Simular processamento
        with patch.object(optimizer, '_run_ffmpeg_with_settings') as mock_ffmpeg:
            mock_ffmpeg.return_value = {"return_code": 0, "output": "success"}
            
            result = optimizer.apply_platform_settings("dummy_path.mp4", Platform.TIKTOK)
            
            assert result["success"] == True
            assert "output_path" in result
            assert "platform_specs" in result
            assert mock_ffmpeg.called
    
    @patch('src.video.processing.platform_optimizer.subprocess')
    def test_optimize_for_platform_error_handling(self, mock_subprocess):
        """Testa tratamento de erros na otimização."""
        optimizer = PlatformOptimizer()
        
        # Simular erro na validação
        with patch.object(optimizer, '_validate_input_video') as mock_validate:
            mock_validate.return_value = {"valid": False, "issues": ["Arquivo não encontrado"]}
            
            result = optimizer.optimize_for_platform("nonexistent.mp4", Platform.TIKTOK)
            
            assert result["success"] == False
            assert "error" in result
            assert "Arquivo não encontrado" in result["error"]
    
    def test_generate_output_paths(self):
        """Testa geração de caminhos de saída."""
        optimizer = PlatformOptimizer()
        
        output_path = optimizer._generate_output_path("video.mp4", Platform.TIKTOK, "SPACE")
        
        assert "video_tiktok_space.mp4" in output_path
        assert Platform.TIKTOK.value in output_path
        assert "SPACE" in output_path.lower()
    
    def test_cleanup(self):
        """Testa limpeza de arquivos temporários."""
        optimizer = PlatformOptimizer()
        temp_dir = optimizer.temp_dir
        
        assert os.path.exists(temp_dir)
        
        optimizer.cleanup()
        
        assert not os.path.exists(temp_dir)


class TestVisualTemplateGenerator:
    """Testes para VisualTemplateGenerator."""
    
    def test_init_templates(self):
        """Testa inicialização de templates."""
        generator = VisualTemplateGenerator()
        
        # Verificar se templates foram criados
        assert len(generator.templates) > 0
        
        # Verificar se todos os tipos estão representados
        template_types = {t.template_type for t in generator.templates}
        assert TemplateType.TITLE_SLIDE in template_types
        assert TemplateType.CONTENT_SLIDE in template_types
        assert TemplateType.END_CARD in template_types
    
    def test_get_template_by_category_and_type(self):
        """Testa obtenção de template por categoria e tipo."""
        template = template_generator.get_template("SPACE", TemplateType.TITLE_SLIDE)
        
        assert template is not None
        assert template.category == "SPACE"
        assert template.template_type == TemplateType.TITLE_SLIDE
    
    def test_get_template_by_name(self):
        """Testa obtenção de template por nome."""
        template = template_generator.get_template("SPACE", TemplateType.TITLE_SLIDE, "space_title")
        
        assert template is not None
        assert template.name == "space_title"
    
    def test_get_templates_by_category(self):
        """Testa obtenção de templates por categoria."""
        space_templates = template_generator.get_templates_by_category("SPACE")
        
        assert len(space_templates) > 0
        assert all(t.category == "SPACE" for t in space_templates)
    
    def test_get_templates_by_type(self):
        """Testa obtenção de templates por tipo."""
        title_templates = template_generator.get_templates_by_type(TemplateType.TITLE_SLIDE)
        
        assert len(title_templates) > 0
        assert all(t.template_type == TemplateType.TITLE_SLIDE for t in title_templates)
    
    def test_generate_custom_text_overlay(self):
        """Testa geração de sobreposição de texto customizada."""
        overlay = template_generator.generate_custom_text_overlay(
            "Teste", "ANIMALS", "center"
        )
        
        assert overlay.text == "Teste"
        assert overlay.position == "center"
        assert overlay.style == TextStyle.PLAYFUL_ROUND
        assert overlay.color in template_generator.get_color_palette("ANIMALS")
        assert overlay.duration == 3.0
    
    def test_get_color_palette(self):
        """Testa obtenção de paleta de cores."""
        space_palette = template_generator.get_color_palette("SPACE")
        animals_palette = template_generator.get_color_palette("ANIMALS")
        
        assert len(space_palette) > 0
        assert len(animals_palette) > 0
        assert space_palette != animals_palette  # Paletas devem ser diferentes
        
        # Teste categoria inexistente
        default_palette = template_generator.get_color_palette("NONEXISTENT")
        assert default_palette == template_generator.color_palettes["GENERAL"]
    
    def test_get_transition_effects(self):
        """Testa obtenção de efeitos de transição."""
        space_effects = template_generator.get_transition_effects("SPACE")
        animals_effects = template_generator.get_transition_effects("ANIMALS")
        
        assert len(space_effects) > 0
        assert len(animals_effects) > 0
        assert "fade" in space_effects  # Efeito comum
    
    def test_create_sequence_template(self):
        """Testa criação de sequência de templates."""
        content = ["Título", "Fato 1", "Fato 2"]
        sequence = template_generator.create_sequence_template("SPACE", content)
        
        assert len(sequence) > 0
        
        # Primeiro template deve ser de título
        assert sequence[0].template_type == TemplateType.TITLE_SLIDE
        
        # Template de título deve ter o texto correto
        assert sequence[0].text_overlays[0].text == "Título"
    
    def test_generate_background_variation(self):
        """Testa geração de variação de cor de fundo."""
        # Teste com categoria específica
        variation = template_generator.generate_background_variation("SPACE")
        assert variation in template_generator.get_color_palette("SPACE")
        
        # Teste com cor base
        variation_with_base = template_generator.generate_background_variation(
            "ANIMALS", "#ff0000"
        )
        assert variation_with_base.startswith("#")


class TestConvenienceFunctions:
    """Testes para funções de conveniência."""
    
    def test_get_template_function(self):
        """Testa função de conveniência get_template."""
        template = get_template("SPACE", TemplateType.TITLE_SLIDE)
        assert template is not None
        assert template.category == "SPACE"
    
    def test_generate_text_overlay_function(self):
        """Testa função de conveniência generate_text_overlay."""
        overlay = generate_text_overlay("Teste", "SCIENCE", "top")
        assert overlay.text == "Teste"
        assert overlay.position == "top"
        assert overlay.style == TextStyle.SCIENTIFIC_BOLD
    
    def test_get_category_palette_function(self):
        """Testa função de conveniência get_category_palette."""
        palette = template_generator.get_color_palette("NATURE")
        assert len(palette) > 0
        assert "#228B22" in palette  # Verde escuro esperado para natureza


class TestIntegration:
    """Testes de integração."""
    
    def test_platform_config_completeness(self):
        """Testa completude das configurações de plataforma."""
        # Verificar se todas as plataformas têm configurações válidas
        for platform in Platform:
            specs = video_config.get_platform_specs(platform)
            safe_zone = video_config.get_safe_zone(platform)
            export_settings = video_config._get_export_settings(platform, specs)
            
            assert specs.resolution == (1080, 1920)
            assert specs.aspect_ratio == "9:16"
            assert specs.fps >= 24
            assert len(safe_zone) > 0
            assert export_settings["container"] in ["mp4", "mov"]
    
    def test_template_consistency(self):
        """Testa consistência entre templates e configurações."""
        # Verificar se todas as categorias definidas têm templates
        for category in CONTENT_CATEGORY_CONFIGS.keys():
            templates = template_generator.get_templates_by_category(category)
            assert len(templates) > 0, f"Categoria {category} sem templates"
    
    def test_timing_config_consistency(self):
        """Testa consistência de configurações de timing."""
        # Verificar se todos os presets de timing estão nas categorias
        for category_config in CONTENT_CATEGORY_CONFIGS.values():
            timing_preset = category_config["timing_preset"]
            assert timing_preset in TIMING_PRESETS, f"Timing preset {timing_preset} não encontrado"


if __name__ == "__main__":
    # Executar testes básicos
    print("=== Executando Testes de Plataforma de Vídeo ===")
    
    # Teste de configuração
    print("\n1. Testando configuração de plataformas...")
    config_test = TestVideoPlatformConfig()
    config_test.test_init_platform_configs()
    config_test.test_content_category_configs()
    print("✅ Configurações funcionando")
    
    # Teste de templates
    print("\n2. Testando templates visuais...")
    template_test = TestVisualTemplateGenerator()
    template_test.test_init_templates()
    template_test.test_get_template_by_category_and_type()
    template_test.test_get_color_palette()
    print("✅ Templates funcionando")
    
    # Teste de otimizador
    print("\n3. Testando otimizador...")
    optimizer_test = TestPlatformOptimizer()
    optimizer_test.test_adjust_timing()
    print("✅ Otimizador funcionando")
    
    print("\n=== Todos os testes passaram! ===")