"""
Otimizador de vídeo para múltiplas plataformas (TikTok, YouTube Shorts, Instagram Reels)

Ajusta vídeos para atender aos requisitos específicos de cada plataforma.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import logging
from dataclasses import asdict

from ...config.video_platforms import (
    Platform, VideoPlatformConfig, video_config, get_category_config, get_timing_preset
)

class VideoProcessingError(Exception):
    """Exceção específica para processamento de vídeo."""
    pass

class PlatformOptimizer:
    """Otimizador de vídeo para diferentes plataformas."""
    
    def __init__(self, temp_dir: str = None):
        """
        Inicializa o otimizador.
        
        Args:
            temp_dir: Diretório temporário para arquivos intermediários
        """
        self.config = video_config
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix="video_opt_")
        self.logger = logging.getLogger(__name__)
        
        # Criar diretório temporário se não existir
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
    
    def optimize_for_platform(self, video_path: str, platform: Platform, 
                            category: str = "SPACE", quality: str = "Média") -> Dict[str, Any]:
        """
        Otimiza um vídeo para uma plataforma específica.
        
        Args:
            video_path: Caminho para o vídeo original
            platform: Plataforma de destino
            category: Categoria do conteúdo (SPACE, ANIMALS, etc.)
            quality: Qualidade de exportação
            
        Returns:
            Dict com informações da otimização
        """
        try:
            self.logger.info(f"Otimizando {video_path} para {platform.value}")
            
            # Validar vídeo de entrada
            validation = self._validate_input_video(video_path)
            if not validation["valid"]:
                raise VideoProcessingError(f"Vídeo inválido: {validation['issues']}")
            
            # Obter configurações da plataforma
            platform_config = self.config.get_platform_config(platform)
            category_config = get_category_config(category)
            quality_preset = self.config.get_quality_preset(quality)
            
            # Gerar caminho de saída
            output_path = self._generate_output_path(video_path, platform, category)
            
            # Otimizar vídeo
            optimization_result = self._apply_optimizations(
                video_path, output_path, platform_config, 
                category_config, quality_preset
            )
            
            return {
                "success": True,
                "output_path": output_path,
                "platform": platform.value,
                "category": category,
                "quality": quality,
                "original_validation": validation,
                "optimization_details": optimization_result,
                "specifications_used": {
                    "resolution": platform_config["specifications"].resolution_str,
                    "fps": platform_config["specifications"].fps,
                    "duration_range": f"{platform_config['specifications'].duration_min}s-{platform_config['specifications'].duration_max}s",
                    "file_size_limit": f"{platform_config['specifications'].file_size_max_mb}MB"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro na otimização: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "video_path": video_path,
                "platform": platform.value
            }
    
    def adjust_timing(self, video_path: str, platform: Platform, 
                     category: str = "SPACE") -> Dict[str, Any]:
        """
        Ajusta timing e transições do vídeo para a plataforma.
        
        Args:
            video_path: Caminho para o vídeo
            platform: Plataforma de destino
            category: Categoria do conteúdo
            
        Returns:
            Dict com informações do ajuste de timing
        """
        try:
            self.logger.info(f"Ajustando timing de {video_path} para {platform.value}")
            
            platform_config = self.config.get_platform_specs(platform)
            category_config = get_category_config(category)
            timing_config = get_timing_preset(category_config["timing_preset"])
            
            # Obter duração atual do vídeo
            current_duration = self._get_video_duration(video_path)
            
            # Calcular timing otimizado
            optimized_timing = self._calculate_optimal_timing(
                current_duration, platform_config, timing_config
            )
            
            return {
                "success": True,
                "current_duration": current_duration,
                "platform_duration_limits": {
                    "min": platform_config.duration_min,
                    "max": platform_config.duration_max
                },
                "optimized_timing": optimized_timing,
                "category_timing": category_config["timing_preset"],
                "recommendations": self._generate_timing_recommendations(
                    current_duration, platform_config, timing_config
                )
            }
            
        except Exception as e:
            self.logger.error(f"Erro no ajuste de timing: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "video_path": video_path
            }
    
    def apply_platform_settings(self, video_path: str, platform: Platform) -> Dict[str, Any]:
        """
        Aplica configurações específicas da plataforma (resolução, codec, etc.).
        
        Args:
            video_path: Caminho para o vídeo
            platform: Plataforma de destino
            
        Returns:
            Dict com informações da aplicação de configurações
        """
        try:
            self.logger.info(f"Aplicando configurações de {platform.value} para {video_path}")
            
            platform_config = self.config.get_platform_config(platform)
            specs = platform_config["specifications"]
            
            # Gerar caminho temporário
            temp_output = self._generate_temp_path(video_path, platform)
            
            # Aplicar configurações usando FFmpeg
            ffmpeg_result = self._run_ffmpeg_with_settings(
                video_path, temp_output, specs
            )
            
            # Validar resultado
            validation = self._validate_output_video(temp_output, specs)
            
            return {
                "success": True,
                "output_path": temp_output,
                "platform_specs": asdict(specs),
                "ffmpeg_result": ffmpeg_result,
                "validation": validation
            }
            
        except Exception as e:
            self.logger.error(f"Erro na aplicação de configurações: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "video_path": video_path,
                "platform": platform.value
            }
    
    def _validate_input_video(self, video_path: str) -> Dict[str, Any]:
        """Valida o vídeo de entrada."""
        file_path = Path(video_path)
        
        issues = []
        
        if not file_path.exists():
            issues.append("Arquivo não encontrado")
        
        if not self._check_video_integrity(video_path):
            issues.append("Arquivo corrompido ou não é um vídeo válido")
        
        if file_path.suffix.lower() not in ['.mp4', '.mov', '.avi', '.mkv']:
            issues.append("Formato não suportado")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "file_info": self._get_video_info(video_path) if file_path.exists() else None
        }
    
    def _generate_output_path(self, original_path: str, platform: Platform, 
                            category: str) -> str:
        """Gera caminho de saída para o vídeo otimizado."""
        original = Path(original_path)
        output_dir = Path(self.temp_dir) / "optimized"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        base_name = f"{original.stem}_{platform.value}_{category.lower()}"
        return str(output_dir / f"{base_name}.mp4")
    
    def _generate_temp_path(self, video_path: str, platform: Platform) -> str:
        """Gera caminho temporário para processamento."""
        original = Path(video_path)
        temp_dir = Path(self.temp_dir) / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        base_name = f"{original.stem}_temp_{platform.value}"
        return str(temp_dir / f"{base_name}.mp4")
    
    def _apply_optimizations(self, input_path: str, output_path: str,
                           platform_config: Dict[str, Any], 
                           category_config: Dict[str, Any],
                           quality_preset) -> Dict[str, Any]:
        """Aplica otimizações ao vídeo."""
        specs = platform_config["specifications"]
        
        # Comando FFmpeg otimizado
        ffmpeg_cmd = [
            "ffmpeg", "-y",  # Sobrescrever arquivo existente
            "-i", input_path,
            "-vf", f"scale={specs.resolution[0]}:{specs.resolution[1]}:force_original_aspect_ratio=decrease,pad={specs.resolution[0]}:{specs.resolution[1]}:(ow-iw)/2:(oh-ih)/2:black",
            "-r", str(specs.fps),  # Taxa de quadros
            "-c:v", "libx264",  # Codec de vídeo
            "-preset", "medium",  # Preset de codificação
            "-crf", self._quality_to_crf(quality_preset.quality_level),  # Qualidade
            "-b:v", f"{quality_preset.bitrate_kbps}k",  # Bitrate
            "-c:a", "aac",  # Codec de áudio
            "-b:a", "128k",  # Bitrate de áudio
            "-movflags", "+faststart",  # Otimização para streaming
            output_path
        ]
        
        # Executar comando
        result = subprocess.run(
            ffmpeg_cmd, 
            capture_output=True, 
            text=True, 
            timeout=300  # 5 minutos máximo
        )
        
        return {
            "ffmpeg_command": " ".join(ffmpeg_cmd),
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "file_size": os.path.getsize(output_path) if os.path.exists(output_path) else 0
        }
    
    def _quality_to_crf(self, quality_level: str) -> str:
        """Converte nível de qualidade para valor CRF do FFmpeg."""
        quality_map = {
            "baixa": "28",
            "média": "23",
            "alta": "18",
            "otimizada": "25"
        }
        return quality_map.get(quality_level, "23")
    
    def _get_video_duration(self, video_path: str) -> float:
        """Obtém a duração do vídeo em segundos."""
        cmd = [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return float(result.stdout.strip())
        return 0.0
    
    def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Obtém informações detalhadas do vídeo."""
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
        return {}
    
    def _check_video_integrity(self, video_path: str) -> bool:
        """Verifica integridade do arquivo de vídeo."""
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-count_packets", "-show_entries", "stream=nb_read_packets",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def _calculate_optimal_timing(self, duration: float, specs, timing_config: Dict[str, int]) -> Dict[str, Any]:
        """Calcula timing otimizado para o vídeo."""
        total_timing = sum(timing_config.values())
        
        if duration <= specs.duration_max:
            # Vídeo está dentro do limite - ajustar proporcionalmente
            scale_factor = duration / total_timing
            adjusted_timing = {k: int(v * scale_factor) for k, v in timing_config.items()}
        else:
            # Vídeo é muito longo - usar timing otimizado
            adjusted_timing = timing_config.copy()
        
        return {
            "original_duration": duration,
            "target_duration": sum(adjusted_timing.values()),
            "timing_breakdown": adjusted_timing,
            "scale_factor": duration / sum(timing_config.values()) if total_timing > 0 else 1.0
        }
    
    def _generate_timing_recommendations(self, duration: float, specs, timing_config: Dict[str, int]) -> List[str]:
        """Gera recomendações de timing."""
        recommendations = []
        
        if duration < specs.duration_min:
            recommendations.append(f"Vídeo muito curto ({duration:.1f}s). Mínimo para {specs.name}: {specs.duration_min}s")
        elif duration > specs.duration_max:
            recommendations.append(f"Vídeo muito longo ({duration:.1f}s). Máximo para {specs.name}: {specs.duration_max}s")
        else:
            recommendations.append("Duração adequada para a plataforma")
        
        # Recomendações específicas baseadas na duração
        if duration <= 15:
            recommendations.append("Use hook forte nos primeiros 3 segundos")
        elif duration <= 30:
            recommendations.append("Mantenha ritmo constante e variam visual a cada 3-5 segundos")
        else:
            recommendations.append("Planeje múltiplos pontos de interesse ao longo do vídeo")
        
        return recommendations
    
    def _run_ffmpeg_with_settings(self, input_path: str, output_path: str, specs) -> Dict[str, Any]:
        """Executa FFmpeg com configurações específicas da plataforma."""
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-r", str(specs.fps),
            "-vf", f"scale={specs.resolution[0]}:{specs.resolution[1]}",
            "-b:v", f"{specs.bitrate_kbps}k",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return {
            "command": " ".join(cmd),
            "return_code": result.returncode,
            "output": result.stdout,
            "error": result.stderr
        }
    
    def _validate_output_video(self, video_path: str, specs) -> Dict[str, Any]:
        """Valida o vídeo de saída."""
        if not os.path.exists(video_path):
            return {"valid": False, "error": "Arquivo de saída não foi criado"}
        
        info = self._get_video_info(video_path)
        
        # Verificar duração
        duration = self._get_video_duration(video_path)
        duration_ok = specs.duration_min <= duration <= specs.duration_max
        
        # Verificar tamanho
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        size_ok = file_size_mb <= specs.file_size_max_mb
        
        return {
            "valid": duration_ok and size_ok,
            "duration": duration,
            "duration_ok": duration_ok,
            "file_size_mb": file_size_mb,
            "size_ok": size_ok,
            "meets_platform_requirements": duration_ok and size_ok
        }
    
    def cleanup(self):
        """Limpa arquivos temporários."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

# Função de conveniência para uso direto
def optimize_video(video_path: str, platform: Platform, category: str = "SPACE") -> Dict[str, Any]:
    """
    Função de conveniência para otimizar um vídeo.
    
    Args:
        video_path: Caminho para o vídeo
        platform: Plataforma de destino
        category: Categoria do conteúdo
        
    Returns:
        Dict com resultado da otimização
    """
    optimizer = PlatformOptimizer()
    try:
        return optimizer.optimize_for_platform(video_path, platform, category)
    finally:
        optimizer.cleanup()

if __name__ == "__main__":
    # Teste básico
    import tempfile
    
    print("=== Teste do PlatformOptimizer ===")
    
    # Criar arquivo de teste temporário (simulado)
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        test_video_path = temp_file.name
        # Em um teste real, aqui would be a actual video file
    
    try:
        optimizer = PlatformOptimizer()
        result = optimizer.adjust_timing(test_video_path, Platform.TIKTOK, "SPACE")
        print(f"Resultado do ajuste de timing: {result}")
    finally:
        if os.path.exists(test_video_path):
            os.unlink(test_video_path)
        optimizer.cleanup()