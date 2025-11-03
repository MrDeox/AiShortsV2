"""
Sistema de Prompt Engineering para AiShorts v2.0

Concentra todos os prompts especializados para geração de temas de curiosidades.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


class ThemeCategory(Enum):
    """Categorias de temas disponíveis."""
    SCIENCE = "science"
    HISTORY = "history" 
    NATURE = "nature"
    TECHNOLOGY = "technology"
    CULTURE = "culture"
    SPACE = "space"
    ANIMALS = "animals"
    PSYCHOLOGY = "psychology"
    GEOGRAPHY = "geography"
    FOOD = "food"


@dataclass
class ThemePrompt:
    """Template de prompt para geração de temas."""
    category: ThemeCategory
    system_message: str
    user_prompt_template: str
    quality_criteria: List[str]
    examples: List[str]


class PromptEngineering:
    """Sistema de prompts otimizados para cada categoria de tema."""
    
    def __init__(self):
        self.prompts = self._create_prompts()
    
    def _create_prompts(self) -> Dict[ThemeCategory, ThemePrompt]:
        """Cria prompts especializados para cada categoria."""
        
        # Sistema base para todos os temas
        base_system = """Você é um especialista em criar conteúdo viral para vídeos curtos de curiosidades.

Sua especialidade:
- Criar temas que desperte curiosidade e surpreendam
- Temas que podem ser explicados em 30-60 segundos
- Conteúdo que é ao mesmo tempo educativo e fascinante
- Temas que geram "nossa, não sabia disso!" na audiência

Princípios:
1. Surpreendente - fatos pouco conhecidos
2. Acessível - fácil de entender
3. Memável - gera reactions
4. Universal - interessante para todos
5. Científico - baseado em fatos

Formato de resposta:
- Um tema por vez
- Máximo 2 frases
- Direto ao ponto
- Com gancho (curiosidade inicial)"""

        prompts = {
            
            ThemeCategory.SCIENCE: ThemePrompt(
                category=ThemeCategory.SCIENCE,
                system_message=base_system + """

Área de foco: DESCOBERTAS CIENTÍFICAS
- Fenômenos naturais surpreendentes
- Pesquisas recentes fascinantes
- Coisas que desafiam a intuição
- Mistérios da ciência ainda não resolvidos""",
                
                user_prompt_template="""Crie um tema de curiosidade científica que seja:

1. Pouco conhecido pelo público geral
2. Explicável em uma frase clara
3. Surpreendente o suficiente para gerar "que loucura!"
4. Baseado em pesquisa real

Categorias possíveis:
- Fenômenos físicos incríveis
- Descobertas biológicas surpreendentes
- Experimentos científicos desconcertantes
- Propriedades químicas inesperadas

Escolha uma das categorias e crie o tema:""",
                
                quality_criteria=[
                    "Base científico verificável",
                    "Surpreendente e Contra-intuitivo", 
                    "Fácil de explicar",
                    "Gera curiosidade imediata",
                    "Universalmente interessante"
                ],
                
                examples=[
                    "Por que o gelo é mais leve que a água?",
                    "Como as plantas 'sentem' quando estão sendo comidas?",
                    "Por que o espaço é tão silencioso?"
                ]
            ),
            
            ThemeCategory.HISTORY: ThemePrompt(
                category=ThemeCategory.HISTORY,
                system_message=base_system + """

Área de foco: HISTÓRIA POCO CONHECIDA
- Eventos históricos surpreendentes
- Personagens esquecidos pela história
- Curiosidades de culturas antigas
- Coincidências históricas impossíveis""",
                
                user_prompt_template="""Crie um tema histórico que seja:

1. Pouco conhecido pelo público geral
2. Surpreendente e interessante
3. Factualmente correto
4. Contável como uma história

Foque em:
- Eventos históricos que parecen ficção
- Personagens com destinos incríveis
- Situações históricas improváveis mas reais
- Curiosidades de períodos bem conhecidos

Escolha uma das opções e crie o tema:""",
                
                quality_criteria=[
                    "Fato histórico real",
                    "Surpreendente e pouco conhecido",
                    "Narrativa interessante",
                    "Factualmente preciso",
                    "Universalmente fascinante"
                ],
                
                examples=[
                    "O imperador que organizou os primeiros Jogos Olímpicos modernos",
                    "Como um médico salvou 2000 pessoas fingindo ter poder divino",
                    "A guerra que durou apenas 38 minutos"
                ]
            ),
            
            ThemeCategory.NATURE: ThemePrompt(
                category=ThemeCategory.NATURE,
                system_message=base_system + """

Área de foco: MUNDO NATURAL
- Comportamentos animais incríveis
- Fenômenos naturais surpreendentes
- Adaptações biológicas extraordinárias
- Criações da natureza que desafiam a lógica""",
                
                user_prompt_template="""Crie um tema da natureza que seja:

1. Relacionado ao mundo natural
2. Comportamento ou fenômeno real
3. Incrível e surpreendente
4. Fácil de visualizar

Foque em:
- Animais com habilidades impossíveis
- Plantas que se comportam como animais
- Fenômenos climáticos extremos
- Simbioses Naturais impressionantes

Escolha uma das opções e crie o tema:""",
                
                quality_criteria=[
                    "Fenômeno natural real",
                    "Visualmente impressionante",
                    "Comportamento ou característica única",
                    "Cientificamente preciso",
                    "Gera admiração imediata"
                ],
                
                examples=[
                    "O animal que pode vivir 10 meses sem respirar",
                    "Como as árvores 'conversam' através de fungos",
                    "Por que alguns peixes podem viver na lama seca"
                ]
            ),
            
            ThemeCategory.TECHNOLOGY: ThemePrompt(
                category=ThemeCategory.TECHNOLOGY,
                system_message=base_system + """

Área de foco: TECNOLOGIA E INOVAÇÃO
- Avanços tecnológicos surpreendentes
- Invenções que mudaram o mundo
- Tecnologias do futuro que já existem
- Como a tecnologia funciona internamente""",
                
                user_prompt_template="""Crie um tema tecnológico que seja:

1. Relacionado à tecnologia atual ou futura
2. Surpreendente sobre como as coisas funcionam
3. Acessível para leigos
4. Fascinante para tech enthusiasts

Foque em:
- Como a tecnologia funciona nos bastidores
- Invenções revolucionárias mas desconhecidas
- Tecnologias emergentes impressionantes
- Curiosidades sobre dispositivos que usamos

Escolha uma das opções e crie o tema:""",
                
                quality_criteria=[
                    "Informação tecnicamente precisa",
                    "Revelador sobre funcionamento interno",
                    "Aplicação prática clara",
                    "Fascina tanto leigos quanto experts",
                    "Atual e relevante"
                ],
                
                examples=[
                    "Como seu celular sabe exatamente onde você está",
                    "Por que a internet não quebra quando milhões usam ao mesmo tempo",
                    "A tecnologia que permite falar com IA em tempo real"
                ]
            ),
            
            ThemeCategory.CULTURE: ThemePrompt(
                category=ThemeCategory.CULTURE,
                system_message=base_system + """

Área de foco: CULTURA E SOCIEDADE
- Costumes e tradições Surpreendentes
- Culturas pouco conhecidas
- Comportamentos sociais interessante
- Evoluções culturais impressionantes""",
                
                user_prompt_template="""Crie um tema cultural que seja:

1. Relacionado a culture, society ou comportamento
2. Surpreendente sobre como vivemos
3. Intelectualmente interessante
4. Universalmente relateable

Foque em:
- Costumes de culturas diferentes
- Como a sociedade evolui
- Comportamentos humanos fascinantes
- Tradições que fazem sentido

Escolha uma das opções e crie o tema:""",
                
                quality_criteria=[
                    "Cultura ou behavior real",
                    "Revelador sobre nossa sociedade",
                    "Fomenta empatia cultural",
                    "Surpreendente mas respeitoso",
                    "Conecta com experiência humana"
                ],
                
                examples=[
                    "O país onde everybody dorme no mesmo horário",
                    "Como uma língua ganhou 1 milhão de novas palavras em 50 anos",
                    "A cultura que resolve disputas com jogos em vez de brigas"
                ]
            )
        }
        
        return prompts
    
    def get_prompt(self, category: ThemeCategory) -> ThemePrompt:
        """
        Retorna o prompt para uma categoria específica.
        
        Args:
            category: Categoria do tema
            
        Returns:
            Template de prompt para a categoria
        """
        return self.prompts.get(category)
    
    def get_all_categories(self) -> List[ThemeCategory]:
        """Retorna todas as categorias disponíveis."""
        return list(ThemeCategory)
    
    def create_generation_prompt(self, 
                                category: ThemeCategory,
                                custom_requirements: List[str] = None) -> Dict[str, str]:
        """
        Cria um prompt completo para geração de tema.
        
        Args:
            category: Categoria do tema
            custom_requirements: Requisitos adicionais específicos
            
        Returns:
            Dicionário com system_message e user_prompt
        """
        prompt_template = self.get_prompt(category)
        
        if not prompt_template:
            raise ValueError(f"Categoria {category} não encontrada")
        
        system_message = prompt_template.system_message
        user_prompt = prompt_template.user_prompt_template
        
        # Adicionar requisitos customizados se fornecidos
        if custom_requirements:
            requirements = "\n".join([f"- {req}" for req in custom_requirements])
            user_prompt += f"\n\nRequisitos adicionais:\n{requirements}"
        
        return {
            "system_message": system_message,
            "user_prompt": user_prompt,
            "category": category.value,
            "quality_criteria": prompt_template.quality_criteria
        }
    
    def validate_prompt_format(self, response: str) -> bool:
        """
        Valida se a resposta segue o formato esperado.
        
        Args:
            response: Resposta do modelo
            
        Returns:
            True se o formato é válido
        """
        # Verificações básicas de formato
        if not response or len(response.strip()) < 10:
            return False
        
        # Deve terminar com interrogação ou ter formato de pergunta
        if not response.strip().endswith('?'):
            return False
        
        # Não deve ser muito longo (não é roteiro, é tema)
        if len(response) > 200:
            return False
        
        return True
    
    def get_quality_metrics(self, response: str, category: ThemeCategory) -> Dict[str, Any]:
        """
        Calcula métricas de qualidade da resposta.
        
        Args:
            response: Resposta do modelo
            category: Categoria do tema
            
        Returns:
            Métricas de qualidade
        """
        prompt_template = self.get_prompt(category)
        metrics = {
            "length_ok": 10 <= len(response) <= 200,
            "has_question_mark": response.endswith('?'),
            "is_interrogative": response.endswith('?'),
            "category_relevant": True  # Assumindo que o modelo conhece a categoria
        }
        
        # Critérios específicos da categoria
        criteria_scores = []
        for criterion in prompt_template.quality_criteria:
            score = self._evaluate_criterion(response, criterion)
            criteria_scores.append({
                "criterion": criterion,
                "score": score
            })
        
        metrics["criteria_scores"] = criteria_scores
        metrics["overall_quality"] = sum(s["score"] for s in criteria_scores) / len(criteria_scores)
        
        return metrics
    
    def _evaluate_criterion(self, response: str, criterion: str) -> float:
        """
        Avalia um critério específico de qualidade.
        
        Args:
            response: Resposta do modelo
            criterion: Critério a avaliar
            
        Returns:
            Score de 0 a 1
        """
        # Implementação simples - pode ser expandida
        if "surpreendente" in criterion.lower():
            return 0.8  # Score médio alto parasurpresa
        
        elif "fácil" in criterion.lower():
            # Verifica se não tem termos muito técnicos
            technical_words = ["quântico", "bioquímica", "astrofísica", "neural"]
            has_technical = any(word in response.lower() for word in technical_words)
            return 0.9 if not has_technical else 0.6
        
        elif "científico" in criterion.lower():
            return 0.8  # Score médio para cientificidade
        
        else:
            return 0.7  # Score neutro para outros critérios


# Instância global do sistema de prompts
prompt_engineering = PromptEngineering()

if __name__ == "__main__":
    # Teste do sistema de prompts
    print("=== Sistema de Prompt Engineering ===")
    
    # Listar categorias
    categories = prompt_engineering.get_all_categories()
    print(f"Categorias disponíveis ({len(categories)}):")
    for cat in categories:
        print(f"  - {cat.value}")
    
    # Testar prompt para science
    print("\nTeste - Categoria Science:")
    science_prompt = prompt_engineering.create_generation_prompt(ThemeCategory.SCIENCE)
    print("System Message (primeiras linhas):")
    print(science_prompt["system_message"][:100] + "...")
    print("\nUser Prompt:")
    print(science_prompt["user_prompt"])
    
    # Testar validação
    print("\nValidação de formato:")
    good_response = "Por que o gelo é mais leve que a água?"
    bad_response = "O gelo é mais leve que a água porque a densidade é menor"
    
    print(f"Bom formato: {prompt_engineering.validate_prompt_format(good_response)}")
    print(f"Formato ruim: {prompt_engineering.validate_prompt_format(bad_response)}")
    
    # Testar métricas de qualidade
    print("\nMétricas de qualidade:")
    metrics = prompt_engineering.get_quality_metrics(good_response, ThemeCategory.SCIENCE)
    for key, value in metrics.items():
        print(f"  {key}: {value}")