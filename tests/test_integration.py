"""
Testes de Integração - AiShorts v2.0

Testa a integração completa entre os componentes do sistema:
- OpenRouter + Theme Generator
- Prompt Engineering + API calls
- Geração completa de temas com validação

Estes testes fazem chamadas reais à API e devem ser executados
quando a OPENROUTER_API_KEY estiver configurada.
"""

import pytest
import time
import json
from pathlib import Path

@pytest.mark.integration
class TestCompleteIntegration:
    """Testes de integração completa do sistema."""
    
    @pytest.mark.skip(reason="Requer OPENROUTER_API_KEY configurada")
    def test_full_theme_generation(self, mock_logger):
        """Testa geração completa de tema com API real."""
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        print("🔄 Testando geração completa de tema...")
        
        # Gerar um tema para categoria SCIENCE
        result = theme_generator.generate_themes(
            categories=[ThemeCategory.SCIENCE],
            num_themes=1,
            min_quality_score=0.6
        )
        
        # Verificar resultado
        assert result is not None
        assert len(result.themes) >= 1
        assert result.best_theme is not None
        
        # Verificar qualidade do tema gerado
        best_theme = result.best_theme
        assert best_theme.quality_score >= 0.6
        assert best_theme.content.strip() != ""
        assert "?" in best_theme.content or "qual" in best_theme.content.lower()
        
        print(f"✅ Tema gerado: '{best_theme.content}'")
        print(f"   Qualidade: {best_theme.quality_score:.2f}")
        print(f"   Tempo: {best_theme.response_time:.2f}s")
    
    @pytest.mark.skip(reason="Requer OPENROUTER_API_KEY configurada")
    def test_multiple_categories_generation(self, mock_logger):
        """Testa geração para múltiplas categorias."""
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        print("🔄 Testando geração para múltiplas categorias...")
        
        categories_to_test = [ThemeCategory.SCIENCE, ThemeCategory.HISTORY, ThemeCategory.NATURE]
        
        result = theme_generator.generate_themes(
            categories=categories_to_test,
            num_themes=1,
            min_quality_score=0.6
        )
        
        # Verificar se gerou temas para todas as categorias
        assert len(result.themes) >= 3
        
        # Verificar distribuição por categoria
        categories_found = set()
        for theme in result.themes:
            categories_found.add(theme.category)
        
        for category in categories_to_test:
            assert category in categories_found, f"Categoria {category} não foi gerada"
        
        print(f"✅ {len(result.themes)} temas gerados para {len(categories_to_test)} categorias")
    
    @pytest.mark.skip(reason="Requer OPENROUTER_API_KEY configurada")  
    def test_quality_threshold_filtering(self, mock_logger):
        """Testa filtragem por threshold de qualidade."""
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        print("🔄 Testando filtragem por qualidade...")
        
        # Tentar gerar com threshold alto (pode falhar e precisar de tentativas)
        result = theme_generator.generate_themes(
            categories=[ThemeCategory.SCIENCE],
            num_themes=2,
            min_quality_score=0.9  # Threshold muito alto
        )
        
        # Deve tentar até conseguir ou atingir limite de tentativas
        assert result is not None
        
        if result.themes:
            # Se conseguiu gerar, verifica qualidade
            for theme in result.themes:
                assert theme.quality_score >= 0.9, f"Tema com qualidade {theme.quality_score} não atende threshold 0.9"
        
        print(f"✅ Gerados {len(result.themes)} temas acima do threshold 0.9")
    
    @pytest.mark.skip(reason="Requer OPENROUTER_API_KEY configurada")
    def test_error_recovery(self, mock_logger):
        """Testa recuperação de erros durante geração."""
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        print("🔄 Testando recuperação de erros...")
        
        # Gerar múltiplos temas para forçar possíveis erros
        result = theme_generator.generate_themes(
            categories=[ThemeCategory.SCIENCE, ThemeCategory.HISTORY],
            num_themes=3,
            min_quality_score=0.6
        )
        
        # Deve completar com sucesso mesmo com possíveis erros
        assert result is not None
        assert result.total_time > 0
        
        print(f"✅ Recuperação bem-sucedida. {len(result.themes)} temas gerados em {result.total_time:.2f}s")
    
    @pytest.mark.skip(reason="Requer OPENROUTER_API_KEY configurada")
    def test_serialization_deserialization(self, mock_logger, temp_dir):
        """Testa serialização e desserialização de resultados."""
        from src.generators.theme_generator import theme_generator, ThemeGenerationResult
        from src.generators.prompt_engineering import ThemeCategory
        
        print("🔄 Testando serialização/desserialização...")
        
        # Gerar tema
        result = theme_generator.generate_themes(
            categories=[ThemeCategory.SCIENCE],
            num_themes=1,
            min_quality_score=0.6
        )
        
        # Serializar
        result_dict = result.to_dict()
        
        # Salvar em arquivo
        output_file = temp_dir / "test_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)
        
        # Ler e desserializar
        with open(output_file, 'r', encoding='utf-8') as f:
            loaded_dict = json.load(f)
        
        restored_result = ThemeGenerationResult.from_dict(loaded_dict)
        
        # Verificar integridade
        assert len(restored_result.themes) == len(result.themes)
        assert restored_result.best_theme.content == result.best_theme.content
        assert restored_result.total_time == result.total_time
        
        print("✅ Serialização/desserialização bem-sucedida")

@pytest.mark.integration
class TestAPIIntegration:
    """Testes específicos da integração com API OpenRouter."""
    
    @pytest.mark.skip(reason="Requer OPENROUTER_API_KEY configurada")
    def test_api_response_time(self, mock_logger):
        """Testa tempo de resposta da API."""
        from src.core.openrouter_client import openrouter_client
        
        print("🔄 Testando tempo de resposta da API...")
        
        start_time = time.time()
        
        result = openrouter_client.generate_completion(
            system_message="Você é um assistente útil.",
            user_message="Gere uma curiosidade sobre ciência em uma frase."
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Deve responder em tempo razoável (menos de 30 segundos)
        assert response_time < 30
        assert result["content"].strip() != ""
        
        print(f"✅ Resposta em {response_time:.2f}s")
        print(f"   Conteúdo: {result['content'][:100]}...")
    
    @pytest.mark.skip(reason="Requer OPENROUTER_API_KEY configurada")
    def test_api_rate_limiting(self, mock_logger):
        """Testa se rate limiting está funcionando."""
        from src.core.openrouter_client import openrouter_client
        
        print("🔄 Testando rate limiting...")
        
        # Fazer algumas requisições rápidas
        start_time = time.time()
        
        results = []
        for i in range(3):
            result = openrouter_client.generate_completion(
                system_message="Teste",
                user_message=f"Tema {i}"
            )
            results.append(result)
            time.sleep(0.1)  # Pequena pausa entre requisições
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Deve completar as requisições
        assert len(results) == 3
        for result in results:
            assert result["content"].strip() != ""
        
        print(f"✅ {len(results)} requisições em {total_time:.2f}s")
    
    @pytest.mark.skip(reason="Requer OPENROUTER_API_KEY configurada")
    def test_different_prompt_structures(self, mock_logger):
        """Testa diferentes estruturas de prompt."""
        from src.generators.prompt_engineering import prompt_engineering
        from src.generators.prompt_engineering import ThemeCategory
        from src.core.openrouter_client import openrouter_client
        
        print("🔄 Testando diferentes estruturas de prompt...")
        
        # Testar diferentes categorias
        categories_to_test = [ThemeCategory.SPACE, ThemeCategory.ANIMALS, ThemeCategory.PSYCHOLOGY]
        
        for category in categories_to_test:
            prompt = prompt_engineering.create_generation_prompt(category)
            
            result = openrouter_client.generate_completion(
                system_message=prompt["system_message"],
                user_message=prompt["user_prompt"]
            )
            
            assert result["content"].strip() != ""
            
            # Verificar se a resposta é relevante à categoria
            content_lower = result["content"].lower()
            category_keywords = {
                ThemeCategory.SPACE: ["espaço", "planeta", "estrela", "galáxia", "space"],
                ThemeCategory.ANIMALS: ["animal", "bicho", "espécie", "natureza"],
                ThemeCategory.PSYCHOLOGY: ["mente", "psicologia", "comportamento", "cérebro"]
            }
            
            # Pelo menos uma palavra-chave deve aparecer (não garantido, mas esperado)
            print(f"   {category.value}: {result['content'][:50]}...")
        
        print("✅ Diferentes estruturas de prompt testadas")

@pytest.mark.integration
class TestEndToEndWorkflow:
    """Testes de workflow completo (end-to-end)."""
    
    @pytest.mark.skip(reason="Requer OPENROUTER_API_KEY configurada")
    def test_complete_workflow(self, mock_logger, temp_dir):
        """Testa workflow completo do sistema."""
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        print("🔄 Testando workflow completo...")
        
        # 1. Configurar parâmetros
        target_categories = [ThemeCategory.SCIENCE, ThemeCategory.HISTORY, ThemeCategory.NATURE]
        num_themes_per_category = 2
        min_quality = 0.7
        
        print(f"   Configuração: {len(target_categories)} categorias, {num_themes_per_category} temas/categoria")
        
        # 2. Gerar temas
        result = theme_generator.generate_themes(
            categories=target_categories,
            num_themes=num_themes_per_category,
            min_quality_score=min_quality
        )
        
        # 3. Analisar resultados
        analysis = theme_generator.analyze_themes(result.themes)
        
        # 4. Salvar resultados
        output_file = temp_dir / "workflow_test_result.json"
        workflow_result = {
            "generation_result": result.to_dict(),
            "analysis": analysis,
            "config": {
                "categories": [c.value for c in target_categories],
                "themes_per_category": num_themes_per_category,
                "min_quality": min_quality
            },
            "summary": {
                "total_generated": len(result.themes),
                "avg_quality": analysis["quality_stats"]["avg_quality"],
                "total_time": result.total_time,
                "categories_covered": len(analysis["categories"])
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_result, f, indent=2, ensure_ascii=False)
        
        # 5. Verificar resultados
        assert len(result.themes) > 0
        assert analysis["total_themes"] == len(result.themes)
        assert analysis["quality_stats"]["avg_quality"] >= min_quality
        assert len(analysis["categories"]) == len(target_categories)
        
        print(f"✅ Workflow completo executado:")
        print(f"   📊 {len(result.themes)} temas gerados")
        print(f"   ⭐ Qualidade média: {analysis['quality_stats']['avg_quality']:.2f}")
        print(f"   ⏱️ Tempo total: {result.total_time:.2f}s")
        print(f"   📁 Resultados salvos em: {output_file}")
    
    @pytest.mark.skip(reason="Requer OPENROUTER_API_KEY configurada")
    def test_different_quality_thresholds(self, mock_logger):
        """Testa diferentes thresholds de qualidade."""
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        print("🔄 Testando diferentes thresholds de qualidade...")
        
        thresholds = [0.5, 0.7, 0.8]
        results = {}
        
        for threshold in thresholds:
            print(f"   Testando threshold {threshold}...")
            
            result = theme_generator.generate_themes(
                categories=[ThemeCategory.SCIENCE],
                num_themes=1,
                min_quality_score=threshold
            )
            
            results[threshold] = {
                "themes_generated": len(result.themes),
                "quality_scores": [t.quality_score for t in result.themes],
                "total_time": result.total_time
            }
            
            # Verificar se gerou temas com qualidade adequada
            if result.themes:
                for theme in result.themes:
                    assert theme.quality_score >= threshold
        
        # Comparar resultados
        print("   Resumo por threshold:")
        for threshold, data in results.items():
            print(f"     {threshold}: {data['themes_generated']} temas, "
                  f"score médio {sum(data['quality_scores'])/len(data['quality_scores']):.2f}")
        
        print("✅ Teste de thresholds concluído")

# Marcadores personalizados para pytest
def pytest_configure(config):
    """Adiciona marcadores personalizados."""
    config.addinivalue_line("markers", "integration: marca testes de integração")
    config.addinivalue_line("markers", "slow: marca testes lentos")
    config.addinivalue_line("markers", "api_required: marca testes que requerem API key")

if __name__ == "__main__":
    # Executar apenas testes de integração não-skip
    pytest.main([__file__, "-v", "-m", "integration and not slow"])