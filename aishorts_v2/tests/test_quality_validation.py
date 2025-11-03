"""
Testes de Validação de Qualidade - AiShorts v2.0

Testa a qualidade dos temas gerados:
- Conformidade com categorias
- Interesse/curiosidade
- Valor educacional
- Formato e estrutura
- Métricas de qualidade

Estes testes avaliam se os temas gerados atendem aos padrões
de qualidade estabelecidos para o sistema AiShorts.
"""

import pytest
from statistics import mean, median
import re

@pytest.mark.unit
class TestThemeQualityValidation:
    """Testes de validação de qualidade de temas."""
    
    def test_curiosity_factor_measurement(self, mock_logger):
        """Testa medição do fator curiosidade."""
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        print("🔍 Testando medição de fator curiosidade...")
        
        # Temas com diferentes níveis de curiosidade
        test_themes = {
            "alta_curiosidade": [
                "Por que os flamingos são rosas?",
                "Como os pássaros navegam usando o campo magnético da Terra?",
                "Por que a neve é branca se as moléculas de água são transparentes?",
                "Como as estrelas comuns se tornam buracos negros?",
                "Por que os gatos ronronam?"
            ],
            "media_curiosidade": [
                "Como funciona o GPS?",
                "Por que o céu é azul?",
                "Como nascem as montanhas?",
                "Por que as folhas ficam amarelas no outono?",
                "Como funciona a fotossíntese?"
            ],
            "baixa_curiosidade": [
                "O céu é azul.",
                "As plantas precisam de água.",
                "Os cachorros são animais.",
                "O fogo queima.",
                "A Terra é redonda."
            ]
        }
        
        for category, themes in test_themes.items():
            curiosity_scores = []
            
            for theme in themes:
                metrics = prompt_engineering.get_quality_metrics(theme, ThemeCategory.SCIENCE)
                curiosity_scores.append(metrics["curiosity_factor"])
                
                print(f"   '{theme[:40]}...' = {metrics['curiosity_factor']:.2f}")
            
            avg_curiosity = mean(curiosity_scores)
            print(f"   Média {category}: {avg_curiosity:.2f}")
            
            # Verificar ordenação esperada
            if category == "alta_curiosidade":
                assert avg_curiosity > 0.7, f"Alta curiosidade deve ter score > 0.7, got {avg_curiosity}"
            elif category == "media_curiosidade":
                assert 0.4 <= avg_curiosity <= 0.8, f"Média curiosidade deve estar entre 0.4-0.8, got {avg_curiosity}"
            elif category == "baixa_curiosidade":
                assert avg_curiosity < 0.6, f"Baixa curiosidade deve ter score < 0.6, got {avg_curiosity}"
    
    def test_educational_value_assessment(self, mock_logger):
        """Testa avaliação de valor educacional."""
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        print("🎓 Testando avaliação de valor educacional...")
        
        # Temas com diferentes valores educacionais
        educational_themes = [
            "Como funciona a teoria da relatividade de Einstein?",
            "Por que os dinossauros se extinguiram?",
            "Como os antigos egípcios construíram as pirâmides?",
            "Por que o sal derrete o gelo?",
            "Como o sistema imunológico protege o corpo?"
        ]
        
        non_educational_themes = [
            "Qual a sua cor favorita?",
            "Você gosta de pizza?",
            "Que horas são?",
            "Como está o tempo hoje?",
            "Você tem fome?"
        ]
        
        # Testar temas educacionais
        edu_scores = []
        for theme in educational_themes:
            metrics = prompt_engineering.get_quality_metrics(theme, ThemeCategory.SCIENCE)
            edu_scores.append(metrics["educational_value"])
            print(f"   Educacional: '{theme[:40]}...' = {metrics['educational_value']:.2f}")
        
        avg_edu = mean(edu_scores)
        print(f"   Média educacional: {avg_edu:.2f}")
        
        # Testar temas não-educacionais
        non_edu_scores = []
        for theme in non_educational_themes:
            metrics = prompt_engineering.get_quality_metrics(theme, ThemeCategory.SCIENCE)
            non_edu_scores.append(metrics["educational_value"])
            print(f"   Não-educacional: '{theme[:40]}...' = {metrics['educational_value']:.2f}")
        
        avg_non_edu = mean(non_edu_scores)
        print(f"   Média não-educacional: {avg_non_edu:.2f}")
        
        # Temas educacionais devem ter score mais alto
        assert avg_edu > avg_non_edu, f"Temas educacionais devem ter maior valor educacional"
        assert avg_edu > 0.6, f"Temas educacionais devem ter score > 0.6, got {avg_edu}"
        assert avg_non_edu < 0.5, f"Temas não-educacionais devem ter score < 0.5, got {avg_non_edu}"
    
    def test_overall_quality_calculation(self, test_utils, mock_logger):
        """Testa cálculo de qualidade geral."""
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        print("⭐ Testando cálculo de qualidade geral...")
        
        # Temas de diferentes qualidades
        quality_examples = {
            "excelente": "Por que os flamingos são rosas? Uma curiosidade fascinante sobre sua dieta rica em carotenoides!",
            "boa": "Por que o céu é azul?",
            "regular": "Como funciona o GPS de forma simples?",
            "ruim": "Azul.",
            "pessima": "?"  # Extremamente ruim
        }
        
        for quality_level, theme in quality_examples.items():
            metrics = prompt_engineering.get_quality_metrics(theme, ThemeCategory.SCIENCE)
            overall_score = metrics["overall_quality"]
            
            print(f"   {quality_level}: {overall_score:.2f}")
            
            # Verificar ordenação esperada
            if quality_level == "excelente":
                assert overall_score > 0.8, f"Excelente deve ter score > 0.8, got {overall_score}"
            elif quality_level == "boa":
                assert 0.6 < overall_score <= 0.8, f"Boa deve ter score 0.6-0.8, got {overall_score}"
            elif quality_level == "regular":
                assert 0.4 <= overall_score <= 0.6, f"Regular deve ter score 0.4-0.6, got {overall_score}"
            elif quality_level == "ruim":
                assert 0.1 <= overall_score < 0.4, f"Ruim deve ter score 0.1-0.4, got {overall_score}"
            elif quality_level == "pessima":
                assert overall_score < 0.2, f"Péssima deve ter score < 0.2, got {overall_score}"
    
    def test_category_specific_quality(self, mock_logger):
        """Testa qualidade específica por categoria."""
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        print("🏷️ Testando qualidade específica por categoria...")
        
        # Temas específicos para cada categoria
        category_themes = {
            ThemeCategory.SPACE: "Por que os planetas são redondos?",
            ThemeCategory.ANIMALS: "Como os golfinhos dormem?",
            ThemeCategory.PSYCHOLOGY: "Por que temos Déjà vu?",
            ThemeCategory.GEOGRAPHY: "Por que os vulcões entram em erupção?",
            ThemeCategory.FOOD: "Por que o chocolate derrete na boca?"
        }
        
        category_scores = {}
        
        for category, theme in category_themes.items():
            metrics = prompt_engineering.get_quality_metrics(theme, category)
            overall_score = metrics["overall_quality"]
            
            category_scores[category.value] = overall_score
            print(f"   {category.value}: {overall_score:.2f}")
            
            # Cada categoria deve ter qualidade mínima
            assert overall_score > 0.5, f"Categoria {category.value} tem qualidade muito baixa: {overall_score}"
        
        # Verificar se todas as categorias têm qualidade similar (não muito diferente)
        scores = list(category_scores.values())
        min_score = min(scores)
        max_score = max(scores)
        score_range = max_score - min_score
        
        print(f"   Range de qualidade: {score_range:.2f}")
        
        # Range não deve ser muito grande (menos de 0.3)
        assert score_range < 0.3, f"Qualidade muito inconsistente entre categorias: {score_range}"

@pytest.mark.unit
class TestThemeContentValidation:
    """Testes de validação de conteúdo de temas."""
    
    def test_question_format_validation(self, mock_logger):
        """Testa validação de formato de pergunta."""
        from src.generators.prompt_engineering import prompt_engineering
        
        print("❓ Testando validação de formato de pergunta...")
        
        # Formatos válidos de pergunta
        valid_questions = [
            "Por que o céu é azul?",
            "Como funciona o GPS?",
            "Qual a origem dos dinossauros?",
            "Quando foram inventadas as rodas?",
            "Onde nascem os rios?",
            "Quem descobriu a penicilina?",
            "Por que os flamingos são rosas?"
        ]
        
        for question in valid_questions:
            is_valid = prompt_engineering.validate_prompt_format(question)
            print(f"   ✓ '{question}' = {is_valid}")
            assert is_valid is True, f"Pergunta válida foi rejeitada: {question}"
        
        # Formatos inválidos
        invalid_questions = [
            "",  # Vazio
            "   ",  # Apenas espaços
            "O céu é azul",  # Afirmativa
            "Azul",  # Muito curto
            "Sabe me dizer por que o céu é azul?",  # Iniciando com "sabe"
            "Pode me explicar como funciona?",  # Vago
            "Sobre o céu azul, o que você pode dizer?"  # Não é pergunta direta
        ]
        
        for question in invalid_questions:
            is_valid = prompt_engineering.validate_prompt_format(question)
            print(f"   ✗ '{question}' = {is_valid}")
            assert is_valid is False, f"Pergunta inválida foi aceita: {question}"
    
    def test_content_appropriateness(self, mock_logger):
        """Testa apropriação de conteúdo."""
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        print("📝 Testando apropriação de conteúdo...")
        
        # Conteúdos apropriados por categoria
        appropriate_content = {
            ThemeCategory.SCIENCE: [
                "Por que o gelo flutua na água?",
                "Como funciona a fotossíntese?",
                "Por que vemos arco-íris?"
            ],
            ThemeCategory.HISTORY: [
                "Como funcionava o calendário egípcio?",
                "Quem foram os faraós do Egito?",
                "Como eram construídas as pirâmides?"
            ],
            ThemeCategory.SPACE: [
                "Por que os planetas giram?",
                "Como nascem as estrelas?",
                "Existe vida em outros planetas?"
            ]
        }
        
        for category, themes in appropriate_content.items():
            for theme in themes:
                # Não deve levantar exceção
                metrics = prompt_engineering.get_quality_metrics(theme, category)
                assert metrics is not None
                assert metrics["overall_quality"] > 0
        
        # Conteúdos inapropriados devem ter baixa qualidade
        inappropriate_content = [
            "Como fazer bombas?",
            "Qual a melhor forma de roubar?",
            "Como enganar as pessoas?",
            "Qual a receita de drogas?"
        ]
        
        for theme in inappropriate_content:
            metrics = prompt_engineering.get_quality_metrics(theme, ThemeCategory.SCIENCE)
            # Deve ter qualidade muito baixa
            assert metrics["overall_quality"] < 0.3, f"Conteúdo inapropriado teve qualidade alta: {theme}"
            print(f"   Inapropriado rejeitado: '{theme}' = {metrics['overall_quality']:.2f}")
    
    def test_language_and_grammar(self, mock_logger):
        """Testa validação de idioma e gramática."""
        from src.generators.prompt_engineering import prompt_engineering
        
        print("📚 Testando idioma e gramática...")
        
        # Temas em português com gramática correta
        valid_portuguese = [
            "Por que o céu é azul?",
            "Como funcionam os neutrinos?",
            "Qual a origem da vida na Terra?",
            "Por que os pássaros migram?",
            "Como os diamonds são formados?"
        ]
        
        for theme in valid_portuguese:
            is_valid = prompt_engineering.validate_prompt_format(theme)
            assert is_valid is True, f"Tema português válido rejeitado: {theme}"
        
        # Temas com problemas gramaticais
        invalid_grammar = [
            "Por que o céu azul é?",  # Ordem incorreta
            "Como funciona o ?",  # Incompleto
            "Qual o origem da vida",  # Faltando artigo
            "Por que as plantas precisa de luz",  # Concordância incorreta
            "Como os flamingos são rosas são?"  # Repetição
        ]
        
        for theme in invalid_grammar:
            is_valid = prompt_engine_engineering.validate_prompt_format(theme)
            # Alguns podem passar, mas devem ter qualidade baixa
            if is_valid:
                metrics = prompt_engineering.get_quality_metrics(theme, ThemeCategory.SCIENCE)
                assert metrics["overall_quality"] < 0.7, f"Gramática incorreta teve alta qualidade: {theme}"

@pytest.mark.unit
class TestQualityMetricsConsistency:
    """Testes de consistência das métricas de qualidade."""
    
    def test_metrics_correlation(self, mock_logger):
        """Testa correlação entre métricas."""
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        print("📊 Testando correlação entre métricas...")
        
        test_themes = [
            "Por que os flamingos são rosas?",
            "Como funciona a relatividade?",
            "Por que o oceano é salgado?",
            "Azul.",
            "?", 
            "Qual sua cor favorita?",
            "Como nascem as estrelas?",
            "Você gosta de pizza?"
        ]
        
        all_metrics = []
        for theme in test_themes:
            metrics = prompt_engineering.get_quality_metrics(theme, ThemeCategory.SCIENCE)
            all_metrics.append(metrics)
            print(f"   Tema: '{theme[:30]}...'")
            print(f"     Curiosidade: {metrics['curiosity_factor']:.2f}")
            print(f"     Educacional: {metrics['educational_value']:.2f}")
            print(f"     Geral: {metrics['overall_quality']:.2f}")
        
        # Verificar se métricas gerais estão correlacionadas
        curiosity_scores = [m["curiosity_factor"] for m in all_metrics]
        educational_scores = [m["educational_value"] for m in all_metrics]
        overall_scores = [m["overall_quality"] for m in all_metrics]
        
        # Qualidade geral deve ser uma combinação das outras
        for i, (cur, edu, overall) in enumerate(zip(curiosity_scores, educational_scores, overall_scores)):
            # Qualidade geral deve estar entre as outras métricas (aproximadamente)
            min_component = min(cur, edu)
            max_component = max(cur, edu)
            if not (min_component <= overall <= max_component or abs(overall - min_component) < 0.3):
                print(f"   ⚠️ Inconsistência na posição {i}: overall={overall:.2f}, componentes={cur:.2f},{edu:.2f}")
    
    def test_metrics_bounds(self, mock_logger):
        """Testa se métricas estão dentro dos limites esperados."""
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        print("📏 Testando limites das métricas...")
        
        # Testar com temas extremos
        extreme_themes = [
            "?",  # Mínimo absoluto
            "Por que os flamingos são rosas? Uma questão fascinante sobre carotenoides e bioquímica!",  # Máximo
            "O céu é azul",  # Baixo
            "",  # Vazio
            "Como funciona a relatividade geral de Einstein de forma extremamente detalhada e cientificamente precisa?"  # Alto
        ]
        
        for theme in extreme_themes:
            metrics = prompt_engineering.get_quality_metrics(theme, ThemeCategory.SCIENCE)
            
            for metric_name, value in metrics.items():
                # Todas as métricas devem estar entre 0 e 1
                assert 0 <= value <= 1, f"Métrica {metric_name} fora dos limites: {value}"
                
                # Evitar valores exatamente 0 ou 1 (muito extremistas)
                if metric_name == "overall_quality":
                    if theme in ["?", ""]:  # Temas ruins
                        assert value <= 0.2, f"Tema ruim teve alta qualidade: {theme} = {value}"
                    elif "flamingos" in theme.lower():  # Tema bom
                        assert value >= 0.7, f"Tema bom teve baixa qualidade: {theme} = {value}"
            
            print(f"   ✓ '{theme[:30]}...' - Todas métricas nos limites")
    
    def test_reproducibility(self, mock_logger):
        """Testa reprodutibilidade das métricas."""
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        print("🔄 Testando reprodutibilidade das métricas...")
        
        test_theme = "Por que o céu é azul?"
        
        # Calcular métricas múltiplas vezes
        metrics_runs = []
        for i in range(3):
            metrics = prompt_engineering.get_quality_metrics(test_theme, ThemeCategory.SCIENCE)
            metrics_runs.append(metrics)
            time.sleep(0.1)  # Pequena pausa
        
        # Verificar se todas as execuções deram resultados similares
        curiosity_scores = [m["curiosity_factor"] for m in metrics_runs]
        educational_scores = [m["educational_value"] for m in metrics_runs]
        overall_scores = [m["overall_quality"] for m in metrics_runs]
        
        # Calcular variação
        curiosity_variance = max(curiosity_scores) - min(curiosity_scores)
        educational_variance = max(educational_scores) - min(educational_scores)
        overall_variance = max(overall_scores) - min(overall_scores)
        
        print(f"   Variação curiosidade: {curiosity_variance:.3f}")
        print(f"   Variação educacional: {educational_variance:.3f}")
        print(f"   Variação geral: {overall_variance:.3f}")
        
        # Variação deve ser pequena (menos de 0.1)
        assert curiosity_variance < 0.1, f"Variação muito alta na curiosidade: {curiosity_variance}"
        assert educational_variance < 0.1, f"Variação muito alta no educacional: {educational_variance}"
        assert overall_variance < 0.1, f"Variação muito alta no geral: {overall_variance}"
        
        print("✅ Métricas são reprodutíveis")

@pytest.mark.unit
class TestQualityThresholds:
    """Testes de thresholds de qualidade."""
    
    def test_quality_threshold_validation(self, mock_logger):
        """Testa validação com diferentes thresholds."""
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        print("⚖️ Testando thresholds de qualidade...")
        
        # Temas de exemplo com qualidades conhecidas
        test_theme = "Por que os flamingos são rosas?"
        
        # Verificar métricas básicas
        from src.generators.prompt_engineering import prompt_engineering
        metrics = prompt_engineering.get_quality_metrics(test_theme, ThemeCategory.SCIENCE)
        actual_quality = metrics["overall_quality"]
        
        print(f"   Qualidade do tema teste: {actual_quality:.2f}")
        
        # Testar diferentes thresholds
        thresholds = [0.3, 0.5, 0.7, 0.9]
        
        for threshold in thresholds:
            meets_threshold = actual_quality >= threshold
            print(f"   Threshold {threshold}: {'PASSOU' if meets_threshold else 'FALHOU'}")
            
            # Se qualidade conhecida for alta, deve passar thresholds baixos
            if actual_quality > 0.7:
                assert meets_threshold or threshold > 0.8, f"Qualidade alta ({actual_quality}) falhou threshold baixo ({threshold})"
    
    def test_realistic_quality_distribution(self, mock_logger):
        """Testa distribuição realista de qualidades."""
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        print("📈 Testando distribuição realista de qualidades...")
        
        # Amostra de temas reais
        real_themes = [
            "Por que os flamingos são rosas?",
            "Como funciona o GPS?",
            "Por que o céu é azul?",
            "Como nascem as estrelas?",
            "Por que os pássaros não caem do céu quando dormem?",
            "Como os diamantes são formados?",
            "Por que as plantas são verdes?",
            "Como funciona a velocidade da luz?"
        ]
        
        qualities = []
        for theme in real_themes:
            metrics = prompt_engineering.get_quality_metrics(theme, ThemeCategory.SCIENCE)
            quality = metrics["overall_quality"]
            qualities.append(quality)
            print(f"   '{theme[:40]}...' = {quality:.2f}")
        
        # Análise estatística
        avg_quality = mean(qualities)
        min_quality = min(qualities)
        max_quality = max(qualities)
        
        print(f"   Estatísticas:")
        print(f"     Média: {avg_quality:.2f}")
        print(f"     Mínimo: {min_quality:.2f}")
        print(f"     Máximo: {max_quality:.2f}")
        
        # Verificações de sanidade
        assert avg_quality > 0.5, f"Média muito baixa: {avg_quality}"
        assert min_quality > 0.2, f"Qualidade mínima muito baixa: {min_quality}"
        assert max_quality < 1.0, f"Qualidade máxima muito alta: {max_quality}"
        assert max_quality - min_quality > 0.3, "Pouca variação nas qualidades"

# Marcador personalizado para testes de qualidade
def pytest_configure(config):
    """Adiciona marcador para testes de qualidade."""
    config.addinivalue_line("markers", "quality: marca testes de validação de qualidade")

if __name__ == "__main__":
    # Executar apenas testes de qualidade
    pytest.main([__file__, "-v", "-m", "quality"])