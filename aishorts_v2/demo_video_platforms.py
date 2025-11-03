"""
Demonstração das configurações de plataforma de vídeo

Este script mostra como usar as configurações específicas para cada plataforma
e gerar templates visuais.
"""

import sys
import os
sys.path.append('/workspace/aishorts_v2')

from aishorts_v2.src.config.video_platforms import (
    Platform, VideoPlatformConfig, video_config, get_category_config, get_timing_preset
)
from aishorts_v2.src.video.generators.visual_templates import (
    template_generator, TemplateType, get_template, generate_text_overlay
)
from aishorts_v2.src.video.processing.platform_optimizer import PlatformOptimizer

def demo_platform_configurations():
    """Demonstra configurações de plataforma."""
    print("=== Configurações de Plataforma de Vídeo ===\n")
    
    # Mostrar especificações de cada plataforma
    for platform in Platform:
        specs = video_config.get_platform_specs(platform)
        print(f"📱 {specs.name}")
        print(f"   Resolução: {specs.resolution_str}")
        print(f"   Aspect Ratio: {specs.aspect_ratio}")
        print(f"   Duração: {specs.duration_min}s - {specs.duration_max}s")
        print(f"   FPS: {specs.fps}")
        print(f"   Formato: {specs.format.value.upper()}")
        print(f"   Codec Vídeo: {specs.video_codec.value}")
        print(f"   Codec Áudio: {specs.audio_codec.value}")
        print(f"   Tamanho Máximo: {specs.file_size_max_mb}MB")
        print()
    
    # Mostrar presets de qualidade
    print("🎨 Presets de Qualidade:")
    for preset in video_config.quality_presets:
        print(f"   {preset.name}: {preset.bitrate_kbps}kbps - {preset.use_case}")
    print()
    
    # Mostrar zonas seguras
    print("🛡️ Zonas Seguras:")
    for platform in Platform:
        safe_zone = video_config.get_safe_zone(platform)
        print(f"   {platform.value.title()}:")
        print(f"     Margem superior: {safe_zone['top_margin_pct']}%")
        print(f"     Margem inferior: {safe_zone['bottom_margin_pct']}%")
        print(f"     Margens laterais: {safe_zone['side_margin_pct']}%")
    print()

def demo_category_configs():
    """Demonstra configurações de categoria."""
    print("=== Configurações de Categoria ===\n")
    
    categories = ["SPACE", "ANIMALS", "SCIENCE", "HISTORY", "NATURE"]
    
    for category in categories:
        config = get_category_config(category)
        print(f"🌟 {category}")
        print(f"   Efeitos de Transição: {', '.join(config['transition_effects'])}")
        print(f"   Estilo de Texto: {config['text_overlay_style']}")
        print(f"   Paleta de Cores: {', '.join(config['color_palette'])}")
        print(f"   Timing: {config['timing_preset']}")
        
        # Mostrar timing preset
        timing = get_timing_preset(config['timing_preset'])
        print(f"   Timing Detalhado:")
        print(f"     Hook: {timing['hook_duration']}s")
        print(f"     Entrega: {' + '.join(map(str, timing['value_delivery_segments']))}s")
        print(f"     Conclusão: {timing['conclusion_duration']}s")
        print()

def demo_visual_templates():
    """Demonstra templates visuais."""
    print("=== Templates Visuais ===\n")
    
    # Mostrar templates por categoria
    for category in ["SPACE", "ANIMALS", "SCIENCE"]:
        templates = template_generator.get_templates_by_category(category)
        print(f"📋 {category} ({len(templates)} templates)")
        
        for template in templates:
            print(f"   - {template.name}: {template.template_type.value}")
            if template.text_overlays:
                overlay = template.text_overlays[0]
                print(f"     Texto: '{overlay.text}' (será definido dinamicamente)")
                print(f"     Posição: {overlay.position}, Cor: {overlay.color}")
        print()
    
    # Demonstração de geração de texto
    print("✏️ Geração de Texto Personalizado:")
    overlay = generate_text_overlay("Planetas Fascinantes", "SPACE", "top")
    print(f"   Texto: '{overlay.text}'")
    print(f"   Categoria: SPACE, Posição: {overlay.position}")
    print(f"   Estilo: {overlay.style.value}, Cor: {overlay.color}")
    print()
    
    # Demonstração de paleta de cores
    print("🎨 Paletas de Cores:")
    for category in ["SPACE", "ANIMALS", "NATURE"]:
        palette = template_generator.get_color_palette(category)
        print(f"   {category}: {', '.join(palette[:3])}...")
    print()

def demo_platform_optimization():
    """Demonstra otimização de plataforma."""
    print("=== Otimização de Plataforma ===\n")
    
    # Criar otimizador
    optimizer = PlatformOptimizer()
    
    try:
        # Simular ajuste de timing
        print("🔧 Simulando Ajuste de Timing:")
        
        for platform in [Platform.TIKTOK, Platform.YOUTUBE_SHORTS, Platform.INSTAGRAM_REELS]:
            # Simular duração do vídeo
            specs = video_config.get_platform_specs(platform)
            print(f"   {specs.name}:")
            print(f"     Duração recomendada: {specs.duration_min}s - {specs.duration_max}s")
            print(f"     Resolução: {specs.resolution_str} @ {specs.fps}fps")
            
            # Validar duração de exemplo
            example_duration = 25  # 25 segundos
            is_valid = specs.validate_duration(example_duration)
            status = "✅ Válido" if is_valid else "❌ Inválido"
            print(f"     Vídeo de {example_duration}s: {status}")
        
        print()
        
        # Demonstração de sequência de templates
        print("📖 Sequência de Templates para História:")
        content = [
            "Você Sabia? Curiosidades Espaciais",
            "Júpiter tem mais de 80 luas confirmadas",
            "Saturno pode flutuar na água",
            "Aguarde mais fatos incríveis!"
        ]
        
        sequence = template_generator.create_sequence_template("SPACE", content, "educational")
        print(f"   Sequência criada com {len(sequence)} templates:")
        
        for i, template in enumerate(sequence, 1):
            template_info = f"{i}. {template.template_type.value}"
            if template.text_overlays and template.text_overlays[0].text:
                template_info += f" - '{template.text_overlays[0].text}'"
            print(f"     {template_info}")
        
    finally:
        optimizer.cleanup()

def demo_export_settings():
    """Demonstra configurações de exportação."""
    print("\n=== Configurações de Exportação ===\n")
    
    for platform in Platform:
        config = video_config.get_platform_config(platform)
        specs = config["specifications"]
        export = config["export_settings"]
        
        print(f"📤 {specs.name} - Configurações de Exportação:")
        print(f"   Container: {export['container'].upper()}")
        print(f"   Codec Vídeo: {export['video_codec'].upper()}")
        print(f"   Codec Áudio: {export['audio_codec'].upper()}")
        print(f"   Resolução: {export['resolution']}")
        print(f"   FPS: {export['fps']}")
        print(f"   Bitrate: {export['bitrate']}")
        print(f"   Aspect Ratio: {export['aspect_ratio']}")
        print()

def main():
    """Função principal de demonstração."""
    print("🚀 AiShorts v2.0 - Demonstração de Configurações de Vídeo\n")
    
    demo_platform_configurations()
    demo_category_configs()
    demo_visual_templates()
    demo_platform_optimization()
    demo_export_settings()
    
    print("="*60)
    print("✅ Demonstração concluída!")
    print("📝 Use estas configurações para otimizar seus vídeos.")
    print("🔧 Consulte a documentação para implementação completa.")

if __name__ == "__main__":
    main()