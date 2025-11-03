#!/usr/bin/env python3
"""
Script de Setup Automatizado - AiShorts v2.0
===========================================

Script para configuração automática do ambiente AiShorts v2.0.
Realiza limpeza, organização e setup completo da codebase.

Funcionalidades:
1. Limpeza de arquivos duplicados
2. Consolidação de configurações
3. Setup de dependências
4. Validação de imports
5. Criação de estrutura limpa

Autor: Sistema AiShorts v2.0
Data: 2025-11-04
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AiShortsCleanup:
    """Classe principal para limpeza e setup da codebase."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.aishorts_dir = self.root_dir / "aishorts_v2"
        self.backup_dir = self.root_dir / "backup_cleanup"
        
        # Estrutura final alvo
        self.target_structure = {
            "src": "Código fonte principal",
            "tests": "Testes organizados", 
            "docs": "Documentação consolidada",
            "data": "Dados centralizados",
            "scripts": "Scripts e demos"
        }
        
        logger.info("🔧 AiShorts Cleanup iniciado")
    
    def create_backup(self) -> bool:
        """Cria backup dos arquivos antes da limpeza."""
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            
            self.backup_dir.mkdir(exist_ok=True)
            
            # Backup dos arquivos de configuração
            backup_files = [
                "requirements_sync.txt",
                "requirements_video.txt", 
                "config/video_settings.py"
            ]
            
            for file_path in backup_files:
                src = self.root_dir / file_path
                if src.exists():
                    dst = self.backup_dir / file_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    logger.info(f"✅ Backup: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no backup: {e}")
            return False
    
    def consolidate_requirements(self) -> bool:
        """Consolida arquivos requirements em único arquivo."""
        try:
            logger.info("📦 Consolidando requirements...")
            
            # Ler todos os requirements existentes
            requirements_files = [
                self.root_dir / "requirements_sync.txt",
                self.root_dir / "requirements_video.txt",
                self.aishorts_dir / "requirements.txt"
            ]
            
            all_deps = set()
            
            for req_file in requirements_files:
                if req_file.exists():
                    with open(req_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                all_deps.add(line)
            
            # Escrever requirements consolidado
            consolidated_req = self.root_dir / "requirements.txt"
            with open(consolidated_req, 'w', encoding='utf-8') as f:
                f.write("# AiShorts v2.0 - Dependências Consolidadas\n")
                f.write("# Gerado automaticamente em setup.py\n\n")
                
                # Dependências organizadas por categoria
                categories = {
                    "Core": ["requests", "python-dotenv", "pydantic", "loguru"],
                    "AI/ML": ["openai", "transformers", "torch", "numpy", "scipy"],
                    "Video/Audio": ["moviepy", "opencv-python", "librosa", "yt-dlp"],
                    "Web": ["httpx", "ffmpeg-python"],
                    "Utils": ["Pillow", "tqdm", "psutil"],
                    "Development": ["pytest", "black", "flake8", "mypy"]
                }
                
                for category, deps in categories.items():
                    f.write(f"# {category}\n")
                    for dep in all_deps:
                        if any(d in dep for d in deps):
                            f.write(f"{dep}\n")
                    f.write("\n")
            
            logger.info(f"✅ Requirements consolidado em: {consolidated_req}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao consolidar requirements: {e}")
            return False
    
    def cleanup_demo_files(self) -> bool:
        """Consolida arquivos demo em estrutura limpa."""
        try:
            logger.info("🎬 Organizando arquivos demo...")
            
            # Criar diretório de scripts limpo
            scripts_dir = self.aishorts_dir / "scripts"
            scripts_dir.mkdir(exist_ok=True)
            
            # Mapear demos para funções específicas
            demo_mapping = {
                "demo_simple_test.py": "scripts/demo_basico.py",
                "demo_fase1_completo.py": "scripts/demo_completo_fase1.py", 
                "demo_fase2_completo.py": "scripts/demo_completo_fase2.py",
                "demo_end_to_end_real.py": "scripts/demo_integracao.py"
            }
            
            # Consolidar demos principais
            for old_demo, new_path in demo_mapping.items():
                src = self.root_dir / old_demo
                if src.exists():
                    dst = self.aishorts_dir / new_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    logger.info(f"✅ Demo consolidado: {old_demo} -> {new_path}")
            
            # Remover demos obsoletos
            old_demos = [
                "demo_clip_scoring.py",
                "demo_processamento_video_automatico.py",
                "demo_video_module.py", 
                "demo_tts_simple.py",
                "tts_demo.py",
                "demo_result_tiktok.json"
            ]
            
            for demo in old_demos:
                src = self.root_dir / demo
                if src.exists():
                    src.unlink()
                    logger.info(f"🗑️ Removido: {demo}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar demos: {e}")
            return False
    
    def fix_import_structure(self) -> bool:
        """Corrige estrutura de imports."""
        try:
            logger.info("🔗 Corrigindo estrutura de imports...")
            
            # Adicionar __init__.py em diretórios necessários
            init_dirs = [
                self.aishorts_dir,
                self.aishorts_dir / "src",
                self.aishorts_dir / "src" / "config",
                self.aishorts_dir / "src" / "core", 
                self.aishorts_dir / "src" / "generators",
                self.aishorts_dir / "src" / "validators",
                self.aishorts_dir / "src" / "video",
                self.aishorts_dir / "src" / "video" / "extractors",
                self.aishorts_dir / "src" / "video" / "generators",
                self.aishorts_dir / "src" / "video" / "matching",
                self.aishorts_dir / "src" / "video" / "processing",
                self.aishorts_dir / "src" / "utils"
            ]
            
            for dir_path in init_dirs:
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    init_file.touch()
                    logger.info(f"✅ Criado: {init_file.relative_to(self.aishorts_dir)}")
            
            # Corrigir imports em arquivos principais
            import_fixes = [
                {
                    "file": "aishorts_v2/src/video/extractors/segment_processor.py",
                    "old": "from ...utils.exceptions import",
                    "new": "from aishorts_v2.src.utils.exceptions import"
                },
                {
                    "file": "aishorts_v2/src/video/extractors/youtube_extractor.py", 
                    "old": "from ...utils.exceptions import",
                    "new": "from aishorts_v2.src.utils.exceptions import"
                },
                {
                    "file": "aishorts_v2/src/video/processing/platform_optimizer.py",
                    "old": "from ...config.video_platforms import",
                    "new": "from aishorts_v2.src.config.video_platforms import"
                }
            ]
            
            for fix in import_fixes:
                file_path = self.root_dir / fix["file"]
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    content = content.replace(fix["old"], fix["new"])
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    logger.info(f"✅ Corrigido imports em: {fix['file']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir imports: {e}")
            return False
    
    def organize_structure(self) -> bool:
        """Organiza estrutura final de diretórios."""
        try:
            logger.info("📁 Organizando estrutura de diretórios...")
            
            # Mover arquivos da raiz para estrutura organizada
            files_to_move = {
                "*.md": "docs/",
                "test_*.py": "tests/",
                "demo_*.py": "scripts/",
                "*.json": "data/",
                "*.txt": "docs/"
            }
            
            for pattern, target_dir in files_to_move.items():
                if pattern.startswith("*."):
                    # Arquivos de configuração especiais
                    if pattern == "*.txt":
                        # Manter requirements.txt na raiz
                        continue
                
                # Mover arquivos correspondentes
                for file_path in self.root_dir.glob(pattern):
                    if file_path.is_file():
                        dst_dir = self.aishorts_dir / target_dir
                        dst_dir.mkdir(exist_ok=True)
                        
                        dst = dst_dir / file_path.name
                        shutil.move(str(file_path), str(dst))
                        logger.info(f"✅ Movido: {file_path.name} -> {target_dir}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao organizar estrutura: {e}")
            return False
    
    def setup_dependencies(self) -> bool:
        """Instala dependências do projeto."""
        try:
            logger.info("📥 Instalando dependências...")
            
            requirements_file = self.root_dir / "requirements.txt"
            if not requirements_file.exists():
                logger.error("❌ requirements.txt não encontrado")
                return False
            
            # Instalar dependências
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Dependências instaladas com sucesso")
                return True
            else:
                logger.error(f"❌ Erro na instalação: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao instalar dependências: {e}")
            return False
    
    def validate_setup(self) -> Dict[str, Any]:
        """Valida se o setup foi bem-sucedido."""
        logger.info("🔍 Validando setup...")
        
        validation_results = {
            "imports_ok": False,
            "structure_ok": False,
            "requirements_ok": False,
            "docs_ok": False
        }
        
        try:
            # Testar imports básicos
            sys.path.insert(0, str(self.aishorts_dir))
            
            try:
                from src.config.settings import config
                from src.generators.theme_generator import theme_generator
                from src.video.extractors.youtube_extractor import YouTubeExtractor
                validation_results["imports_ok"] = True
                logger.info("✅ Imports funcionando")
            except Exception as e:
                logger.warning(f"⚠️ Alguns imports falharam: {e}")
            
            # Verificar estrutura
            required_dirs = ["src", "tests", "docs", "data", "scripts"]
            missing_dirs = [d for d in required_dirs if not (self.aishorts_dir / d).exists()]
            
            if not missing_dirs:
                validation_results["structure_ok"] = True
                logger.info("✅ Estrutura de diretórios correta")
            else:
                logger.warning(f"⚠️ Diretórios faltando: {missing_dirs}")
            
            # Verificar requirements
            req_file = self.root_dir / "requirements.txt"
            if req_file.exists() and req_file.stat().st_size > 1000:
                validation_results["requirements_ok"] = True
                logger.info("✅ Requirements válido")
            
            # Verificar documentação
            docs_dir = self.aishorts_dir / "docs"
            if docs_dir.exists() and len(list(docs_dir.glob("*.md"))) > 0:
                validation_results["docs_ok"] = True
                logger.info("✅ Documentação presente")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Erro na validação: {e}")
            return validation_results
    
    def generate_summary(self, validation_results: Dict[str, Any]) -> None:
        """Gera resumo final do setup."""
        logger.info("\n" + "="*60)
        logger.info("📊 RESUMO DO SETUP")
        logger.info("="*60)
        
        logger.info(f"📦 Requirements consolidado: {'✅' if validation_results.get('requirements_ok') else '❌'}")
        logger.info(f"🔗 Imports funcionando: {'✅' if validation_results.get('imports_ok') else '❌'}")
        logger.info(f"📁 Estrutura organizada: {'✅' if validation_results.get('structure_ok') else '❌'}")
        logger.info(f"📚 Documentação presente: {'✅' if validation_results.get('docs_ok') else '❌'}")
        
        success_rate = sum(validation_results.values()) / len(validation_results) * 100
        logger.info(f"📈 Taxa de sucesso: {success_rate:.0f}%")
        
        if success_rate >= 75:
            logger.info("🎉 Setup concluído com sucesso!")
        else:
            logger.warning("⚠️ Setup parcialmente concluído. Revisar problemas acima.")
        
        logger.info("\n💡 Próximos passos:")
        logger.info("   1. cd aishorts_v2")
        logger.info("   2. python scripts/demo_basico.py")
        logger.info("   3. python -m pytest tests/")
    
    def run_cleanup(self) -> bool:
        """Executa limpeza completa da codebase."""
        logger.info("🚀 Iniciando limpeza completa da codebase AiShorts v2.0...")
        
        steps = [
            ("Backup", self.create_backup),
            ("Consolidar requirements", self.consolidate_requirements),
            ("Limpar demos", self.cleanup_demo_files),
            ("Corrigir imports", self.fix_import_structure),
            ("Organizar estrutura", self.organize_structure),
            ("Instalar dependências", self.setup_dependencies),
            ("Validar setup", self.validate_setup)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n🔄 Executando: {step_name}...")
            
            try:
                result = step_func()
                if step_name == "Validar setup":
                    # Último step retorna dict de validação
                    self.generate_summary(result)
                elif not result:
                    logger.error(f"❌ Falha em: {step_name}")
                    return False
                else:
                    logger.info(f"✅ Concluído: {step_name}")
                    
            except Exception as e:
                logger.error(f"❌ Erro em {step_name}: {e}")
                return False
        
        logger.info("\n🎉 Limpeza da codebase concluída com sucesso!")
        return True


def main():
    """Função principal."""
    print("""
╔══════════════════════════════════════╗
║     AiShorts v2.0 - Setup Automatizado     ║
║                                      ║
║  🔧 Limpeza e organização da codebase    ║
║  📦 Consolidação de dependências         ║  
║  🔗 Correção de imports                  ║
║  📁 Estrutura limpa e organizada        ║
╚══════════════════════════════════════╝
    """)
    
    cleanup = AiShortsCleanup()
    success = cleanup.run_cleanup()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()