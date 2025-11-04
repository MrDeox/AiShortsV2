"""
Demo de Sincronização Áudio-Vídeo para AiShorts v2.0
Demonstra o uso completo do sistema de sincronização TTS-vídeo
"""

import os
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.video.sync import AudioVideoSynchronizer, TimingOptimizer
from src.tts.kokoro_tts import KokoroTTSClient
from src.models.script_models import Script, ScriptSection, Theme
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AudioVideoSyncDemo:
    """
    Classe demo para demonstrar sincronização áudio-vídeo
    """
    
    def __init__(self):
        """Inicializa demo com cliente TTS e sincronizador"""
        self.tts_client = KokoroTTSClient()
        self.synchronizer = AudioVideoSynchronizer()
        self.optimizer = TimingOptimizer()
        
        # Diretórios de saída
        self.output_dir = Path("outputs/video/sync_demo")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("AudioVideoSyncDemo inicializado")
    
    def create_sample_script(self) -> Script:
        """Cria script de exemplo para demo"""
        
        # Criar tema
        theme = Theme(
            main_title="Fatos Incríveis sobre Golfinhos",
            category="educacao",
            keywords=["golfinhos", "ocean", "fatos", "curiosidades"]
        )
        
        # Criar seções do script
        sections = [
            ScriptSection(
                type="hook",
                content="Você sabia que golfinhos têm nomes próprios? É verdade! Cada golfinho desenvolve um assobio único que funciona como seu nome.",
                order=1
            ),
            ScriptSection(
                type="development", 
                content="Os golfinhos usam esses 'nomes' para se chamarem através das águas do oceano. Cientistas descobriram que eles podem se lembrar desses assobios por mais de 20 anos!",
                order=2
            ),
            ScriptSection(
                type="development",
                content="Além disso, golfinhos têm culturas próprias! Diferentes grupos ensinaunsuários comportamentos únicos para suas crias, passando conhecimento de geração em geração.",
                order=3
            ),
            ScriptSection(
                type="conclusion",
                content="Os golfinhos continuam nos surpreendendo com sua inteligência. Esses magnificos морські ссавці são muito mais complexos do que imaginávamos!",
                order=4
            )
        ]
        
        # Criar script completo
        script = Script(
            id="demo_golfinhos_script",
            theme=theme,
            sections=sections,
            estimated_duration=45.0
        )
        
        return script
    
    def create_sample_video_segments(self) -> list:
        """Cria segmentos de vídeo de exemplo para demo"""
        
        video_segments = [
            {
                'video_path': 'outputs/video/segment1_golfinhos.mp4',
                'start_time': 0.0,
                'duration': 10.0,
                'description': 'Golfinhos nadando em alto mar',
                'transition_in': 'fade',
                'transition_out': 'slide_right'
            },
            {
                'video_path': 'outputs/video/segment2_comunicacao.mp4', 
                'start_time': 10.0,
                'duration': 12.0,
                'description': 'Golfinhos se comunicando',
                'transition_in': 'slide_left',
                'transition_out': 'zoom_in'
            },
            {
                'video_path': 'outputs/video/segment3_cultura.mp4',
                'start_time': 22.0,
                'duration': 11.0,
                'description': 'Golfinhos ensinando filhotes',
                'transition_in': 'zoom_out', 
                'transition_out': 'cross_dissolve'
            },
            {
                'video_path': 'outputs/video/segment4_conclusao.mp4',
                'start_time': 33.0,
                'duration': 12.0,
                'description': 'Golfinhos em美丽的海洋景观',
                'transition_in': 'fade_in',
                'transition_out': 'fade_out'
            }
        ]
        
        return video_segments
    
    def demo_complete_sync(self):
        """Demonstração completa do sistema de sincronização"""
        try:
            logger.info("🎬 Iniciando demo completa de sincronização áudio-vídeo")
            
            # 1. Criar script de exemplo
            logger.info("📝 Criando script de exemplo...")
            script = self.create_sample_script()
            
            # 2. Gerar áudio TTS
            logger.info("🗣️ Gerando narração TTS...")
            tts_result = self.tts_client.script_to_audio(
                script, 
                output_prefix="demo_golfinhos",
                voice="af_diamond"
            )
            
            if not tts_result:
                logger.error("❌ Falha na geração de áudio TTS")
                return
            
            # Salvar script timing
            script_timing_path = self.output_dir / "script_timing.json"
            import json
            with open(script_timing_path, 'w', encoding='utf-8') as f:
                json.dump(tts_result, f, ensure_ascii=False, indent=2)
            
            # 3. Criar segmentos de vídeo de exemplo
            logger.info("🎥 Criando segmentos de vídeo...")
            video_segments = self.create_sample_video_segments()
            
            # 4. Sincronizar áudio com vídeo
            logger.info("⚡ Sincronizando áudio com vídeo...")
            sync_result = self.synchronizer.sync_audio_with_video(
                audio_path=tts_result['full_audio']['audio_path'],
                video_segments=video_segments,
                script_timing=tts_result
            )
            
            # 5. Otimizar transições
            logger.info("🎨 Otimizando transições...")
            optimization_result = self.optimizer.optimize_transitions(
                video_segments=video_segments,
                audio_timing=tts_result
            )
            
            # 6. Adicionar efeitos de transição
            logger.info("✨ Adicionando efeitos de transição...")
            effects_result = self.optimizer.add_transition_effects(video_segments)
            
            # 7. Calcular durações otimizadas para segmentos
            logger.info("⏱️ Calculando durações otimizadas...")
            duration_results = []
            for section in script.sections:
                duration_opt = self.optimizer.calculate_optimal_duration(
                    segment_text=section.content,
                    video_length=tts_result['total_duration']
                )
                duration_results.append(duration_opt)
            
            # 8. Gerar relatório final
            logger.info("📊 Gerando relatório final...")
            final_report = self.generate_final_report(
                tts_result=tts_result,
                sync_result=sync_result,
                optimization_result=optimization_result,
                effects_result=effects_result,
                duration_results=duration_results
            )
            
            # Salvar relatório
            report_path = self.output_dir / "relatorio_sincronizacao.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(final_report)
            
            logger.info("✅ Demo concluída com sucesso!")
            logger.info(f"📁 Resultados salvos em: {self.output_dir}")
            
            return {
                'success': True,
                'tts_result': tts_result,
                'sync_result': sync_result,
                'optimization_result': optimization_result,
                'effects_result': effects_result,
                'duration_results': duration_results,
                'report_path': str(report_path)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na demo completa: {e}")
            return {'success': False, 'error': str(e)}
    
    def demo_beat_detection(self):
        """Demonstração específica de detecção de beats"""
        try:
            logger.info("🎵 Iniciando demo de detecção de beats")
            
            # Criar áudio simples para teste
            test_text = "Beat detection é essencial para sincronização perfeita!"
            audio_result = self.tts_client.text_to_speech(
                test_text, 
                output_filename="beat_test"
            )
            
            if audio_result['success']:
                # Detectar beats
                beat_points = self.synchronizer.detect_beat_points(
                    audio_result['audio_path']
                )
                
                logger.info(f"🎼 Detectados {len(beat_points)} pontos de sincronização:")
                for i, point in enumerate(beat_points[:10]):  # Mostrar apenas os primeiros 10
                    logger.info(f"  Beat {i+1}: {point:.2f}s")
                
                return {
                    'success': True,
                    'audio_path': audio_result['audio_path'],
                    'beat_points': beat_points,
                    'total_beats': len(beat_points)
                }
            
        except Exception as e:
            logger.error(f"❌ Erro na demo de beats: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_final_report(self, 
                            tts_result: dict,
                            sync_result: dict,
                            optimization_result: dict,
                            effects_result: dict,
                            duration_results: list) -> str:
        """Gera relatório final da demo"""
        
        report = f"""# 🎬 Relatório de Sincronização Áudio-Vídeo - AiShorts v2.0

## 📊 Resumo Executivo

### Sistema TTS
- **Áudio gerado**: {tts_result.get('sections_count', 0)} seções
- **Duração total**: {tts_result.get('total_duration', 0):.1f} segundos
- **Voz utilizada**: {tts_result.get('voice_info', {}).get('name', 'N/A')}
- **Arquivo completo**: {tts_result.get('full_audio', {}).get('audio_path', 'N/A')}

### Sincronização
- **Status**: {'✅ Sucesso' if sync_result.get('success') else '❌ Falha'}
- **Segmentos sincronizados**: {sync_result.get('segments_count', 0)}
- **Pontos de beat detectados**: {len(sync_result.get('beat_points', []))}
- **Duração do vídeo final**: {sync_result.get('total_duration', 0):.1f} segundos

### Otimização de Transições
- **Status**: {'✅ Otimizado' if optimization_result.get('success') else '❌ Falha'}
- **Pontos de transição**: {len(optimization_result.get('transition_points', []))}
- **Score de suavidade**: {optimization_result.get('improvements', {}).get('smoothness_score', 0):.2f}
- **Predição de engajamento**: {optimization_result.get('improvements', {}).get('engagement_prediction', 0):.2f}

### Efeitos Aplicados
- **Efeitos de transição**: {effects_result.get('total_effects', 0)}
- **Variedade de efeitos**: {effects_result.get('effect_statistics', {}).get('unique_effects', 0)}
- **Duração média**: {effects_result.get('effect_statistics', {}).get('avg_duration', 0):.2f}s

## 📈 Análise Detalhada

### Análise de Beats
"""
        
        if sync_result.get('beat_points'):
            report += f"""
**Pontos de sincronização detectados**: {len(sync_result['beat_points'])}

```
"""
            for i, beat in enumerate(sync_result['beat_points'][:15]):  # Primeiros 15 beats
                report += f"Beat {i+1:2d}: {beat:6.2f}s\n"
            
            if len(sync_result['beat_points']) > 15:
                report += f"... e mais {len(sync_result['beat_points']) - 15} beats\n"
            
            report += "```\n"
        
        report += "\n### Durações Otimizadas por Seção\n\n"
        
        for i, (section, duration_result) in enumerate(zip(
            ['Hook', 'Desenvolvimento 1', 'Desenvolvimento 2', 'Conclusão'],
            duration_results
        )):
            if duration_result.get('success'):
                report += f"**{section}**: {duration_result['final_duration']:.1f}s\n"
                report += f"- Palavras: {duration_result['text_analysis']['word_count']}\n"
                report += f"- Tipo: {duration_result['text_analysis']['content_type']}\n"
                report += f"- Precisão: {duration_result['sync_precision']:.2f}\n\n"
        
        report += """## 🎯 Recomendações

### Para Máxima Qualidade:
1. **Sincronização**: Utilize os pontos de beat detectados para timing preciso
2. **Transições**: Aplique os efeitos otimizados para transições suaves
3. **Duração**: Mantenha cada segmento entre 3-15 segundos para engajamento ideal
4. **Áudio**: Use velocidade de fala consistente (2.5 palavras/segundo)

### Para Plataformas Específicas:
- **TikTok/Shorts**: Máximo 60s, idealmente 45s
- **Instagram Reels**: Máximo 90s, idealmente 60s  
- **YouTube Shorts**: Máximo 60s, idealmente 45s

## 📁 Arquivos Gerados

### Áudio TTS:
"""
        
        if tts_result.get('output_files'):
            report += f"- Áudio completo: `{tts_result['output_files']['complete']}`\n"
            for section_file in tts_result['output_files'].get('sections', []):
                report += f"- Seção: `{section_file}`\n"
        
        if sync_result.get('synchronized_video'):
            report += f"\n### Vídeo Sincronizado:\n"
            report += f"- Arquivo final: `{sync_result['synchronized_video'].get('output_path', 'N/A')}`\n"
            report += f"- Duração: {sync_result['synchronized_video'].get('duration', 0):.1f}s\n"
        
        report += f"""
### Dados Técnicos:
- Script timing: `script_timing.json`
- Pontos de beat: {len(sync_result.get('beat_points', []))} detectadas
- Segmentos otimizados: {sync_result.get('segments_count', 0)}

---
*Gerado pelo Sistema AiShorts v2.0 - Módulo de Sincronização Áudio-Vídeo*
*Data: {self.get_timestamp()}*
"""
        
        return report
    
    def get_timestamp(self):
        """Retorna timestamp atual"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Função principal da demo"""
    print("🎬 DEMO: SISTEMA DE SINCRONIZAÇÃO ÁUDIO-VÍDEO")
    print("=" * 60)
    
    # Inicializar demo
    demo = AudioVideoSyncDemo()
    
    # Executar demo de beats primeiro (mais rápido)
    print("\n🎵 Demo 1: Detecção de Beats")
    beat_result = demo.demo_beat_detection()
    
    if beat_result.get('success'):
        print(f"✅ Beats detectados: {beat_result['total_beats']}")
    else:
        print(f"❌ Erro: {beat_result.get('error')}")
    
    # Executar demo completa
    print("\n🎬 Demo 2: Sincronização Completa")
    print("(⚠️ Esta demo pode levar alguns minutos...)")
    
    complete_result = demo.demo_complete_sync()
    
    if complete_result.get('success'):
        print("✅ Sincronização concluída com sucesso!")
        print(f"📁 Relatório salvo em: {complete_result['report_path']}")
        
        # Mostrar estatísticas finais
        sync_result = complete_result['sync_result']
        print(f"\n📊 Estatísticas:")
        print(f"  - Segmentos: {sync_result.get('segments_count', 0)}")
        print(f"  - Duração: {sync_result.get('total_duration', 0):.1f}s")
        print(f"  - Beats: {len(sync_result.get('beat_points', []))}")
    else:
        print(f"❌ Erro na sincronização: {complete_result.get('error')}")
    
    print("\n🎉 Demo finalizada!")
    print(f"📁 Verifique os resultados em: {demo.output_dir}")


if __name__ == "__main__":
    main()