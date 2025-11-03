"""
Demonstração do Sistema de Narração Kokoro TTS - Módulo 7
Pipeline completo AiShorts v2.0: Tema → Roteiro → Validação → Narração
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any

# Adicionar src ao path
sys.path.append('/workspace')
sys.path.append('/workspace/src')

# Imports dos módulos do projeto
from theme_generator.theme_generator import ThemeGenerator
from script_generator.script_generator import ScriptGenerator  
from validators.script_validator import ScriptValidator
from tts.kokoro_tts import KokoroTTSClient

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AiShortsPipeline:
    """
    Pipeline completo AiShorts v2.0 com narração TTS
    Tema → Roteiro → Validação → Narração
    """
    
    def __init__(self):
        """Inicializa todos os componentes do pipeline"""
        logger.info("🚀 Inicializando Pipeline AiShorts v2.0 completo...")
        
        # Inicializar geradores
        self.theme_generator = ThemeGenerator()
        self.script_generator = ScriptGenerator()
        self.validator = ScriptValidator()
        self.tts_client = KokoroTTSClient(
            lang_code='p',  # Português brasileiro
            voice_name='af_diamond',  # Voz feminina padrão
            speed=1.0,
            output_dir='outputs/tts_demo'
        )
        
        # Criar diretório de saída
        Path('outputs').mkdir(exist_ok=True)
        Path('outputs/tts_demo').mkdir(exist_ok=True)
        
        logger.info("✅ Pipeline inicializado com sucesso!")
    
    def generate_complete_short(self, 
                               category: str = "SCIENCE",
                               platform: str = "tiktok",
                               voice_name: str = "af_diamond") -> Dict[str, Any]:
        """
        Gera short completo com narração TTS
        
        Args:
            category: Categoria do tema (SCIENCE, ANIMALS, etc.)
            platform: Plataforma target (tiktok, shorts, reels)
            voice_name: Voz para narração TTS
            
        Returns:
            Dict com resultado completo do pipeline
        """
        logger.info(f"🎬 Iniciando geração completa - Categoria: {category}, Plataforma: {platform}")
        
        try:
            # ETAPA 1: Gerar Tema
            logger.info("1️⃣ GERANDO TEMA...")
            theme_result = self.theme_generator.generate_single_theme(category)
            if not theme_result.success:
                raise Exception(f"Falha na geração de tema: {theme_result.error}")
            
            theme = theme_result.theme
            logger.info(f"   ✅ Tema gerado: {theme.main_title}")
            
            # ETAPA 2: Gerar Roteiro  
            logger.info("2️⃣ GERANDO ROTEIRO...")
            script_result = self.script_generator.generate_script(
                theme=theme,
                platform=platform,
                duration_target=60  # 60 segundos
            )
            if not script_result.success:
                raise Exception(f"Falha na geração de roteiro: {script_result.error}")
            
            script = script_result.script
            logger.info(f"   ✅ Roteiro gerado ({len(script.sections)} seções)")
            
            # ETAPA 3: Validar Roteiro
            logger.info("3️⃣ VALIDANDO ROTEIRO...")
            validation_result = self.validator.validate_script(
                script=script,
                platform=platform
            )
            
            if not validation_result.success:
                logger.warning(f"   ⚠️ Validação com problemas: {validation_result.overall_score:.1f}/100")
            else:
                logger.info(f"   ✅ Roteiro validado: {validation_result.overall_score:.1f}/100")
            
            # ETAPA 4: Gerar Narração TTS
            logger.info("4️⃣ GERANDO NARRAÇÃO TTS...")
            
            # Configurar voz específica
            self.tts_client.set_voice(voice_name)
            
            # Gerar áudio completo
            tts_result = self.tts_client.script_to_audio(
                script=script,
                output_prefix=f"short_{category.lower()}_{platform}"
            )
            
            if not tts_result.get('full_audio', {}).get('success'):
                raise Exception(f"Falha na geração de áudio: {tts_result.get('full_audio', {}).get('error')}")
            
            logger.info(f"   ✅ Narração gerada: {tts_result['total_duration']:.1f}s")
            
            # ETAPA 5: Otimizar para Plataforma
            logger.info("5️⃣ OTIMIZANDO PARA PLATAFORMA...")
            optimization = self.tts_client.optimize_for_platform(
                audio_path=tts_result['full_audio']['audio_path'],
                platform=platform,
                target_duration=60
            )
            
            # Compilar resultado final
            final_result = {
                'pipeline_success': True,
                'execution_timestamp': __import__('datetime').datetime.now().isoformat(),
                
                # Dados do tema
                'theme': {
                    'title': theme.main_title,
                    'category': str(theme.category),
                    'keywords': theme.keywords,
                    'target_audience': theme.target_audience
                },
                
                # Dados do roteiro
                'script': {
                    'id': script.id,
                    'platform': platform,
                    'sections_count': len(script.sections),
                    'estimated_duration': script_result.estimated_duration,
                    'sections_summary': [
                        {
                            'type': section.type,
                            'content_preview': section.content[:100] + "..." if len(section.content) > 100 else section.content
                        } for section in script.sections
                    ]
                },
                
                # Dados da validação
                'validation': {
                    'success': validation_result.success,
                    'overall_score': validation_result.overall_score,
                    'quality_level': validation_result.quality_level,
                    'issues_count': len(validation_result.issues),
                    'recommendations': validation_result.suggestions[:3] if validation_result.suggestions else []
                },
                
                # Dados da narração
                'narration': {
                    'success': True,
                    'voice_info': tts_result['voice_info'],
                    'total_duration': tts_result['total_duration'],
                    'text_length': tts_result['total_text_length'],
                    'sections_audio': len(tts_result['section_audio']),
                    'audio_files': tts_result['output_files']
                },
                
                # Dados de otimização
                'optimization': {
                    'platform': platform,
                    'duration': optimization['original_duration'],
                    'is_compliant': optimization['is_compliant'],
                    'is_optimal': optimization['is_optimal'],
                    'recommendations': optimization['recommendations']
                },
                
                # Estatísticas completas
                'statistics': {
                    'total_processing_time': '~30-60s',  # Estimativa
                    'components_used': ['ThemeGenerator', 'ScriptGenerator', 'ScriptValidator', 'KokoroTTS'],
                    'output_format': 'WAV audio + JSON metadata',
                    'pipeline_version': 'AiShorts v2.0 - Módulo 7'
                }
            }
            
            logger.info("🎉 PIPELINE CONCLUÍDO COM SUCESSO!")
            logger.info(f"   📊 Score final: {validation_result.overall_score:.1f}/100")
            logger.info(f"   🎙️ Narração: {tts_result['total_duration']:.1f}s")
            logger.info(f"   📱 Plataforma: {platform}")
            
            return final_result
            
        except Exception as e:
            error_result = {
                'pipeline_success': False,
                'error': str(e),
                'stage': 'unknown',
                'timestamp': __import__('datetime').datetime.now().isoformat()
            }
            logger.error(f"❌ Erro no pipeline: {e}")
            return error_result
    
    def batch_generate_samples(self) -> Dict[str, Any]:
        """
        Gera múltiplos samples para demonstração
        """
        logger.info("🎯 Iniciando geração de samples em lote...")
        
        # Configurações para demonstração
        test_configs = [
            {
                'category': 'SCIENCE',
                'platform': 'tiktok',
                'voice': 'af_diamond',
                'name': 'Ciência'
            },
            {
                'category': 'ANIMALS', 
                'platform': 'shorts',
                'voice': 'af_heart',
                'name': 'Animais'
            },
            {
                'category': 'PSYCHOLOGY',
                'platform': 'reels', 
                'voice': 'am_oreo',
                'name': 'Psicologia'
            }
        ]
        
        results = []
        
        for i, config in enumerate(test_configs, 1):
            logger.info(f"\n📺 Sample {i}/3: {config['name']}")
            
            result = self.generate_complete_short(
                category=config['category'],
                platform=config['platform'],
                voice_name=config['voice']
            )
            
            results.append({
                'sample_name': config['name'],
                'config': config,
                'result': result
            })
            
            if result['pipeline_success']:
                logger.info(f"   ✅ Sample {config['name']} gerado com sucesso!")
            else:
                logger.error(f"   ❌ Sample {config['name']} falhou: {result.get('error')}")
        
        # Compilar relatório final
        successful_samples = [r for r in results if r['result']['pipeline_success']]
        failed_samples = [r for r in results if not r['result']['pipeline_success']]
        
        batch_report = {
            'batch_success': len(failed_samples) == 0,
            'total_samples': len(results),
            'successful_samples': len(successful_samples),
            'failed_samples': len(failed_samples),
            'samples': results,
            'summary': {
                'total_duration_generated': sum(
                    r['result']['narration']['total_duration'] 
                    for r in successful_samples
                ),
                'average_quality_score': sum(
                    r['result']['validation']['overall_score']
                    for r in successful_samples
                ) / len(successful_samples) if successful_samples else 0,
                'voices_used': list(set(r['config']['voice'] for r in successful_samples)),
                'platforms_tested': list(set(r['config']['platform'] for r in successful_samples))
            }
        }
        
        logger.info(f"\n📊 RELATÓRIO BATCH - Sucessos: {len(successful_samples)}/{len(results)}")
        logger.info(f"🎙️ Duração total: {batch_report['summary']['total_duration_generated']:.1f}s")
        logger.info(f"📈 Score médio: {batch_report['summary']['average_quality_score']:.1f}/100")
        
        return batch_report
    
    def save_results(self, results: Dict[str, Any], filename: str):
        """Salva resultados em arquivo JSON"""
        output_path = Path(f"outputs/{filename}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"💾 Resultados salvos em: {output_path}")


def main():
    """Função principal de demonstração"""
    print("🎙️" + "="*60)
    print("   DEMONSTRAÇÃO SISTEMA NARRAÇÃO KOKORO TTS")
    print("   AiShorts v2.0 - Pipeline Completo")
    print("   Tema → Roteiro → Validação → Narração")
    print("="*60)
    
    # Inicializar pipeline
    pipeline = AiShortsPipeline()
    
    # OPÇÃO 1: Geração single
    print("\n🎬 GERANDO SHORT INDIVIDUAL...")
    print("-" * 40)
    
    single_result = pipeline.generate_complete_short(
        category="SCIENCE",
        platform="tiktok", 
        voice_name="af_diamond"
    )
    
    # Salvar resultado individual
    pipeline.save_results(single_result, "tts_demo_single.json")
    
    # OPÇÃO 2: Geração em lote (descomente para executar)
    # print("\n🎯 GERANDO SAMPLES EM LOTE...")  
    # print("-" * 40)
    # 
    # batch_results = pipeline.batch_generate_samples()
    # pipeline.save_results(batch_results, "tts_demo_batch.json")
    
    # Mostrar resultado principal
    if single_result['pipeline_success']:
        print(f"\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"📊 Score: {single_result['validation']['overall_score']:.1f}/100")
        print(f"🎙️ Duração: {single_result['narration']['total_duration']:.1f}s")
        print(f"🎵 Voz: {single_result['narration']['voice_info']['description']}")
        print(f"📱 Plataforma: {single_result['optimization']['platform']}")
        print(f"📁 Arquivos: {single_result['narration']['audio_files']}")
    else:
        print(f"\n❌ ERRO NA DEMONSTRAÇÃO: {single_result.get('error')}")
    
    print(f"\n📋 Relatório detalhado salvo em: outputs/tts_demo_single.json")
    print("🎙️ Sistema de narração Kokoro TTS implementado com sucesso!")


if __name__ == "__main__":
    main()