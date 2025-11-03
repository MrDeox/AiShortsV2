"""
Demonstração do Sistema de Processamento Automático de Vídeos
Demo Automatic Video Processing System

Este script demonstra o uso completo do sistema de processamento automático
para converter vídeos para qualidade profissional 1080x1920 (vertical).
"""

import os
import sys
import logging
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.video.processing.automatic_video_processor import AutomaticVideoProcessor
from src.video.processing.video_quality_analyzer import VideoQualityAnalyzer


def setup_logging():
    """Configura sistema de logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('video_processing_demo.log', encoding='utf-8')
        ]
    )


def create_test_video():
    """Cria um vídeo de teste simples."""
    try:
        import numpy as np
        from moviepy.editor import ImageClip, ColorClip, concatenate_videoclips
        import tempfile
        
        print("Criando vídeo de teste...")
        
        # Criar clip colorido simples
        color_clip = ColorClip(size=(1920, 1080), color=(50, 100, 150), duration=10)
        color_clip = color_clip.set_fps(30)
        
        # Adicionar texto simples (se disponível)
        try:
            from moviepy.editor import TextClip
            text_clip = TextClip("Demo AI Shorts", fontsize=70, color='white')
            text_clip = text_clip.set_duration(10).set_position('center')
            final_clip = concatenate_videoclips([color_clip, color_clip])
        except:
            final_clip = color_clip
        
        # Salvar vídeo de teste
        test_video_path = "/tmp/demo_test_video.mp4"
        final_clip.write_videofile(
            test_video_path,
            fps=30,
            codec='libx264',
            audio_codec='aac'
        )
        
        color_clip.close()
        final_clip.close()
        
        print(f"Vídeo de teste criado: {test_video_path}")
        return test_video_path
        
    except Exception as e:
        print(f"Erro ao criar vídeo de teste: {e}")
        return None


def demo_video_processing():
    """Demonstra o processamento automático de vídeos."""
    print("\n" + "="*60)
    print("DEMONSTRAÇÃO DO PROCESSAMENTO AUTOMÁTICO DE VÍDEOS")
    print("="*60)
    
    # Inicializar componentes
    processor = AutomaticVideoProcessor()
    analyzer = VideoQualityAnalyzer()
    
    # Criar ou usar vídeo de teste
    test_video = create_test_video()
    
    if not test_video or not os.path.exists(test_video):
        print("❌ Não foi possível criar vídeo de teste. Pulando demonstração.")
        return
    
    try:
        print(f"\n📹 Vídeo de teste: {test_video}")
        
        # 1. Análise inicial
        print("\n🔍 1. ANALISANDO QUALIDADE INICIAL...")
        initial_quality = analyzer.analyze_video_quality(test_video)
        print(f"   • Qualidade inicial: {initial_quality.overall_score:.1f}/100")
        print(f"   • Brilho: {initial_quality.brightness:.2f}")
        print(f"   • Nitidez: {initial_quality.sharpness:.2f}")
        print(f"   • Movimento: {initial_quality.motion_level:.2f}")
        
        # 2. Verificar compatibilidade com plataformas
        print("\n🌐 2. VERIFICANDO COMPATIBILIDADE COM PLATAFORMAS...")
        platforms = ['tiktok', 'instagram_reels', 'youtube_shorts']
        for platform in platforms:
            try:
                compatibility = analyzer.check_platform_compatibility(test_video, platform)
                score = compatibility.get('overall_compatibility', 0)
                status = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
                print(f"   {status} {platform.title()}: {score:.1f}% compatível")
            except Exception as e:
                print(f"   ❌ {platform.title()}: Erro na análise")
        
        # 3. Converter para formato vertical
        print("\n📱 3. CONVERTENDO PARA FORMATO VERTICAL (1080x1920)...")
        vertical_video = processor.normalize_to_vertical(test_video)
        
        if vertical_video and os.path.exists(vertical_video):
            print(f"   ✅ Vídeo vertical criado: {vertical_video}")
            
            # Verificar qualidade do vídeo vertical
            vertical_quality = analyzer.analyze_video_quality(vertical_video)
            print(f"   • Nova qualidade: {vertical_quality.overall_score:.1f}/100")
            print(f"   • Melhoria: +{vertical_quality.overall_score - initial_quality.overall_score:.1f}")
        else:
            print("   ❌ Falha na conversão vertical")
            return
        
        # 4. Melhorar qualidade
        print("\n🎨 4. APLICANDO MELHORIAS DE QUALIDADE...")
        enhanced_video = processor.enhance_quality(vertical_video)
        
        if enhanced_video and os.path.exists(enhanced_video):
            print(f"   ✅ Vídeo melhorado criado: {enhanced_video}")
            
            # Verificar qualidade final
            final_quality = analyzer.analyze_video_quality(enhanced_video)
            print(f"   • Qualidade final: {final_quality.overall_score:.1f}/100")
            print(f"   • Melhoria total: +{final_quality.overall_score - initial_quality.overall_score:.1f}")
        else:
            print("   ❌ Falha na melhoria de qualidade")
            return
        
        # 5. Processar segmento específico
        print("\n✂️ 5. PROCESSANDO SEGMENTO ESPECÍFICO (10-20s)...")
        segment_video = processor.process_video_segment(
            enhanced_video, 
            target_duration=10.0, 
            start_time=10.0
        )
        
        if segment_video and os.path.exists(segment_video):
            print(f"   ✅ Segmento processado: {segment_video}")
            
            segment_quality = analyzer.analyze_video_quality(segment_video)
            print(f"   • Qualidade do segmento: {segment_quality.overall_score:.1f}/100")
        else:
            print("   ❌ Falha no processamento de segmento")
        
        # 6. Extrair frames para análise
        print("\n🖼️ 6. EXTRAINDO FRAMES PARA ANÁLISE...")
        frames = processor.extract_frames_for_analysis(enhanced_video, num_frames=3)
        
        if frames:
            print(f"   ✅ {len(frames)} frames extraídos:")
            for i, frame_path in enumerate(frames):
                print(f"      • Frame {i+1}: {os.path.basename(frame_path)}")
        else:
            print("   ❌ Falha na extração de frames")
        
        # 7. Gerar relatório completo
        print("\n📊 7. GERANDO RELATÓRIO COMPLETO...")
        report_path = "/tmp/video_quality_report.json"
        
        success = analyzer.generate_quality_report(enhanced_video, report_path)
        if success:
            print(f"   ✅ Relatório gerado: {report_path}")
        else:
            print("   ❌ Falha na geração do relatório")
        
        # 8. Sugerir melhorias
        print("\n💡 8. GERANDO SUGESTÕES DE MELHORIA...")
        suggestions = analyzer.suggest_improvements(enhanced_video)
        
        if suggestions and 'suggestions' in suggestions:
            quality_improvements = suggestions['suggestions'].get('quality_improvements', [])
            if quality_improvements:
                print("   🔧 Sugestões de qualidade:")
                for suggestion in quality_improvements[:3]:  # Mostrar apenas 3
                    print(f"      • {suggestion['suggestion']} (Impacto: {suggestion['impact']})")
            else:
                print("   ✅ Nenhuma melhoria de qualidade necessária")
        
        # 9. Estatísticas de processamento
        print("\n📈 9. ESTATÍSTICAS DE PROCESSAMENTO...")
        stats = processor.get_processing_stats()
        print(f"   • Vídeos processados: {stats['processed_videos']}")
        print(f"   • Vídeos em cache: {stats['cached_videos']}")
        print(f"   • Taxa de acerto do cache: {stats['cache_hit_rate']:.1f}%")
        print(f"   • Tempo médio de processamento: {stats['average_processing_time']:.2f}s")
        print(f"   • Taxa de processamento: {stats['processing_rate_videos_per_hour']:.1f} vídeos/hora")
        
        # 10. Verificar compatibilidade final
        print("\n✅ 10. VERIFICAÇÃO FINAL DE COMPATIBILIDADE...")
        for platform in platforms:
            try:
                final_compatibility = analyzer.check_platform_compatibility(enhanced_video, platform)
                final_score = final_compatibility.get('overall_compatibility', 0)
                status = "✅" if final_score >= 90 else "✅" if final_score >= 70 else "⚠️" if final_score >= 50 else "❌"
                print(f"   {status} {platform.title()}: {final_score:.1f}% compatível")
            except Exception as e:
                print(f"   ❌ {platform.title()}: Erro na verificação")
        
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"\n📁 Arquivos gerados:")
        print(f"   • Vídeo vertical: {vertical_video}")
        print(f"   • Vídeo melhorado: {enhanced_video}")
        if segment_video:
            print(f"   • Segmento processado: {segment_video}")
        print(f"   • Relatório: {report_path}")
        if frames:
            print(f"   • Frames: {len(frames)} arquivos em {processor.cache_dir}")
        
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        logging.error(f"Erro na demonstração: {e}", exc_info=True)


def demo_batch_processing():
    """Demonstra processamento em lote."""
    print("\n" + "="*60)
    print("DEMONSTRAÇÃO DE PROCESSAMENTO EM LOTE")
    print("="*60)
    
    processor = AutomaticVideoProcessor()
    analyzer = VideoQualityAnalyzer()
    
    # Criar múltiplos vídeos de teste
    test_videos = []
    for i in range(3):
        video_path = create_test_video()
        if video_path:
            test_videos.append(video_path)
    
    if len(test_videos) < 2:
        print("❌ Não foi possível criar vídeos suficientes para demonstração em lote.")
        return
    
    try:
        print(f"\n🔄 Processando {len(test_videos)} vídeos em lote...")
        
        # Batch processing
        batch_results = processor.batch_process_videos(
            test_videos, 
            operations=['normalize_to_vertical', 'enhance_quality']
        )
        
        # Analisar resultados
        successful = sum(1 for result in batch_results.values() if result is not None)
        print(f"   ✅ Processados com sucesso: {successful}/{len(test_videos)}")
        
        # Análise de qualidade em lote
        print(f"\n🔍 Analisando qualidade dos vídeos processados...")
        batch_analysis = analyzer.batch_analyze_quality(
            [result for result in batch_results.values() if result is not None]
        )
        
        if 'overall_statistics' in batch_analysis:
            stats = batch_analysis['overall_statistics']
            print(f"   • Qualidade média: {stats['average_quality_score']:.1f}/100")
            print(f"   • Potencial de melhoria: {stats['improvement_potential']:.1f}%")
        
        print("\n🎉 PROCESSAMENTO EM LOTE CONCLUÍDO!")
        
    except Exception as e:
        print(f"\n❌ Erro no processamento em lote: {e}")


def demo_platform_optimization():
    """Demonstra otimização específica para plataformas."""
    print("\n" + "="*60)
    print("DEMONSTRAÇÃO DE OTIMIZAÇÃO PARA PLATAFORMAS")
    print("="*60)
    
    analyzer = VideoQualityAnalyzer()
    
    test_video = create_test_video()
    if not test_video:
        return
    
    platforms = {
        'tiktok': 'TikTok',
        'instagram_reels': 'Instagram Reels', 
        'youtube_shorts': 'YouTube Shorts',
        'facebook_reels': 'Facebook Reels'
    }
    
    print(f"\n🎯 Testando compatibilidade com {len(platforms)} plataformas...")
    
    for platform_key, platform_name in platforms.items():
        try:
            compatibility = analyzer.check_platform_compatibility(test_video, platform_key)
            score = compatibility.get('overall_compatibility', 0)
            
            print(f"\n📱 {platform_name}:")
            print(f"   • Compatibilidade geral: {score:.1f}%")
            
            checks = compatibility.get('compatibility_checks', {})
            for check, result in checks.items():
                status = "✅" if result else "❌"
                check_name = check.replace('_ok', '').replace('_', ' ').title()
                print(f"     {status} {check_name}")
            
            if score >= 90:
                print(f"   🎉 Otimizado para {platform_name}!")
            elif score >= 70:
                print(f"   ⚡ Pequenos ajustes necessários para {platform_name}")
            else:
                print(f"   🔧 Melhorias significativas necessárias para {platform_name}")
                
        except Exception as e:
            print(f"   ❌ Erro ao analisar {platform_name}: {e}")


def main():
    """Função principal da demonstração."""
    print("🚀 DEMONSTRAÇÃO DO SISTEMA DE PROCESSAMENTO AUTOMÁTICO DE VÍDEOS")
    print("=" * 80)
    print("Este sistema converte vídeos para qualidade profissional 1080x1920")
    print("com análise automática de qualidade e otimização para plataformas.")
    print("=" * 80)
    
    # Configurar logging
    setup_logging()
    
    try:
        # Demonstrações principais
        demo_video_processing()
        
        # Demonstrações avançadas
        demo_batch_processing()
        demo_platform_optimization()
        
        print("\n" + "="*80)
        print("🎊 TODAS AS DEMONSTRAÇÕES CONCLUÍDAS COM SUCESSO!")
        print("="*80)
        print("\n💡 O sistema está pronto para uso em produção!")
        print("📚 Consulte os arquivos gerados para ver os resultados detalhados.")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demonstração interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        logging.error(f"Erro inesperado: {e}", exc_info=True)


if __name__ == "__main__":
    main()