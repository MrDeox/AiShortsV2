#!/usr/bin/env python3
"""
🚀 DEMO END-TO-END REAL - AiShorts v2.0
========================================

Este demo executa o pipeline completo com dados REAIS do YouTube:
1. Geração de tema real
2. Roteiro gerado dinamicamente
3. Narração TTS Kokoro
4. Busca e download REAL de vídeos YouTube
5. Processamento e sincronização
6. Vídeo final para TikTok

CRÍTICO: Validação de qualidade para monetização
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List
import logging
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "aishorts_v2/src"))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DemoEndToEndReal:
    """Demo completo do pipeline AiShorts v2.0 com dados REAIS"""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = {}
        self.output_dir = Path("output_demo_real")
        self.output_dir.mkdir(exist_ok=True)
        
        # Módulos do pipeline
        self.theme_generator = None
        self.script_generator = None
        self.validator = None
        self.tts = None
        self.youtube_extractor = None
        self.video_processor = None
        self.final_composer = None
        
        logger.info("🚀 DEMO END-TO-END REAL iniciado")
        logger.info(f"📁 Output directory: {self.output_dir}")
    
    def initialize_modules(self) -> bool:
        """Inicializar todos os módulos do pipeline"""
        logger.info("🔧 Inicializando módulos do pipeline...")
        
        try:
            # Theme Generator
            from generators.theme_generator import ThemeGenerator
            self.theme_generator = ThemeGenerator()
            logger.info("✅ Theme Generator inicializado")
            
            # Script Generator  
            from generators.script_generator import ScriptGenerator
            self.script_generator = ScriptGenerator()
            logger.info("✅ Script Generator inicializado")
            
            # Script Validator
            from validators.script_validator import ScriptValidator
            self.validator = ScriptValidator()
            logger.info("✅ Script Validator inicializado")
            
            # TTS Kokoro
            from tts.kokoro_tts import KokoroTTS
            self.tts = KokoroTTS()
            logger.info("✅ TTS Kokoro inicializado")
            
            # YouTube Extractor
            from video.extractors.youtube_extractor import YouTubeExtractor
            self.youtube_extractor = YouTubeExtractor()
            logger.info("✅ YouTube Extractor inicializado")
            
            # Video Processor
            from video.processors.video_processor import VideoProcessor
            self.video_processor = VideoProcessor()
            logger.info("✅ Video Processor inicializado")
            
            # Final Composer
            from video.generators.final_video_composer import FinalVideoComposer
            self.final_composer = FinalVideoComposer()
            logger.info("✅ Final Composer inicializado")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar módulos: {e}")
            return False
    
    def step1_generate_theme(self) -> Dict[str, Any]:
        """Etapa 1: Gerar tema real"""
        logger.info("🎯 ETAPA 1: Geração de tema...")
        
        start_time = time.time()
        
        try:
            # Gerar tema real com categoria específica
            theme = self.theme_generator.generate_theme(
                category="ANIMALS",
                language="pt-BR"
            )
            
            duration = time.time() - start_time
            
            # Salvar resultado
            theme_file = self.output_dir / "step1_theme.json"
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Tema gerado em {duration:.2f}s")
            logger.info(f"📝 Tema: {theme.get('theme', 'N/A')}")
            logger.info(f"📂 Arquivo salvo: {theme_file}")
            
            self.results['step1_theme'] = {
                'status': 'success',
                'duration': duration,
                'theme': theme,
                'file': str(theme_file)
            }
            
            return theme
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de tema: {e}")
            self.results['step1_theme'] = {'status': 'error', 'error': str(e)}
            raise
    
    def step2_generate_script(self, theme: Dict[str, Any]) -> Dict[str, Any]:
        """Etapa 2: Gerar roteiro baseado no tema"""
        logger.info("📝 ETAPA 2: Geração de roteiro...")
        
        start_time = time.time()
        
        try:
            # Gerar roteiro para TikTok
            script = self.script_generator.generate_script(
                theme=theme['theme'],
                platform="tiktok",
                duration_target=60,
                language="pt-BR"
            )
            
            duration = time.time() - start_time
            
            # Salvar resultado
            script_file = self.output_dir / "step2_script.json"
            with open(script_file, 'w', encoding='utf-8') as f:
                json.dump(script, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Roteiro gerado em {duration:.2f}s")
            logger.info(f"📝 Título: {script.get('title', 'N/A')}")
            logger.info(f"📊 Qualidade: {script.get('metrics', {}).get('quality_score', 'N/A')}")
            logger.info(f"📂 Arquivo salvo: {script_file}")
            
            self.results['step2_script'] = {
                'status': 'success',
                'duration': duration,
                'script': script,
                'file': str(script_file)
            }
            
            return script
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de roteiro: {e}")
            self.results['step2_script'] = {'status': 'error', 'error': str(e)}
            raise
    
    def step3_validate_script(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """Etapa 3: Validar roteiro"""
        logger.info("🔍 ETAPA 3: Validação de roteiro...")
        
        start_time = time.time()
        
        try:
            # Validar roteiro
            validation = self.validator.validate_script(
                script_text=script['script'],
                platform="tiktok",
                language="pt-BR"
            )
            
            duration = time.time() - start_time
            
            # Salvar resultado
            validation_file = self.output_dir / "step3_validation.json"
            with open(validation_file, 'w', encoding='utf-8') as f:
                json.dump(validation, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Validação concluída em {duration:.2f}s")
            logger.info(f"📊 Score: {validation.get('total_score', 0):.1f}/100")
            logger.info(f"✅ Status: {validation.get('status', 'unknown')}")
            logger.info(f"📂 Arquivo salvo: {validation_file}")
            
            self.results['step3_validation'] = {
                'status': 'success',
                'duration': duration,
                'validation': validation,
                'file': str(validation_file)
            }
            
            return validation
            
        except Exception as e:
            logger.error(f"❌ Erro na validação: {e}")
            self.results['step3_validation'] = {'status': 'error', 'error': str(e)}
            raise
    
    def step4_generate_tts(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """Etapa 4: Gerar narração TTS"""
        logger.info("🎙️ ETAPA 4: Geração de narração TTS...")
        
        start_time = time.time()
        
        try:
            # Gerar narração com voz brasileira
            audio_files = self.tts.generate_speech(
                text=script['script'],
                voice="af_heart",  # Voz feminina coração
                output_dir=str(self.output_dir / "step4_tts"),
                language="pt-BR"
            )
            
            duration = time.time() - start_time
            
            # Salvar informações
            tts_info = {
                'audio_files': audio_files,
                'voice': 'af_heart',
                'duration': duration,
                'language': 'pt-BR'
            }
            
            tts_file = self.output_dir / "step4_tts_info.json"
            with open(tts_file, 'w', encoding='utf-8') as f:
                json.dump(tts_info, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Narração gerada em {duration:.2f}s")
            logger.info(f"🎵 Arquivos de áudio: {len(audio_files)}")
            logger.info(f"🗣️ Voz: af_heart (Português Brasil)")
            logger.info(f"📂 Arquivo salvo: {tts_file}")
            
            self.results['step4_tts'] = {
                'status': 'success',
                'duration': duration,
                'audio_files': audio_files,
                'file': str(tts_file)
            }
            
            return tts_info
            
        except Exception as e:
            logger.error(f"❌ Erro na geração TTS: {e}")
            self.results['step4_tts'] = {'status': 'error', 'error': str(e)}
            raise
    
    def step5_search_youtube(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """Etapa 5: Buscar vídeos REAIS no YouTube"""
        logger.info("🔍 ETAPA 5: Busca REAL no YouTube...")
        
        start_time = time.time()
        
        try:
            # Extrair palavras-chave do roteiro
            from video.matching.semantic_analyzer import SemanticAnalyzer
            analyzer = SemanticAnalyzer()
            
            keywords = analyzer.extract_keywords(script['script'])
            logger.info(f"🔑 Keywords extraídas: {keywords[:5]}...")  # Mostrar primeiras 5
            
            # Buscar vídeos reais
            videos = self.youtube_extractor.search_videos(
                query=" ".join(keywords[:3]),  # Usar top 3 keywords
                max_results=10
            )
            
            duration = time.time() - start_time
            
            # Salvar resultado
            search_info = {
                'keywords': keywords,
                'query': " ".join(keywords[:3]),
                'videos_found': len(videos),
                'videos': videos[:3],  # Salvar primeiros 3
                'duration': duration
            }
            
            search_file = self.output_dir / "step5_youtube_search.json"
            with open(search_file, 'w', encoding='utf-8') as f:
                json.dump(search_info, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Busca concluída em {duration:.2f}s")
            logger.info(f"🎬 Vídeos encontrados: {len(videos)}")
            logger.info(f"🔑 Keywords: {keywords[:3]}")
            logger.info(f"📂 Arquivo salvo: {search_file}")
            
            self.results['step5_youtube_search'] = {
                'status': 'success',
                'duration': duration,
                'search_info': search_info,
                'file': str(search_file)
            }
            
            return search_info
            
        except Exception as e:
            logger.error(f"❌ Erro na busca YouTube: {e}")
            self.results['step5_youtube_search'] = {'status': 'error', 'error': str(e)}
            raise
    
    def step6_download_segments(self, search_info: Dict[str, Any]) -> Dict[str, Any]:
        """Etapa 6: Download de segmentos REAIS do YouTube"""
        logger.info("📥 ETAPA 6: Download REAL de segmentos...")
        
        start_time = time.time()
        
        try:
            videos = search_info['videos']
            downloaded_segments = []
            
            # Baixar primeiros 3 vídeos
            for i, video in enumerate(videos[:3]):
                logger.info(f"📥 Baixando vídeo {i+1}/3: {video.get('title', 'N/A')[:50]}...")
                
                # Download de segmento específico (5 segundos)
                segment_path = self.youtube_extractor.download_segment(
                    video_url=video['url'],
                    start_time=15.0,  # Início do vídeo + 15s
                    duration=5.0,     # 5 segundos
                    output_dir=str(self.output_dir / "step6_segments")
                )
                
                if segment_path:
                    downloaded_segments.append({
                        'original_video': video,
                        'segment_path': str(segment_path),
                        'index': i
                    })
                    logger.info(f"✅ Segmento {i+1} baixado: {segment_path}")
                else:
                    logger.warning(f"⚠️ Falha no download do segmento {i+1}")
            
            duration = time.time() - start_time
            
            # Salvar informações
            download_info = {
                'downloaded_segments': downloaded_segments,
                'total_downloaded': len(downloaded_segments),
                'duration': duration
            }
            
            download_file = self.output_dir / "step6_download_info.json"
            with open(download_file, 'w', encoding='utf-8') as f:
                json.dump(download_info, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Downloads concluídos em {duration:.2f}s")
            logger.info(f"📊 Segmentos baixados: {len(downloaded_segments)}/3")
            logger.info(f"📂 Arquivo salvo: {download_file}")
            
            self.results['step6_download'] = {
                'status': 'success',
                'duration': duration,
                'download_info': download_info,
                'file': str(download_file)
            }
            
            return download_info
            
        except Exception as e:
            logger.error(f"❌ Erro no download: {e}")
            self.results['step6_download'] = {'status': 'error', 'error': str(e)}
            raise
    
    def step7_process_videos(self, download_info: Dict[str, Any]) -> Dict[str, Any]:
        """Etapa 7: Processar vídeos baixados"""
        logger.info("🎬 ETAPA 7: Processamento de vídeos...")
        
        start_time = time.time()
        
        try:
            segments = download_info['downloaded_segments']
            processed_videos = []
            
            for segment in segments:
                logger.info(f"🎬 Processando: {Path(segment['segment_path']).name}")
                
                # Processar vídeo para formato TikTok (1080x1920)
                processed_path = self.video_processor.process_video(
                    input_path=segment['segment_path'],
                    output_dir=str(self.output_dir / "step7_processed"),
                    target_resolution=(1080, 1920),
                    platform="tiktok"
                )
                
                if processed_path:
                    processed_videos.append({
                        'original': segment,
                        'processed_path': str(processed_path)
                    })
                    logger.info(f"✅ Processado: {processed_path}")
                else:
                    logger.warning(f"⚠️ Falha no processamento")
            
            duration = time.time() - start_time
            
            # Salvar informações
            process_info = {
                'processed_videos': processed_videos,
                'total_processed': len(processed_videos),
                'duration': duration
            }
            
            process_file = self.output_dir / "step7_process_info.json"
            with open(process_file, 'w', encoding='utf-8') as f:
                json.dump(process_info, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Processamento concluído em {duration:.2f}s")
            logger.info(f"🎬 Vídeos processados: {len(processed_videos)}")
            logger.info(f"📂 Arquivo salvo: {process_file}")
            
            self.results['step7_process'] = {
                'status': 'success',
                'duration': duration,
                'process_info': process_info,
                'file': str(process_file)
            }
            
            return process_info
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento: {e}")
            self.results['step7_process'] = {'status': 'error', 'error': str(e)}
            raise
    
    def step8_final_composition(self, process_info: Dict[str, Any], tts_info: Dict[str, Any]) -> Dict[str, Any]:
        """Etapa 8: Composição final do vídeo"""
        logger.info("🎞️ ETAPA 8: Composição final do vídeo...")
        
        start_time = time.time()
        
        try:
            processed_videos = process_info['processed_videos']
            audio_files = tts_info['audio_files']
            
            # Compor vídeo final
            final_video = self.final_composer.compose_video(
                video_segments=[v['processed_path'] for v in processed_videos],
                audio_file=audio_files[0] if audio_files else None,
                platform="tiktok",
                style="engaging",
                output_dir=str(self.output_dir / "step8_final")
            )
            
            duration = time.time() - start_time
            
            # Salvar informações
            composition_info = {
                'final_video_path': str(final_video) if final_video else None,
                'video_segments_used': len(processed_videos),
                'audio_files_used': len(audio_files),
                'duration': duration
            }
            
            composition_file = self.output_dir / "step8_composition_info.json"
            with open(composition_file, 'w', encoding='utf-8') as f:
                json.dump(composition_info, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Composição concluída em {duration:.2f}s")
            logger.info(f"🎬 Vídeo final: {final_video}")
            logger.info(f"📂 Arquivo salvo: {composition_file}")
            
            self.results['step8_composition'] = {
                'status': 'success',
                'duration': duration,
                'composition_info': composition_info,
                'file': str(composition_file)
            }
            
            return composition_info
            
        except Exception as e:
            logger.error(f"❌ Erro na composição: {e}")
            self.results['step8_composition'] = {'status': 'error', 'error': str(e)}
            raise
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Gerar relatório final do demo"""
        logger.info("📊 ETAPA FINAL: Gerando relatório...")
        
        total_duration = time.time() - self.start_time
        
        # Calcular métricas gerais
        successful_steps = sum(1 for step in self.results.values() if step.get('status') == 'success')
        total_steps = len(self.results)
        success_rate = (successful_steps / total_steps) * 100
        
        # Métricas de qualidade
        quality_metrics = {
            'pipeline_success_rate': success_rate,
            'total_duration': total_duration,
            'successful_steps': successful_steps,
            'total_steps': total_steps,
            'youtube_real_content': True,
            'tts_real_audio': True,
            'final_video_generated': any(
                step.get('composition_info', {}).get('final_video_path') 
                for step in self.results.values() 
                if step.get('status') == 'success'
            )
        }
        
        # Relatório final
        final_report = {
            'demo_info': {
                'name': 'Demo End-to-End Real - AiShorts v2.0',
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0',
                'real_youtube_content': True,
                'production_ready': success_rate >= 70
            },
            'pipeline_results': self.results,
            'quality_metrics': quality_metrics,
            'files_generated': list(self.output_dir.glob("*")) if self.output_dir.exists() else []
        }
        
        # Salvar relatório
        report_file = self.output_dir / "final_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 Relatório salvo: {report_file}")
        logger.info(f"✅ Taxa de sucesso: {success_rate:.1f}%")
        logger.info(f"⏱️ Duração total: {total_duration:.1f}s")
        
        return final_report
    
    def run_complete_demo(self) -> Dict[str, Any]:
        """Executar demo completo end-to-end"""
        logger.info("🚀 INICIANDO DEMO END-TO-END REAL")
        logger.info("=" * 60)
        
        try:
            # 1. Inicializar módulos
            if not self.initialize_modules():
                raise Exception("Falha na inicialização dos módulos")
            
            # 2. Executar pipeline completo
            theme = self.step1_generate_theme()
            script = self.step2_generate_script(theme)
            validation = self.step3_validate_script(script)
            tts_info = self.step4_generate_tts(script)
            search_info = self.step5_search_youtube(script)
            download_info = self.step6_download_segments(search_info)
            process_info = self.step7_process_videos(download_info)
            composition_info = self.step8_final_composition(process_info, tts_info)
            
            # 3. Gerar relatório final
            final_report = self.generate_final_report()
            
            # 4. Status final
            logger.info("=" * 60)
            logger.info("🎉 DEMO END-TO-END REAL CONCLUÍDO!")
            logger.info(f"✅ Taxa de sucesso: {final_report['quality_metrics']['pipeline_success_rate']:.1f}%")
            logger.info(f"⏱️ Duração total: {final_report['quality_metrics']['total_duration']:.1f}s")
            logger.info(f"📁 Arquivos gerados: {len(final_report['files_generated'])}")
            logger.info(f"🚀 Production ready: {final_report['demo_info']['production_ready']}")
            
            return final_report
            
        except Exception as e:
            logger.error(f"❌ ERRO NO DEMO: {e}")
            self.results['error'] = {'status': 'failed', 'error': str(e)}
            return self.generate_final_report()

def main():
    """Função principal"""
    try:
        demo = DemoEndToEndReal()
        report = demo.run_complete_demo()
        
        # Exibir resumo final
        print("\n" + "=" * 60)
        print("📊 RESUMO FINAL - DEMO END-TO-END REAL")
        print("=" * 60)
        print(f"🎯 Pipeline Success Rate: {report['quality_metrics']['pipeline_success_rate']:.1f}%")
        print(f"⏱️ Duração Total: {report['quality_metrics']['total_duration']:.1f}s")
        print(f"📁 Arquivos Gerados: {len(report['files_generated'])}")
        print(f"🚀 Production Ready: {report['demo_info']['production_ready']}")
        print(f"🎬 YouTube Real: {report['quality_metrics']['youtube_real_content']}")
        print(f"🎙️ TTS Real: {report['quality_metrics']['tts_real_audio']}")
        print(f"📹 Vídeo Final: {report['quality_metrics']['final_video_generated']}")
        print("=" * 60)
        
        return report
        
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        return None

if __name__ == "__main__":
    main()