"""
Kokoro TTS Client para AiShorts v2.0
Sistema de narração em português brasileiro integrado ao pipeline
"""

import os
import torch
import soundfile as sf
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from kokoro import KPipeline
from src.models.script_models import Script, ScriptSection

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KokoroTTSClient:
    """
    Cliente TTS usando Kokoro para narração em português brasileiro
    Integra com o pipeline AiShorts v2.0
    """
    
    def __init__(self, 
                 lang_code: str = 'p',  # 'p' = Português Brasileiro
                 voice_name: str = 'af_diamond',  # Voz feminina padrão
                 speed: float = 1.0,
                 output_dir: str = 'outputs/audio'):
        """
        Inicializa cliente Kokoro TTS
        
        Args:
            lang_code: Código do idioma ('p' = português brasileiro)
            voice_name: Nome da voz a usar
            speed: Velocidade da fala (1.0 = normal)
            output_dir: Diretório para salvar áudios
        """
        self.lang_code = lang_code
        self.voice_name = voice_name
        self.speed = speed
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar pipeline Kokoro
        try:
            self.pipeline = KPipeline(lang_code=lang_code)
            logger.info(f"Kokoro TTS inicializado - Lang: {lang_code}, Voice: {voice_name}")
        except Exception as e:
            logger.error(f"Erro ao inicializar Kokoro: {e}")
            raise
        
        # Mapear vozes disponíveis para português
        self.portuguese_voices = {
            'af_diamond': 'Voz feminina - Diamante',
            'af_heart': 'Voz feminina - Coração', 
            'af_breeze': 'Voz feminina - Brisa',
            'af_sol': 'Voz feminina - Sol',
            'am_oreo': 'Voz masculina - Oreo',
            'am_glenn': 'Voz masculina - Glenn',
            'am_liam': 'Voz masculina - Liam'
        }
    
    def text_to_speech(self, 
                      text: str, 
                      output_filename: Optional[str] = None,
                      voice: Optional[str] = None,
                      split_text: bool = True) -> Dict[str, Any]:
        """
        Converte texto para áudio usando Kokoro TTS
        
        Args:
            text: Texto para converter
            output_filename: Nome do arquivo de saída
            voice: Voz específica (usa a padrão se None)
            split_text: Se deve dividir texto longo em partes
            
        Returns:
            Dict com informações do áudio gerado
        """
        if voice:
            self.voice_name = voice
            
        if not text or not text.strip():
            raise ValueError("Texto vazio fornecido para TTS")
        
        # Limpar e preparar texto
        text = text.strip()
        
        # Dividir texto longo se necessário
        if split_text and len(text) > 1000:
            # Tentar dividir em parágrafos ou sentenças
            import re
            parts = re.split(r'[.!?]+', text)
            parts = [p.strip() for p in parts if p.strip()]
            
            audio_files = []
            for i, part in enumerate(parts):
                filename = f"{output_filename}_part_{i+1}.wav" if output_filename else f"segment_{i+1}.wav"
                result = self._generate_audio_segment(part, filename)
                audio_files.append(result['audio_path'])
            
            # Combinar áudios se múltiplos segmentos
            return self._combine_audio_segments(audio_files, output_filename)
        
        else:
            filename = output_filename or "narration.wav"
            return self._generate_audio_segment(text, filename)
    
    def _generate_audio_segment(self, text: str, filename: str) -> Dict[str, Any]:
        """Gera segmento de áudio individual"""
        try:
            audio_path = self.output_dir / filename
            
            # Gerar áudio com Kokoro
            generator = self.pipeline(
                text=text,
                voice=self.voice_name,
                speed=self.speed,
                split_pattern=r'\n+'  # Dividir por quebras de linha
            )
            
            # Coletar áudio gerado
            audio_data = []
            for i, (gs, ps, audio) in enumerate(generator):
                audio_data.append(audio)
                if i > 0:  # Apenas o primeiro chunk para texto simples
                    break
            
            if not audio_data:
                raise Exception("Nenhum áudio foi gerado")
            
            # Salvar áudio
            final_audio = audio_data[0]
            sf.write(str(audio_path), final_audio, 24000)
            
            # Calcular duração
            duration = len(final_audio) / 24000  # 24kHz sample rate
            
            logger.info(f"Áudio gerado: {audio_path} ({duration:.2f}s)")
            
            return {
                'audio_path': str(audio_path),
                'duration': duration,
                'text': text,
                'voice': self.voice_name,
                'speed': self.speed,
                'sample_rate': 24000,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar áudio: {e}")
            return {
                'error': str(e),
                'success': False,
                'audio_path': None,
                'duration': 0
            }
    
    def script_to_audio(self, 
                       script: Script, 
                       output_prefix: str = "narracao",
                       voice: Optional[str] = None) -> Dict[str, Any]:
        """
        Converte roteiro completo para áudio
        
        Args:
            script: Objeto Script com seções
            output_prefix: Prefixo para arquivos de saída
            voice: Voz específica para narração
            
        Returns:
            Dict com informações completas da narração
        """
        if voice:
            self.voice_name = voice
            
        # Extrair texto de todas as seções
        all_text = []
        section_audio_files = []
        
        for i, section in enumerate(script.sections):
            if section.content:
                section_text = f"{section.content}"
                if section.type == "hook":
                    section_text = f"{section_text} ..."  # Pausa dramática
                elif section.type == "conclusion":
                    section_text = f"{section_text}!"  # Pausa final
                
                all_text.append(section_text)
                
                # Gerar áudio para cada seção
                section_filename = f"{output_prefix}_section_{i+1}_{section.type}.wav"
                result = self.text_to_speech(
                    section_text, 
                    output_filename=section_filename,
                    split_text=False
                )
                
                if result['success']:
                    section_audio_files.append({
                        'section_type': section.type,
                        'audio_path': result['audio_path'],
                        'duration': result['duration'],
                        'text': section_text
                    })
        
        # Combinar todos os áudios
        full_text = " ".join(all_text)
        
        # Gerar arquivo completo
        full_audio_result = self.text_to_speech(
            full_text,
            output_filename=f"{output_prefix}_completo.wav",
            split_text=True
        )
        
        # Calcular estatísticas
        total_duration = sum(seg['duration'] for seg in section_audio_files)
        estimated_reading_time = total_duration / 60  # minutos
        
        return {
            'script_id': script.id,
            'theme': script.theme.main_title if script.theme else "Tema não definido",
            'sections_count': len(script.sections),
            'total_text_length': len(full_text),
            'total_duration': total_duration,
            'estimated_reading_time': estimated_reading_time,
            'full_audio': full_audio_result,
            'section_audio': section_audio_files,
            'voice_info': {
                'name': self.voice_name,
                'description': self.portuguese_voices.get(self.voice_name, "Voz customizada"),
                'lang_code': self.lang_code,
                'speed': self.speed
            },
            'output_files': {
                'complete': full_audio_result['audio_path'],
                'sections': [seg['audio_path'] for seg in section_audio_files]
            }
        }
    
    def optimize_for_platform(self, 
                             audio_path: str, 
                             platform: str = "tiktok",
                             target_duration: Optional[float] = None) -> Dict[str, Any]:
        """
        Otimiza áudio para plataforma específica
        
        Args:
            audio_path: Caminho do arquivo de áudio
            platform: Plataforma target (tiktok, shorts, reels)
            target_duration: Duração alvo em segundos
            
        Returns:
            Dict com informações da otimização
        """
        # Carregar áudio
        try:
            audio_data, sample_rate = sf.read(audio_path)
            duration = len(audio_data) / sample_rate
            
            # Configurações por plataforma
            platform_configs = {
                'tiktok': {'max_duration': 60, 'recommended': 45},
                'shorts': {'max_duration': 60, 'recommended': 45}, 
                'reels': {'max_duration': 90, 'recommended': 60}
            }
            
            config = platform_configs.get(platform, platform_configs['tiktok'])
            
            # Verificar conformidade
            is_compliant = duration <= config['max_duration']
            is_optimal = duration <= config['recommended']
            
            # Calcular speed factor se necessário
            speed_factor = 1.0
            if target_duration and duration > target_duration:
                speed_factor = duration / target_duration
            
            return {
                'audio_path': audio_path,
                'platform': platform,
                'original_duration': duration,
                'target_duration': target_duration,
                'platform_max_duration': config['max_duration'],
                'platform_recommended_duration': config['recommended'],
                'is_compliant': is_compliant,
                'is_optimal': is_optimal,
                'speed_factor': speed_factor,
                'recommendations': self._get_platform_recommendations(
                    duration, config, is_compliant, is_optimal
                )
            }
            
        except Exception as e:
            logger.error(f"Erro ao otimizar áudio: {e}")
            return {'error': str(e), 'success': False}
    
    def _get_platform_recommendations(self, duration: float, config: Dict, 
                                     is_compliant: bool, is_optimal: bool) -> List[str]:
        """Gera recomendações para otimização por plataforma"""
        recommendations = []
        
        if not is_compliant:
            recommendations.append(f"Áudio muito longo ({duration:.1f}s). Máximo permitido: {config['max_duration']}s")
            recommendations.append("Sugestão: Reduzir velocidade ou remover conteúdo desnecessário")
        
        elif not is_optimal:
            recommendations.append(f"Áudio pode ser otimizado. Duração recomendada: {config['recommended']}s")
            recommendations.append("Considerar acelerar levemente para maior engajamento")
        
        else:
            recommendations.append("Duração ideal para a plataforma!")
            
        return recommendations
    
    def _combine_audio_segments(self, audio_files: List[str], output_filename: str) -> Dict[str, Any]:
        """Combina múltiplos segmentos de áudio"""
        try:
            combined_path = self.output_dir / f"{output_filename}_combinado.wav"
            combined_data = []
            
            for audio_file in audio_files:
                if os.path.exists(audio_file):
                    data, sr = sf.read(audio_file)
                    combined_data.append(data)
            
            if combined_data:
                # Concatenar áudios
                import numpy as np
                final_audio = np.concatenate(combined_data)
                sf.write(str(combined_path), final_audio, 24000)
                
                duration = len(final_audio) / 24000
                
                return {
                    'audio_path': str(combined_path),
                    'duration': duration,
                    'segments_count': len(audio_files),
                    'success': True
                }
            else:
                raise Exception("Nenhum segmento válido para combinar")
                
        except Exception as e:
            logger.error(f"Erro ao combinar segmentos: {e}")
            return {'error': str(e), 'success': False}
    
    def get_voice_list(self) -> Dict[str, str]:
        """Retorna lista de vozes disponíveis para português"""
        return self.portuguese_voices.copy()
    
    def set_speed(self, speed: float):
        """Define velocidade da fala"""
        if 0.5 <= speed <= 2.0:
            self.speed = speed
            logger.info(f"Velocidade alterada para: {speed}x")
        else:
            raise ValueError("Velocidade deve estar entre 0.5 e 2.0")
    
    def set_voice(self, voice_name: str):
        """Define voz para narração"""
        if voice_name in self.portuguese_voices:
            self.voice_name = voice_name
            logger.info(f"Voz alterada para: {voice_name}")
        else:
            available = list(self.portuguese_voices.keys())
            raise ValueError(f"Voz '{voice_name}' não disponível. Disponíveis: {available}")


def main():
    """Função de teste standalone"""
    client = KokoroTTSClient()
    
    # Teste básico
    test_text = "Olá! Este é um teste do sistema de narração Kokoro para AiShorts v2.0."
    result = client.text_to_speech(test_text, "teste_basico")
    print(f"Teste básico: {result}")
    
    # Listar vozes disponíveis
    voices = client.get_voice_list()
    print(f"Vozes disponíveis: {voices}")


if __name__ == "__main__":
    main()