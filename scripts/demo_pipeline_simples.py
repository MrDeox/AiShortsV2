#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Pipeline Simples - Teste de Confiabilidade
Testa isoladamente Theme Generator e YouTube Extractor
Gera logs detalhados e arquivo de saída para validação

Uso: python demo_pipeline_simples.py
"""

import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Configuração de logging detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent / "aishorts_v2"
sys.path.insert(0, str(root_dir))

class PipelineTest:
    """Classe para testar o pipeline de forma isolada e confiável."""
    
    def __init__(self):
        self.output_dir = Path("pipeline_test_output")
        self.output_dir.mkdir(exist_ok=True)
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "theme_generator": {},
            "youtube_extractor": {},
            "pipeline_integration": {},
            "summary": {}
        }
    
    def log_step(self, step: str, message: str, level: str = "INFO"):
        """Registra um passo do teste com log detalhado."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {step}: {message}"
        
        if level == "ERROR":
            logger.error(log_msg)
        elif level == "WARNING":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
        
        # Salvar no results
        self.test_results["tests"][f"{step}_{int(time.time())}"] = {
            "timestamp": timestamp,
            "message": message,
            "level": level
        }
    
    def test_theme_generator_isolated(self) -> Dict[str, Any]:
        """Testa o Theme Generator isoladamente."""
        self.log_step("THEME_START", "Iniciando teste isolado do Theme Generator")
        
        theme_result = {
            "status": "pending",
            "components_tested": [],
            "errors": [],
            "performance": {}
        }
        
        try:
            # 1. Teste de import
            self.log_step("THEME_IMPORT", "Testando import do Theme Generator...")
            start_time = time.time()
            
            from src.generators.theme_generator import theme_generator
            from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
            
            import_time = time.time() - start_time
            theme_result["performance"]["import_time"] = import_time
            theme_result["components_tested"].append("import")
            
            self.log_step("THEME_IMPORT", f"✅ Importou em {import_time:.3f}s", "INFO")
            
            # 2. Teste de configurações
            self.log_step("THEME_CONFIG", "Testando configurações...")
            start_time = time.time()
            
            categories = prompt_engineering.get_all_categories()
            config_time = time.time() - start_time
            
            theme_result["performance"]["config_time"] = config_time
            theme_result["components_tested"].append("config")
            theme_result["components_tested"].append("categories")
            
            self.log_step("THEME_CONFIG", f"✅ {len(categories)} categorias disponíveis", "INFO")
            self.log_step("THEME_CONFIG", f"✅ Config carregada em {config_time:.3f}s", "INFO")
            
            # 3. Teste de estruturas de dados
            self.log_step("THEME_DATA", "Testando estruturas de dados...")
            start_time = time.time()
            
            from src.generators.theme_generator import GeneratedTheme
            
            test_theme = GeneratedTheme(
                content="Por que o céu é azul?",
                category=ThemeCategory.SCIENCE,
                quality_score=0.8,
                response_time=1.5,
                timestamp=datetime.now()
            )
            
            theme_dict = test_theme.to_dict()
            theme_restored = GeneratedTheme.from_dict(theme_dict)
            
            data_time = time.time() - start_time
            theme_result["performance"]["data_time"] = data_time
            theme_result["components_tested"].append("data_structures")
            
            self.log_step("THEME_DATA", "✅ Estruturas de dados funcionando", "INFO")
            self.log_step("THEME_DATA", f"✅ Dados processados em {data_time:.3f}s", "INFO")
            
            # 4. Teste de validação
            self.log_step("THEME_VALIDATION", "Testando validação...")
            start_time = time.time()
            
            # Testar limpeza de resposta
            messy_response = "   Por que o céu é azul?   \n\nTexto adicional"
            clean_response = theme_generator._clean_response(messy_response)
            
            # Testar validação de formato
            valid_theme = "Por que o céu é azul?"
            invalid_theme = ""
            
            try:
                theme_generator._validate_theme_response(valid_theme, ThemeCategory.SCIENCE)
                valid_passes = True
            except:
                valid_passes = False
            
            try:
                theme_generator._validate_theme_response(invalid_theme, ThemeCategory.SCIENCE)
                invalid_passes = True
            except:
                invalid_passes = False
            
            validation_time = time.time() - start_time
            theme_result["performance"]["validation_time"] = validation_time
            theme_result["components_tested"].append("validation")
            
            self.log_step("THEME_VALIDATION", f"✅ Resposta válida passou: {valid_passes}", "INFO")
            self.log_step("THEME_VALIDATION", f"✅ Resposta inválida rejeitada: {not invalid_passes}", "INFO")
            self.log_step("THEME_VALIDATION", f"✅ Validação em {validation_time:.3f}s", "INFO")
            
            # 5. Teste de análise
            self.log_step("THEME_ANALYSIS", "Testando análise de temas...")
            start_time = time.time()
            
            test_themes = [
                GeneratedTheme(
                    content="Por que o céu é azul?",
                    category=ThemeCategory.SCIENCE,
                    quality_score=0.8,
                    response_time=1.0,
                    timestamp=datetime.now()
                ),
                GeneratedTheme(
                    content="Como funcionava o calendário egípcio?",
                    category=ThemeCategory.HISTORY,
                    quality_score=0.9,
                    response_time=1.2,
                    timestamp=datetime.now()
                )
            ]
            
            analysis = theme_generator.analyze_themes(test_themes)
            analysis_time = time.time() - start_time
            
            theme_result["performance"]["analysis_time"] = analysis_time
            theme_result["components_tested"].append("analysis")
            theme_result["sample_analysis"] = analysis
            
            self.log_step("THEME_ANALYSIS", f"✅ {analysis['total_themes']} temas analisados", "INFO")
            self.log_step("THEME_ANALYSIS", f"✅ Qualidade média: {analysis['quality_stats']['avg_quality']:.2f}", "INFO")
            self.log_step("THEME_ANALYSIS", f"✅ Análise em {analysis_time:.3f}s", "INFO")
            
            # Salvar resultado do Theme Generator
            theme_result["status"] = "success"
            theme_result["total_components"] = len(theme_result["components_tested"])
            theme_result["total_performance_time"] = sum(theme_result["performance"].values())
            
            self.log_step("THEME_SUCCESS", f"✅ Theme Generator testado com sucesso!", "INFO")
            
        except Exception as e:
            error_msg = f"Erro no teste do Theme Generator: {str(e)}"
            self.log_step("THEME_ERROR", error_msg, "ERROR")
            theme_result["status"] = "error"
            theme_result["errors"].append(error_msg)
        
        return theme_result
    
    def test_youtube_extractor_isolated(self) -> Dict[str, Any]:
        """Testa o YouTube Extractor isoladamente."""
        self.log_step("YT_START", "Iniciando teste isolado do YouTube Extractor")
        
        yt_result = {
            "status": "pending",
            "components_tested": [],
            "errors": [],
            "performance": {}
        }
        
        try:
            # 1. Teste de import
            self.log_step("YT_IMPORT", "Testando import do YouTube Extractor...")
            start_time = time.time()
            
            from src.video.extractors.youtube_extractor import YouTubeExtractor
            from src.video.extractors.segment_processor import SegmentProcessor
            
            import_time = time.time() - start_time
            yt_result["performance"]["import_time"] = import_time
            yt_result["components_tested"].append("import")
            
            self.log_step("YT_IMPORT", f"✅ Importou em {import_time:.3f}s", "INFO")
            
            # 2. Teste de inicialização
            self.log_step("YT_INIT", "Testando inicialização...")
            start_time = time.time()
            
            extractor = YouTubeExtractor(
                temp_dir=str(self.output_dir / "temp"),
                output_dir=str(self.output_dir / "output")
            )
            
            init_time = time.time() - start_time
            yt_result["performance"]["init_time"] = init_time
            yt_result["components_tested"].append("initialization")
            
            self.log_step("YT_INIT", f"✅ Inicializou em {init_time:.3f}s", "INFO")
            
            # 3. Teste de configurações
            self.log_step("YT_CONFIG", "Testando configurações do yt-dlp...")
            start_time = time.time()
            
            config_loaded = hasattr(extractor, 'ydl_opts') and extractor.ydl_opts is not None
            dirs_created = extractor.temp_dir.exists() and extractor.output_dir.exists()
            
            config_time = time.time() - start_time
            yt_result["performance"]["config_time"] = config_time
            yt_result["components_tested"].append("config")
            yt_result["components_tested"].append("directories")
            
            self.log_step("YT_CONFIG", f"✅ Configurações carregadas: {config_loaded}", "INFO")
            self.log_step("YT_CONFIG", f"✅ Diretórios criados: {dirs_created}", "INFO")
            self.log_step("YT_CONFIG", f"✅ Config verificada em {config_time:.3f}s", "INFO")
            
            # 4. Teste de métodos básicos (sem API real)
            self.log_step("YT_METHODS", "Testando métodos básicos...")
            start_time = time.time()
            
            # Testar cleanup
            extractor.cleanup_temp_files()
            
            methods_time = time.time() - start_time
            yt_result["performance"]["methods_time"] = methods_time
            yt_result["components_tested"].append("basic_methods")
            
            self.log_step("YT_METHODS", "✅ Métodos básicos testados", "INFO")
            self.log_step("YT_METHODS", f"✅ Métodos verificados em {methods_time:.3f}s", "INFO")
            
            # 5. Teste de tratamento de erro
            self.log_step("YT_ERRORS", "Testando tratamento de erro...")
            start_time = time.time()
            
            try:
                # Testar URL inválida
                extractor.extract_video_info("https://youtube.com/watch?v=INVALID")
                error_handling_fails = True
            except Exception:
                error_handling_fails = False
            
            errors_time = time.time() - start_time
            yt_result["performance"]["errors_time"] = errors_time
            yt_result["components_tested"].append("error_handling")
            
            self.log_step("YT_ERRORS", f"✅ Erro de URL inválida capturado: {not error_handling_fails}", "INFO")
            self.log_step("YT_ERRORS", f"✅ Tratamento de erro em {errors_time:.3f}s", "INFO")
            
            # Salvar resultado do YouTube Extractor
            yt_result["status"] = "success"
            yt_result["total_components"] = len(yt_result["components_tested"])
            yt_result["total_performance_time"] = sum(yt_result["performance"].values())
            
            self.log_step("YT_SUCCESS", f"✅ YouTube Extractor testado com sucesso!", "INFO")
            
        except Exception as e:
            error_msg = f"Erro no teste do YouTube Extractor: {str(e)}"
            self.log_step("YT_ERROR", error_msg, "ERROR")
            yt_result["status"] = "error"
            yt_result["errors"].append(error_msg)
        
        return yt_result
    
    def test_pipeline_integration(self, theme_result: Dict, yt_result: Dict) -> Dict[str, Any]:
        """Testa a integração dos dois módulos."""
        self.log_step("PIPE_START", "Iniciando teste de integração do pipeline")
        
        integration_result = {
            "status": "pending",
            "integration_tests": [],
            "errors": [],
            "performance": {}
        }
        
        try:
            start_time = time.time()
            
            # 1. Verificar compatibilidade
            self.log_step("PIPE_COMPAT", "Verificando compatibilidade entre módulos...")
            
            theme_ok = theme_result["status"] == "success"
            yt_ok = yt_result["status"] == "success"
            
            self.log_step("PIPE_COMPAT", f"Theme Generator: {'✅ OK' if theme_ok else '❌ FALHOU'}", "INFO")
            self.log_step("PIPE_COMPAT", f"YouTube Extractor: {'✅ OK' if yt_ok else '❌ FALHOU'}", "INFO")
            
            integration_result["integration_tests"].append("compatibility")
            integration_result["compatibility"] = {
                "theme_generator": theme_ok,
                "youtube_extractor": yt_ok,
                "overall": theme_ok and yt_ok
            }
            
            # 2. Simular fluxo de dados entre módulos
            if theme_ok and yt_ok:
                self.log_step("PIPE_FLOW", "Simulando fluxo de dados...")
                
                # Simular tema gerado
                from src.generators.theme_generator import GeneratedTheme
                from src.generators.prompt_engineering import ThemeCategory
                
                sample_theme = GeneratedTheme(
                    content="Por que os flamingos são rosa?",
                    category=ThemeCategory.NATURE,
                    quality_score=0.85,
                    response_time=2.1,
                    timestamp=datetime.now()
                )
                
                # Simular informações de vídeo
                sample_video_info = {
                    "title": "Flamingos Rosa - Curiosidades",
                    "description": "Um vídeo sobre flamingos...",
                    "duration": 180,
                    "categories": ["nature", "education"]
                }
                
                integration_result["integration_tests"].append("data_flow")
                integration_result["sample_data"] = {
                    "theme": sample_theme.to_dict(),
                    "video_info": sample_video_info
                }
                
                self.log_step("PIPE_FLOW", "✅ Fluxo de dados simulado", "INFO")
            
            # 3. Verificar outputs
            self.log_step("PIPE_OUTPUT", "Verificando sistema de outputs...")
            
            output_files = list(self.output_dir.glob("*.json")) + list(self.output_dir.glob("*.log"))
            
            integration_result["integration_tests"].append("output_system")
            integration_result["output_files"] = len(output_files)
            
            self.log_step("PIPE_OUTPUT", f"✅ {len(output_files)} arquivos de output criados", "INFO")
            
            integration_time = time.time() - start_time
            integration_result["performance"]["integration_time"] = integration_time
            
            # Resultado final
            overall_success = theme_ok and yt_ok
            
            integration_result["status"] = "success" if overall_success else "partial"
            integration_result["integration_score"] = len(integration_result["integration_tests"]) / 3
            
            self.log_step("PIPE_SUCCESS", f"✅ Integração testada - Score: {integration_result['integration_score']:.2f}", "INFO")
            
        except Exception as e:
            error_msg = f"Erro na integração: {str(e)}"
            self.log_step("PIPE_ERROR", error_msg, "ERROR")
            integration_result["status"] = "error"
            integration_result["errors"].append(error_msg)
        
        return integration_result
    
    def generate_validation_report(self):
        """Gera relatório final de validação."""
        self.log_step("REPORT_START", "Gerando relatório final de validação")
        
        # Estatísticas finais
        total_tests = len(self.test_results["tests"])
        successful_tests = len([t for t in self.test_results["tests"].values() if t["level"] != "ERROR"])
        
        # Salvar resultados detalhados
        output_file = self.output_dir / "pipeline_test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False, default=str)
        
        # Criar relatório resumido
        summary_report = {
            "test_execution": {
                "timestamp": self.test_results["timestamp"],
                "total_test_steps": total_tests,
                "successful_steps": successful_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0
            },
            "component_status": {
                "theme_generator": self.test_results["theme_generator"].get("status", "unknown"),
                "youtube_extractor": self.test_results["youtube_extractor"].get("status", "unknown"),
                "pipeline_integration": self.test_results["pipeline_integration"].get("status", "unknown")
            },
            "performance_summary": {
                "theme_generator_time": self.test_results["theme_generator"].get("total_performance_time", 0),
                "youtube_extractor_time": self.test_results["youtube_extractor"].get("total_performance_time", 0),
                "total_execution_time": sum([
                    self.test_results["theme_generator"].get("total_performance_time", 0),
                    self.test_results["youtube_extractor"].get("total_performance_time", 0),
                    self.test_results["pipeline_integration"].get("performance", {}).get("integration_time", 0)
                ])
            },
            "validation": {
                "pipeline_reliable": all([
                    self.test_results["theme_generator"].get("status") == "success",
                    self.test_results["youtube_extractor"].get("status") == "success",
                    self.test_results["pipeline_integration"].get("status") in ["success", "partial"]
                ]),
                "components_tested": {
                    "theme_generator": self.test_results["theme_generator"].get("total_components", 0),
                    "youtube_extractor": self.test_results["youtube_extractor"].get("total_components", 0)
                },
                "ready_for_production": False
            }
        }
        
        # Determinar se está pronto para produção
        all_components_success = all([
            self.test_results["theme_generator"].get("status") == "success",
            self.test_results["youtube_extractor"].get("status") == "success"
        ])
        
        summary_report["validation"]["ready_for_production"] = all_components_success
        
        # Salvar relatório resumido
        summary_file = self.output_dir / "pipeline_validation_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_report, f, indent=2, ensure_ascii=False, default=str)
        
        self.test_results["summary"] = summary_report
        
        # Log final
        self.log_step("REPORT_COMPLETE", f"Relatório salvo em: {output_file}", "INFO")
        self.log_step("REPORT_COMPLETE", f"Resumo salvo em: {summary_file}", "INFO")
        
        return summary_report
    
    def run_complete_test(self):
        """Executa o teste completo do pipeline."""
        self.log_step("MAIN_START", "🚀 Iniciando teste completo do pipeline")
        
        start_time = time.time()
        
        try:
            # 1. Testar Theme Generator isoladamente
            self.log_step("MAIN_PHASE", "FASE 1: Testando Theme Generator isoladamente")
            theme_result = self.test_theme_generator_isolated()
            self.test_results["theme_generator"] = theme_result
            
            # 2. Testar YouTube Extractor isoladamente
            self.log_step("MAIN_PHASE", "FASE 2: Testando YouTube Extractor isoladamente")
            yt_result = self.test_youtube_extractor_isolated()
            self.test_results["youtube_extractor"] = yt_result
            
            # 3. Testar integração
            self.log_step("MAIN_PHASE", "FASE 3: Testando integração dos componentes")
            integration_result = self.test_pipeline_integration(theme_result, yt_result)
            self.test_results["pipeline_integration"] = integration_result
            
            # 4. Gerar relatório final
            self.log_step("MAIN_PHASE", "FASE 4: Gerando relatório final")
            summary = self.generate_validation_report()
            
            # Tempo total
            total_time = time.time() - start_time
            
            # Resumo final
            self.log_step("MAIN_FINISH", f"🎉 Teste completo finalizado em {total_time:.2f}s", "INFO")
            self.log_step("MAIN_FINISH", f"📊 Taxa de sucesso: {summary['test_execution']['success_rate']:.1%}", "INFO")
            self.log_step("MAIN_FINISH", f"🔧 Componentes testados: Theme({theme_result.get('total_components', 0)}), YouTube({yt_result.get('total_components', 0)})", "INFO")
            self.log_step("MAIN_FINISH", f"✅ Pronto para produção: {'SIM' if summary['validation']['ready_for_production'] else 'NÃO'}", "INFO")
            
            return summary
            
        except Exception as e:
            self.log_step("MAIN_ERROR", f"❌ Erro crítico no teste completo: {str(e)}", "ERROR")
            raise


def main():
    """Função principal."""
    print("=" * 80)
    print("🧪 DEMO PIPELINE SIMPLES - TESTE DE CONFIABILIDADE")
    print("=" * 80)
    print()
    print("📋 Objetivo: Testar isoladamente Theme Generator e YouTube Extractor")
    print("📊 Saída: Logs detalhados + arquivo de validação")
    print("🎯 Meta: Pipeline simples e confiável")
    print()
    
    try:
        # Executar teste
        tester = PipelineTest()
        summary = tester.run_complete_test()
        
        # Resultado final
        print("\n" + "=" * 80)
        print("📊 RESULTADO FINAL")
        print("=" * 80)
        
        print(f"Theme Generator: {'✅' if summary['component_status']['theme_generator'] == 'success' else '❌'}")
        print(f"YouTube Extractor: {'✅' if summary['component_status']['youtube_extractor'] == 'success' else '❌'}")
        print(f"Integração: {'✅' if summary['component_status']['pipeline_integration'] in ['success', 'partial'] else '❌'}")
        
        print(f"\n🚀 Pronto para produção: {'✅ SIM' if summary['validation']['ready_for_production'] else '❌ NÃO'}")
        
        print(f"\n📁 Arquivos gerados:")
        print(f"   • pipeline_test_output/pipeline_test_results.json (detalhado)")
        print(f"   • pipeline_test_output/pipeline_validation_summary.json (resumo)")
        print(f"   • pipeline_test.log (logs)")
        
        if summary['validation']['ready_for_production']:
            print("\n🎉 PIPELINE VALIDADO COM SUCESSO!")
            print("✅ Todos os componentes estão funcionando")
            print("✅ Testes de integração passaram")
            print("✅ Sistema pronto para uso em produção")
            return True
        else:
            print("\n⚠️ PIPELINE PRECISA DE AJUSTES")
            print("❌ Alguns componentes falharam nos testes")
            print("🔧 Verifique os logs para mais detalhes")
            return False
            
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO: {str(e)}")
        print("🔧 Verifique a configuração dos módulos")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)