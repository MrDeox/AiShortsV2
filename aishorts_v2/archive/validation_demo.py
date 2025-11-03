"""
Demonstração do Sistema de Validação de Roteiros - AiShorts v2.0

Este script demonstra as funcionalidades do sistema de validação,
incluindo validação para múltiplas plataformas e geração de relatórios.
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Adiciona o diretório src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from src.validators.script_validator import (
    ScriptValidator, PlatformType, ValidationSeverity, QualityLevel
)
from src.generators.script_generator import GeneratedScript, ScriptSection
from src.generators.theme_generator import GeneratedTheme
from src.generators.prompt_engineering import ThemeCategory


def create_sample_scripts() -> Dict[str, GeneratedScript]:
    """Cria roteiros de exemplo para demonstração."""
    
    scripts = {}
    
    # 1. Roteiro de qualidade alta
    print("📝 Criando roteiro de qualidade alta...")
    
    theme_high = GeneratedTheme(
        content="Mistérios dos oceanos profundos",
        category=ThemeCategory.SCIENCE,
        quality_score=0.9,
        response_time=2.5,
        timestamp=datetime.now()
    )
    
    hook_high = ScriptSection(
        name="hook",
        content="Você sabia que existem criaturas nos oceanos que brilham no escuro? Esses seres incríveis estão a milhares de metros de profundidade!",
        duration_seconds=18,
        purpose="Captar atenção com curiosidade",
        key_elements=["pergunta", "criaturas", "bioluminescência"]
    )
    
    development_high = ScriptSection(
        name="development",
        content="Esses organismos usam bioluminescência para caçar, se comunicar e se defender. Estudos recentes mostram que 80% das criaturas marinhas em águas profundas possuem essa capacidade incrível. Pesquisadores descobriram que essa luz é produced por uma reação química chamada luciferina.",
        duration_seconds=63,
        purpose="Explicar o fenômeno científico",
        key_elements=["bioluminescência", "estudos", "luciferina"]
    )
    
    conclusion_high = ScriptSection(
        name="conclusion",
        content="Incrível, né? Os oceanos ainda guardam muitos segredos! Curtiu esse fato? Compartilha com seus amigos e segue para mais mistérios marinhos!",
        duration_seconds=18,
        purpose="Encerrar com engajamento",
        key_elements=["engajamento", "cta", "oceanografia"]
    )
    
    scripts["high_quality"] = GeneratedScript(
        title="Bioluminescência Oceânica",
        theme=theme_high,
        sections=[hook_high, development_high, conclusion_high],
        total_duration=99,
        quality_score=0.92,
        engagement_score=0.95,
        retention_score=0.88,
        response_time=3.2,
        timestamp=datetime.now()
    )
    
    # 2. Roteiro de qualidade média
    print("📝 Criando roteiro de qualidade média...")
    
    theme_medium = GeneratedTheme(
        content="Fatos sobre o espaço",
        category=ThemeCategory.SPACE,
        quality_score=0.7,
        response_time=2.0,
        timestamp=datetime.now()
    )
    
    hook_medium = ScriptSection(
        name="hook",
        content="O espaço é muito interessante",
        duration_seconds=10,
        purpose="Hook básico",
        key_elements=["espaço"]
    )
    
    development_medium = ScriptSection(
        name="development",
        content="Existem muitas estrelas no céu. Elas são muito brilhantes e bonitas.",
        duration_seconds=50,
        purpose="Desenvolvimento simples",
        key_elements=["estrelas", "céu"]
    )
    
    conclusion_medium = ScriptSection(
        name="conclusion",
        content="Espero que tenham gostado",
        duration_seconds=15,
        purpose="Encerrar",
        key_elements=["expectativa"]
    )
    
    scripts["medium_quality"] = GeneratedScript(
        title="Fatos Básicos do Espaço",
        theme=theme_medium,
        sections=[hook_medium, development_medium, conclusion_medium],
        total_duration=75,
        quality_score=0.65,
        engagement_score=0.45,
        retention_score=0.55,
        response_time=2.8,
        timestamp=datetime.now()
    )
    
    # 3. Roteiro problemático
    print("📝 Criando roteiro problemático...")
    
    theme_problematic = GeneratedTheme(
        content="Tema genérico",
        category=ThemeCategory.SCIENCE,
        quality_score=0.3,
        response_time=1.5,
        timestamp=datetime.now()
    )
    
    hook_problematic = ScriptSection(
        name="hook",
        content="",  # Conteúdo vazio - PROBLEMA
        duration_seconds=0,  # Duração zero - PROBLEMA
        purpose="",
        key_elements=[]
    )
    
    development_problematic = ScriptSection(
        name="development",
        content="spam spam spam repetição spam spam spam spam spam repetição spam",  # Muito repetitivo
        duration_seconds=25,
        purpose="",
        key_elements=[]
    )
    
    scripts["problematic"] = GeneratedScript(
        title="Roteiro com Problemas",
        theme=theme_problematic,
        sections=[hook_problematic, development_problematic],
        total_duration=25,
        quality_score=0.25,
        engagement_score=0.15,
        retention_score=0.20,
        response_time=1.5,
        timestamp=datetime.now()
    )
    
    return scripts


def demonstrate_single_platform_validation(validator: ScriptValidator, script: GeneratedScript):
    """Demonstra validação para uma plataforma específica."""
    print(f"\n🎯 VALIDANDO PARA TIKTOK")
    print("=" * 50)
    
    report = validator.validate_script(script, PlatformType.TIKTOK)
    
    # Exibe resumo
    print(f"📊 RESUMO DA VALIDAÇÃO:")
    print(f"   Plataforma: {report.platform.value}")
    print(f"   Score Geral: {report.overall_score:.2f}/100")
    print(f"   Nível: {report.quality_level.value.upper()}")
    print(f"   Aprovado: {'✅ SIM' if report.is_approved else '❌ NÃO'}")
    
    # Exibe scores por categoria
    print(f"\n📈 SCORES DETALHADOS:")
    print(f"   Estrutura: {report.structure_validation.score:.1f}/100")
    print(f"   Conteúdo: {report.content_validation.score:.1f}/100") 
    print(f"   Plataforma: {report.platform_validation.score:.1f}/100")
    
    # Exibe métricas de qualidade
    print(f"\n🎯 MÉTRICAS DE QUALIDADE:")
    print(f"   Clareza: {report.quality_metrics.clarity_score:.2f}")
    print(f"   Engajamento: {report.quality_metrics.engagement_score:.2f}")
    print(f"   Retenção: {report.quality_metrics.retention_score:.2f}")
    
    # Exibe problemas encontrados
    if report.all_issues:
        print(f"\n⚠️  PROBLEMAS ENCONTRADOS ({len(report.all_issues)}):")
        for i, issue in enumerate(report.all_issues[:5], 1):  # Mostra apenas os 5 primeiros
            emoji = "🔴" if issue.severity == ValidationSeverity.ERROR else "🟡"
            print(f"   {emoji} {issue.code}: {issue.message}")
            if issue.section:
                print(f"      Seção: {issue.section}")
    
    # Exibe sugestões
    if report.suggestions:
        print(f"\n💡 SUGESTÕES ({len(report.suggestions)}):")
        for i, suggestion in enumerate(report.suggestions[:3], 1):  # Mostra apenas as 3 primeiras
            print(f"   {i}. {suggestion}")
    
    return report


def demonstrate_multiple_platform_validation(validator: ScriptValidator, script: GeneratedScript):
    """Demonstra validação para múltiplas plataformas."""
    print(f"\n🌐 VALIDAÇÃO MULTIPLATAFORMA")
    print("=" * 50)
    
    reports = validator.validate_multiple_platforms(script)
    
    print(f"Roteiro: '{script.title}'\n")
    
    # Cria tabela comparativa
    platforms_data = []
    for platform, report in reports.items():
        platforms_data.append({
            "plataforma": platform.value.upper(),
            "score": f"{report.overall_score:.1f}",
            "nível": report.quality_level.value,
            "aprovado": "✅" if report.is_approved else "❌",
            "problemas": len(report.all_issues),
            "sugestões": len(report.suggestions)
        })
    
    # Exibe tabela
    print(f"{'Plataforma':<12} {'Score':<8} {'Nível':<10} {'Aprovado':<10} {'Problemas':<10} {'Sugestões':<10}")
    print("-" * 70)
    for data in platforms_data:
        print(f"{data['plataforma']:<12} {data['score']:<8} {data['nível']:<10} {data['aprovado']:<10} {data['problemas']:<10} {data['sugestões']:<10}")
    
    # Identifica a melhor plataforma
    best_platform = max(reports.items(), key=lambda x: x[1].overall_score)
    worst_platform = min(reports.items(), key=lambda x: x[1].overall_score)
    
    print(f"\n🏆 MELHOR PLATAFORMA: {best_platform[0].value.upper()} ({best_platform[1].overall_score:.1f}/100)")
    print(f"⚠️  PLATAFORMA MAIS DESAFIADORA: {worst_platform[0].value.upper()} ({worst_platform[1].overall_score:.1f}/100)")
    
    return reports


def save_comprehensive_report(reports: Dict[str, Dict[PlatformType, Any]], output_dir: Path):
    """Salva relatório comprensivo de validação."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Relatório principal
    main_report = {
        "timestamp": datetime.now().isoformat(),
        "total_scripts": len(reports),
        "scripts_analyzed": {}
    }
    
    for script_name, script_reports in reports.items():
        main_report["scripts_analyzed"][script_name] = {}
        
        for platform, report in script_reports.items():
            main_report["scripts_analyzed"][script_name][platform.value] = {
                "overall_score": report.overall_score,
                "quality_level": report.quality_level.value,
                "is_approved": report.is_approved,
                "summary": report.get_summary(),
                "issues_count": len(report.all_issues),
                "critical_issues": len(report.get_critical_issues()),
                "suggestions_count": len(report.suggestions)
            }
    
    # Salva relatório principal
    main_file = output_dir / f"validation_report_{timestamp}.json"
    with open(main_file, 'w', encoding='utf-8') as f:
        json.dump(main_report, f, ensure_ascii=False, indent=2)
    
    # Salva relatórios detalhados por roteiro
    for script_name, script_reports in reports.items():
        script_dir = output_dir / "detailed_reports" / script_name
        script_dir.mkdir(parents=True, exist_ok=True)
        
        for platform, report in script_reports.items():
            report_file = script_dir / f"{platform.value}_validation.json"
            
            # Converte relatório para formato serializável
            # Cria um validador temporário para serializar issues
            temp_validator = ScriptValidator()
            
            report_data = {
                "timestamp": report.timestamp.isoformat(),
                "script_title": report.script.title,
                "platform": report.platform.value,
                "overall_score": report.overall_score,
                "quality_level": report.quality_level.value,
                "is_approved": report.is_approved,
                "structure_validation": {
                    "score": report.structure_validation.score,
                    "is_valid": report.structure_validation.is_valid,
                    "issues": [temp_validator._issue_to_dict(issue) for issue in report.structure_validation.issues],
                    "suggestions": report.structure_validation.suggestions
                },
                "content_validation": {
                    "score": report.content_validation.score,
                    "is_valid": report.content_validation.is_valid,
                    "issues": [temp_validator._issue_to_dict(issue) for issue in report.content_validation.issues],
                    "suggestions": report.content_validation.suggestions
                },
                "platform_validation": {
                    "score": report.platform_validation.score,
                    "is_valid": report.platform_validation.is_valid,
                    "issues": [temp_validator._issue_to_dict(issue) for issue in report.platform_validation.issues],
                    "suggestions": report.platform_validation.suggestions
                },
                "quality_metrics": {
                    "clarity_score": report.quality_metrics.clarity_score,
                    "engagement_score": report.quality_metrics.engagement_score,
                    "retention_score": report.quality_metrics.retention_score,
                    "clarity_issues": [temp_validator._issue_to_dict(issue) for issue in report.quality_metrics.clarity_issues],
                    "engagement_issues": [temp_validator._issue_to_dict(issue) for issue in report.quality_metrics.engagement_issues],
                    "retention_issues": [temp_validator._issue_to_dict(issue) for issue in report.quality_metrics.retention_issues]
                },
                "all_issues": [temp_validator._issue_to_dict(issue) for issue in report.all_issues],
                "suggestions": report.suggestions,
                "summary": report.get_summary()
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 RELATÓRIOS SALVOS:")
    print(f"   📄 Relatório principal: {main_file}")
    print(f"   📁 Relatórios detalhados: {output_dir}/detailed_reports/")
    
    return main_file


def demonstrate_quality_insights(validator: ScriptValidator, reports: Dict[str, Dict[PlatformType, Any]]):
    """Demonstra insights sobre qualidade dos roteiros."""
    print(f"\n🔍 INSIGHTS DE QUALIDADE")
    print("=" * 50)
    
    # Análise comparativa
    all_scores = []
    quality_levels = []
    approved_count = 0
    total_issues = 0
    
    for script_reports in reports.values():
        for report in script_reports.values():
            all_scores.append(report.overall_score)
            quality_levels.append(report.quality_level.value)
            if report.is_approved:
                approved_count += 1
            total_issues += len(report.all_issues)
    
    total_reports = len(all_scores)
    
    # Estatísticas gerais
    print(f"📊 ESTATÍSTICAS GERAIS:")
    print(f"   Total de validações: {total_reports}")
    print(f"   Score médio: {sum(all_scores)/len(all_scores):.1f}/100")
    print(f"   Score mais alto: {max(all_scores):.1f}/100")
    print(f"   Score mais baixo: {min(all_scores):.1f}/100")
    print(f"   Roteiros aprovados: {approved_count}/{total_reports} ({approved_count/total_reports*100:.1f}%)")
    print(f"   Total de problemas encontrados: {total_issues}")
    
    # Distribuição por nível de qualidade
    quality_distribution = {}
    for level in quality_levels:
        quality_distribution[level] = quality_distribution.get(level, 0) + 1
    
    print(f"\n🎯 DISTRIBUIÇÃO POR NÍVEL DE QUALIDADE:")
    for level, count in quality_distribution.items():
        percentage = count / total_reports * 100
        print(f"   {level.upper()}: {count} ({percentage:.1f}%)")
    
    # Recomendações gerais
    print(f"\n💡 RECOMENDAÇÕES GERAIS:")
    
    avg_score = sum(all_scores) / len(all_scores)
    if avg_score >= 80:
        print("   ✅ Qualidade geral excelente! Continue assim.")
    elif avg_score >= 60:
        print("   🟡 Qualidade geral boa, mas há espaço para melhorias.")
    else:
        print("   ❌ Qualidade geral precisa de atenção. Revise a estratégia.")
    
    # Identifica problemas mais comuns
    all_issues_text = []
    for script_reports in reports.values():
        for report in script_reports.values():
            all_issues_text.extend([issue.code for issue in report.all_issues])
    
    if all_issues_text:
        issue_frequency = {}
        for issue_code in all_issues_text:
            issue_frequency[issue_code] = issue_frequency.get(issue_code, 0) + 1
        
        most_common = sorted(issue_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
        
        print(f"\n⚠️  PROBLEMAS MAIS COMUNS:")
        for i, (issue_code, count) in enumerate(most_common, 1):
            print(f"   {i}. {issue_code}: {count} ocorrências")


def main():
    """Função principal de demonstração."""
    print("🎬 DEMONSTRAÇÃO DO SISTEMA DE VALIDAÇÃO DE ROTEIROS")
    print("=" * 60)
    print("AiShorts v2.0 - Módulo 6: Sistema de Validação de Roteiro")
    print("=" * 60)
    
    # Inicializa validador
    print("\n🔧 Inicializando sistema de validação...")
    validator = ScriptValidator()
    print("✅ Validador inicializado com sucesso!")
    
    # Cria roteiros de exemplo
    print("\n📝 Preparando roteiros para validação...")
    scripts = create_sample_scripts()
    print(f"✅ {len(scripts)} roteiros preparados!")
    
    # Análise individual dos roteiros
    print(f"\n🔍 ANÁLISE DETALHADA DOS ROTEIROS")
    print("=" * 50)
    
    reports = {}
    
    for script_name, script in scripts.items():
        print(f"\n📋 Analisando: {script_name.upper().replace('_', ' ')}")
        print(f"   Título: {script.title}")
        print(f"   Tema: {script.theme.content}")
        print(f"   Duração: {script.total_duration}s")
        
        # Validação individual (TikTok)
        single_report = demonstrate_single_platform_validation(validator, script)
        
        # Validação multiplataforma
        multi_reports = demonstrate_multiple_platform_validation(validator, script)
        
        reports[script_name] = multi_reports
    
    # Insights gerais
    demonstrate_quality_insights(validator, reports)
    
    # Salva relatórios
    print(f"\n💾 GERANDO RELATÓRIOS")
    print("=" * 30)
    
    output_dir = Path("data/validation_reports")
    main_report_file = save_comprehensive_report(reports, output_dir)
    
    # Resumo final
    print(f"\n🎉 DEMONSTRAÇÃO CONCLUÍDA!")
    print("=" * 40)
    print(f"✅ Sistema de validação totalmente funcional")
    print(f"✅ Validações para 3 plataformas (TikTok, Shorts, Reels)")
    print(f"✅ Análise de estrutura, conteúdo e qualidade")
    print(f"✅ Geração automática de sugestões")
    print(f"✅ Relatórios detalhados salvos")
    print(f"\n📁 Relatórios salvos em: {output_dir}")
    print(f"📄 Arquivo principal: {main_report_file.name}")
    
    print(f"\n🚀 PRÓXIMOS PASSOS:")
    print("   1. Integração com sistema de geração de roteiros")
    print("   2. Validação automática pós-geração") 
    print("   3. Feedback loop para melhoria contínua")
    print("   4. Dashboard de métricas de qualidade")


if __name__ == "__main__":
    main()
