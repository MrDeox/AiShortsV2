"""
Testes Simplificados de Integração para AiShortsOrchestrator
Testa o fluxo completo com todos os componentes avançados integrados
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Teste básico de integração
def test_basic_integration():
    """Teste básico para verificar que os componentes podem ser importados"""
    print("🧪 Testando integração básica dos componentes...")
    
    try:
        # Testar imports básicos
        from src.models import (
            ThemeCategory, 
            GeneratedTheme, 
            ScriptSection, 
            GeneratedScript,
            validate_model_consistency,
            get_migration_info
        )
        print("✅ Models importados com sucesso")
        
        # Testar validação de modelos
        validation = validate_model_consistency()
        assert validation["status"] == "valid"
        print(f"✅ Validação de modelos: {validation['status']}")
        
        # Testar migração
        migration_info = get_migration_info()
        assert migration_info["compatibility_level"] == "full"
        print(f"✅ Compatibilidade: {migration_info['compatibility_level']}")
        
        # Criar tema de teste
        theme = GeneratedTheme(
            content="Animais incríveis da Amazônia",
            category=ThemeCategory.ANIMALS,
            quality_score=0.85,
            keywords=["amazon", "animals", "biodiversity"]
        )
        print(f"✅ Tema criado: {theme.content}")
        
        # Criar seções de teste
        sections = [
            ScriptSection(
                name="hook",
                content="Você sabia que a Amazônia abriga 10% de todas as espécies?",
                duration_seconds=5.0,
                purpose="capturar atenção"
            ),
            ScriptSection(
                name="development",
                content="A floresta amazônica tem uma biodiversidade incrível.",
                duration_seconds=45.0,
                purpose="informar"
            )
        ]
        print(f"✅ Seções criadas: {len(sections)}")
        
        # Criar script completo
        script = GeneratedScript(
            title="Animais da Amazônia",
            theme=theme,
            sections=sections,
            total_duration=50.0,
            quality_score=0.88
        )
        print(f"✅ Script criado: {script.title}")
        
        # Testar serialização
        script_dict = script.to_dict()
        print(f"✅ Script serializado: {len(script_dict)} campos")
        
        # Testar desserialização
        script_restored = GeneratedScript.from_dict(script_dict)
        print(f"✅ Script restaurado: {script_restored.title}")
        
        # Verificar consistência
        assert script.title == script_restored.title
        assert script.total_duration == script_restored.total_duration
        print("✅ Consistência verificada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste básico: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_script_validator_integration():
    """Teste de integração com ScriptValidator"""
    print("\n🔍 Testando integração com ScriptValidator...")
    
    try:
        from src.models import GeneratedTheme, ScriptSection, GeneratedScript, ThemeCategory
        from src.validators.script_validator import ScriptValidator, PlatformType
        
        # Criar script de teste
        theme = GeneratedTheme(
            content="Curiosidades sobre o espaço",
            category=ThemeCategory.SPACE,
            quality_score=0.9
        )
        
        sections = [
            ScriptSection(
                name="hook",
                content="Você sabia que o Sol representa 99.86% da massa do Sistema Solar?",
                duration_seconds=4.0,
                purpose="capturar atenção"
            ),
            ScriptSection(
                name="development",
                content="O Sol é uma estrela anã amarela que ilumina e aquece nosso planeta. Sem ele, não haveria vida na Terra.",
                duration_seconds=50.0,
                purpose="informar"
            ),
            ScriptSection(
                name="conclusion",
                content="Compartilhe esse fato incrível sobre o Sol com seus amigos!",
                duration_seconds=6.0,
                purpose="chamada à ação"
            )
        ]
        
        script = GeneratedScript(
            title="O Sol - A Estrela do Sistema Solar",
            theme=theme,
            sections=sections,
            total_duration=60.0,
            quality_score=0.85
        )
        
        # Criar validador
        validator = ScriptValidator()
        print("✅ ScriptValidator criado")
        
        # Validar script
        report = validator.validate_script(script, PlatformType.TIKTOK)
        print(f"✅ Script validado - Score: {report.overall_score:.2f}")
        print(f"   • Aprovado: {report.is_approved}")
        print(f"   • Nível: {report.quality_level.value}")
        print(f"   • Issues críticos: {len(report.get_critical_issues())}")
        
        # Testar validação multiplataforma
        reports = validator.validate_multiple_platforms(script)
        print(f"✅ Validação multiplataforma: {len(reports)} plataformas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do ScriptValidator: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_semantic_components():
    """Teste de componentes semânticos"""
    print("\n🧠 Testando componentes semânticos...")
    
    try:
        # Testar CLIPRelevanceScorer
        from src.video.matching.clip_relevance_scorer import CLIPRelevanceScorer
        
        scorer = CLIPRelevanceScorer()
        print("✅ CLIPRelevanceScorer criado (lazy loading)")
        
        # Testar ContentMatcher
        from src.video.matching.content_matcher import ContentMatcher
        
        matcher = ContentMatcher()
        print("✅ ContentMatcher criado")
        
        # Testar ClipPreValidator
        from src.video.validation.clip_pre_validator import ClipVideoPreValidator, VideoCandidate
        
        validator = ClipVideoPreValidator()
        print("✅ ClipVideoPreValidator criado")
        
        # Criar candidato de teste
        candidate = VideoCandidate(
            id="test123",
            title="Amazing Amazon Wildlife",
            description="Incredible animals from the Amazon rainforest",
            thumbnail_url="http://example.com/thumb.jpg",
            video_url="http://example.com/video.mp4",
            duration=120,
            view_count=1000000,
            upload_date="2024-01-01"
        )
        print("✅ VideoCandidate criado")
        
        # Testar fallback scoring
        score = validator._fallback_scoring(candidate, "amazon animals")
        print(f"✅ Fallback scoring: {score:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de componentes semânticos: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sync_components():
    """Teste de componentes de sincronização"""
    print("\n🎵 Testando componentes de sincronização...")
    
    try:
        # Testar AudioVideoSynchronizer
        from src.video.sync.audio_video_synchronizer import AudioVideoSynchronizer
        
        syncer = AudioVideoSynchronizer()
        print("✅ AudioVideoSynchronizer criado")
        
        # Testar TimingOptimizer
        from src.video.sync.timing_optimizer import TimingOptimizer
        
        optimizer = TimingOptimizer()
        print("✅ TimingOptimizer criado")
        
        # Testar otimização básica
        video_segments = [
            {"path": "video1.mp4", "duration": 10.0},
            {"path": "video2.mp4", "duration": 15.0}
        ]
        
        audio_timing = {
            "audio_path": "test_audio.wav",
            "total_duration": 30.0,
            "sections": [],
            "beat_points": [0.0, 5.0, 10.0, 15.0, 20.0, 25.0]
        }
        
        result = optimizer.optimize_transitions(video_segments, audio_timing)
        print(f"✅ Timing otimizado: {len(result.get('optimized_segments', []))} segmentos")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de componentes de sincronização: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_simplified_tests():
    """Executa testes simplificados de integração"""
    print("🧪 Executando Testes Simplificados de Integração")
    print("=" * 60)
    
    tests = [
        ("Integração Básica", test_basic_integration),
        ("ScriptValidator", test_script_validator_integration),
        ("Componentes Semânticos", test_semantic_components),
        ("Componentes de Sincronização", test_sync_components)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            if success:
                print(f"✅ {test_name}: PASS")
                passed += 1
            else:
                print(f"❌ {test_name}: FAIL")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Resumo: {passed} passaram, {failed} falharam")
    
    if failed == 0:
        print("🎉 Todos os testes passaram!")
        print("✅ Componentes integrados funcionando corretamente")
        print("✅ Models unificados consistentes")
        print("✅ Sistema pronto para uso avançado")
    else:
        print("⚠️ Alguns testes falharam. Verifique a implementação.")
    
    return failed == 0


if __name__ == "__main__":
    run_simplified_tests()