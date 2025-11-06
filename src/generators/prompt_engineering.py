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
        base_system = """You are an expert content strategist for viral short-form curiosity videos.

Your expertise:
- Crafting hooks that spark instant curiosity
- Topics that can be explained in 30-60 seconds
- Stories that are educational, fun, and based on facts
- Narratives that trigger the reaction "no way, I didn't know that!"

Guiding principles:
1. Unexpected – highlight little-known facts
2. Accessible – easy to follow with no prior knowledge
3. Shareable – something people will repeat to friends
4. Universal – fascinating for any audience
5. Trustworthy – grounded in credible sources

Response format:
- Return exactly one topic
- Use at most two short sentences
- Be direct and conversational
- Open with a hook or surprising fact"""

        prompts = {
            
            ThemeCategory.SCIENCE: ThemePrompt(
                category=ThemeCategory.SCIENCE,
                system_message=base_system + """

Area of focus: SCIENCE DISCOVERIES
- Astonishing natural phenomena
- Fascinating recent research
- Findings that challenge intuition
- Unsolved scientific mysteries""",
                
                user_prompt_template="""Create a science curiosity topic that is:

1. Largely unknown to the general public
2. Explainable in one clear sentence
3. Surprising enough to provoke a "no way" reaction
4. Supported by real research or documented evidence

Possible angles:
- Mind-bending physics phenomena
- Counterintuitive biology discoveries
- Experiments with unbelievable outcomes
- Unexpected chemical properties

Choose one angle and craft the topic:""",
                
                quality_criteria=[
                    "Scientifically verifiable",
                    "Unexpected or counterintuitive",
                    "Explainable in plain language",
                    "Triggers instant curiosity",
                    "Widely interesting"
                ],
                
                examples=[
                    "The metal that melts in your hand without burning you",
                    "Plants that release a panic signal when pests attack",
                    "Why outer space is quieter than any vacuum chamber on Earth"
                ]
            ),
            
            ThemeCategory.HISTORY: ThemePrompt(
                category=ThemeCategory.HISTORY,
                system_message=base_system + """

Area of focus: HIDDEN HISTORY
- Astonishing real events
- Forgotten historical figures
- Surprising facts from ancient cultures
- Seemingly impossible coincidences""",
                
                user_prompt_template="""Create a history topic that is:

1. Rarely discussed in mainstream media
2. Dramatic or surprising enough to feel like fiction
3. Verified and historically accurate
4. Easy to retell as a miniature story

Focus on:
- Events that sound impossible but actually happened
- People with unbelievable life trajectories
- Improbable historical twists
- Hidden details of well-known eras

Pick one angle and craft the topic:""",
                
                quality_criteria=[
                    "Historically accurate",
                    "Little-known to general audiences",
                    "Naturally story-driven",
                    "Surprising or ironic",
                    "Globally interesting"
                ],
                
                examples=[
                    "The 38-minute war that still holds the record for shortest conflict",
                    "The doctor who saved thousands by pretending to be a prophet",
                    "How a chess-playing automaton fooled Europe for 80 years"
                ]
            ),
            
            ThemeCategory.NATURE: ThemePrompt(
                category=ThemeCategory.NATURE,
                system_message=base_system + """

Area of focus: WONDERS OF NATURE
- Incredible animal behaviors
- Surprising natural phenomena
- Extraordinary biological adaptations
- Nature-made marvels that defy logic""",
                
                user_prompt_template="""Create a nature topic that is:

1. Grounded in a real natural behavior or phenomenon
2. Visually compelling or easy to picture
3. Astonishing enough to feel like fantasy
4. Backed by documented observations

Focus on:
- Animals with "superpowers" nature can explain
- Plants behaving in shockingly animal-like ways
- Extreme or rare weather phenomena
- Mind-blowing symbiosis stories

Pick one focus and craft the topic:""",
                
                quality_criteria=[
                    "Rooted in real natural science",
                    "Easy to visualize",
                    "Highlights a unique trait or behavior",
                    "Scientifically accurate",
                    "Instantly awe-inspiring"
                ],
                
                examples=[
                    "The fish that survives by burying itself in mud for months",
                    "How trees trade nutrients through an underground fungus network",
                    "The jellyfish that can literally age backwards"
                ]
            ),
            
            ThemeCategory.TECHNOLOGY: ThemePrompt(
                category=ThemeCategory.TECHNOLOGY,
                system_message=base_system + """

Area of focus: TECHNOLOGY & INNOVATION
- Breakthroughs redefining daily life
- Inventions that feel futuristic but real
- Emerging tech hiding in plain sight
- Behind-the-scenes mechanics of gadgets""",
                
                user_prompt_template="""Create a technology topic that is:

1. About a real current or emerging technology
2. Surprising in how it actually works
3. Understandable for non-technical viewers
4. Exciting for tech enthusiasts and newbies alike

Focus on:
- The hidden systems powering everyday tech
- Revolutionary inventions people rarely hear about
- Emerging technologies with jaw-dropping potential
- Fascinating quirks of devices we use constantly

Choose one focus and craft the topic:""",
                
                quality_criteria=[
                    "Technically accurate information",
                    "Reveals a hidden or unexpected mechanism",
                    "Clear practical takeaway",
                    "Captivates both experts and beginners",
                    "Timely and relevant"
                ],
                
                examples=[
                    "How your phone triangulates your location within a few meters",
                    "Why the internet doesn't collapse when billions log on at once",
                    "The real tech that lets you talk to an AI in real time"
                ]
            ),
            
            ThemeCategory.CULTURE: ThemePrompt(
                category=ThemeCategory.CULTURE,
                system_message=base_system + """

Area of focus: CULTURE & SOCIETY
- Eye-opening customs and traditions
- Underrepresented cultures with big lessons
- Fascinating social behaviors
- Cultural shifts that explain the present""",
                
                user_prompt_template="""Create a culture topic that is:

1. Based on a real tradition, custom, or social behavior
2. Surprising in how people live, think, or celebrate
3. Thought-provoking yet respectful
4. Easy for a global audience to relate to

Focus on:
- Traditions from around the world with unexpected origins
- How societies evolve in clever or unusual ways
- Human behaviors that seem strange until you hear the story
- Everyday rituals that carry a deeper meaning

Choose one focus and craft the topic:""",
                
                quality_criteria=[
                    "Authentic cultural or social practice",
                    "Reveals something about humanity",
                    "Encourages cultural empathy",
                    "Surprising yet respectful",
                    "Connects to shared human experiences"
                ],
                
                examples=[
                    "The town that schedules citywide naps to keep the peace",
                    "How one language added a million new words in 50 years",
                    "The community that settles disputes through high-stakes board games"
                ]
            ),
            
            ThemeCategory.SPACE: ThemePrompt(
                category=ThemeCategory.SPACE,
                system_message=base_system + """

Area of focus: SPACE & ASTRONOMY
- Jaw-dropping cosmic phenomena
- Breakthrough space discoveries
- Mysteries hiding in plain sight
- Mind-bending facts about the cosmos""",
                
                user_prompt_template="""Create a space topic that is:

1. About a real cosmic object, mission, or discovery
2. Visually or conceptually mind-blowing
3. Scientifically accurate yet easy to follow
4. Guaranteed to amaze space-curious viewers

Focus on:
- Recent breakthroughs in space exploration
- Rare or extreme cosmic phenomena
- Mysteries scientists are still puzzling over
- Planet and star facts that shatter intuition

Choose one focus and craft the topic:""",
                
                quality_criteria=[
                    "Astronomically accurate information",
                    "Highlights our place in the universe",
                    "Engaging for both casual fans and experts",
                    "Reveals a surprising cosmic insight",
                    "Leaves viewers hungry to learn more"
                ],
                
                examples=[
                    "Why you don't feel Earth spinning at 1,000 mph",
                    "How scientists dated the universe to billions of years",
                    "What really happens if you fall into a black hole"
                ]
            ),
            
            ThemeCategory.ANIMALS: ThemePrompt(
                category=ThemeCategory.ANIMALS,
                system_message=base_system + """

Area of focus: ANIMAL BEHAVIOR
- Astonishing survival strategies
- Evolutionary superpowers
- Hidden social lives of animals
- Facts that flip our assumptions about wildlife""",
                
                user_prompt_template="""Create an animal topic that is:

1. Based on a documented real animal behavior
2. Surprising in how the species survives or interacts
3. Backed by scientific observation
4. Fascinating for animal lovers of any age

Focus on:
- Strange-but-true animal behaviors
- Evolutionary adaptations that seem impossible
- Unexpected social structures in the wild
- Survival tricks that feel like superpowers

Choose one focus and craft the topic:""",
                
                quality_criteria=[
                    "Documented animal behavior",
                    "Highlights surprising capabilities",
                    "Teaches something about wildlife",
                    "Inspires awe about nature",
                    "Engaging for experts and kids alike"
                ],
                
                examples=[
                    "How octopuses think with their arms",
                    "Why some birds perfectly mimic human speech",
                    "The secret message cats send when they stare at us"
                ]
            ),
            
            ThemeCategory.PSYCHOLOGY: ThemePrompt(
                category=ThemeCategory.PSYCHOLOGY,
                system_message=base_system + """

Area of focus: MIND & BEHAVIOR
- How the brain really works
- Surprising human habits
- Psychological curiosities
- Hidden mental processes guiding daily life""",
                
                user_prompt_template="""Create a psychology topic that is:

1. Grounded in peer-reviewed psychology or neuroscience
2. Reveals an unexpected truth about how we think or act
3. Easy to explain without jargon
4. Makes people reflect on their own behavior

Focus on:
- Automatic mental processes we never notice
- Unconscious behaviors with big effects
- Memory and perception quirks
- Ways the brain tricks or protects us

Choose one focus and craft the topic:""",
                
                quality_criteria=[
                    "Based on real psychological research",
                    "Highlights a surprising aspect of the mind",
                    "Intuitive once explained",
                    "Encourages self-reflection",
                    "Accepted by the scientific community"
                ],
                
                examples=[
                    "Why you can't tickle yourself no matter how hard you try",
                    "How your brain confidently creates false memories",
                    "The childhood smells your brain hardwires into nostalgia"
                ]
            ),
            
            ThemeCategory.GEOGRAPHY: ThemePrompt(
                category=ThemeCategory.GEOGRAPHY,
                system_message=base_system + """

Area of focus: GEOGRAPHY & PLACES
- Destinations that feel impossible
- One-of-a-kind geographic phenomena
- Hidden curiosities about our planet
- Locations that challenge intuition""",
                
                user_prompt_template="""Create a geography topic that is:

1. About a real place or natural phenomenon
2. Mind-blowing in what it reveals about Earth
3. Precise about location and context
4. Irresistible for curious travelers

Focus on:
- Places that look impossible on a map
- Geographic phenomena that defy expectations
- Curious facts about our planet's extremes
- Locations that flip our sense of scale or direction

Choose one focus and craft the topic:""",
                
                quality_criteria=[
                    "Geographically accurate information",
                    "Reveals a surprising facet of Earth",
                    "Sparks wanderlust",
                    "Delivers a memorable visual",
                    "Educational about our planet"
                ],
                
                examples=[
                    "The village where the sunset literally stops time for a moment",
                    "Why an entire lake glows bubblegum pink",
                    "How one mountain peak belongs to two countries at once"
                ]
            ),
            
            ThemeCategory.FOOD: ThemePrompt(
                category=ThemeCategory.FOOD,
                system_message=base_system + """

Area of focus: FOOD & CULINARY CULTURE
- Foods that sound fictional but are real
- Surprising facts about what we eat
- Culinary traditions with wild backstories
- Cooking techniques that defy expectations""",
                
                user_prompt_template="""Create a food topic that is:

1. About a real ingredient, dish, or culinary ritual
2. Unexpected or mind-bending in how it tastes or is prepared
3. Rich in cultural insight
4. Irresistible for curious food lovers

Focus on:
- Dishes that seem unreal until you see them
- Hidden science behind familiar ingredients
- Cultural rituals around cooking or eating
- Global twists on everyday foods

Choose one focus and craft the topic:""",
                
                quality_criteria=[
                    "Accurate culinary information",
                    "Reveals a surprising food insight",
                    "Culturally informative",
                    "Sparks appetite and curiosity",
                    "Highlights global food diversity"
                ],
                
                examples=[
                    "Why eating spicy food tricks your body into releasing painkillers",
                    "The festival where chefs cook with 700-year-old sourdough",
                    "The fruit that naturally grows on three continents at once"
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
