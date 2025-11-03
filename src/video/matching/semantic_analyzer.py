"""
Analisador semântico para roteiros - AiShorts v2.0
Sistema de análise semântica para extração de palavras-chave e categorização
"""

import re
import string
from typing import List, Dict, Any, Optional
import numpy as np
from collections import Counter
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Tentar importar spaCy, se não disponível usar implementação alternativa
try:
    import spacy
    SPACY_AVAILABLE = True
    logger.info("spaCy detectado, usando modelo completo")
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy não disponível, usando análise básica")


class SemanticAnalyzer:
    """
    Analisador semântico para processamento de roteiros.
    
    Features:
    - Extração de palavras-chave
    - Análise de tom emocional
    - Categorização de conteúdo
    - Geração de embeddings semânticos
    - Processamento de objetos Script
    """
    
    def __init__(self):
        """Inicializa o analisador semântico."""
        self.logger = logging.getLogger(__name__)
        
        # Palavras de parada em português
        self.stop_words = {
            'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'da', 'do', 'dos', 'das',
            'em', 'no', 'na', 'nos', 'nas', 'por', 'para', 'com', 'que', 'se', 'não', 'é',
            'e', 'ou', 'mas', 'como', 'já', 'muito', 'mais', 'menos', 'bem', 'mal', 'ao',
            'pelo', 'pela', 'pelos', 'pelas', 'dele', 'dela', 'eles', 'elas', 'nosso', 'nossa',
            'seu', 'sua', 'seus', 'suas', 'este', 'esta', 'estes', 'estas', 'esse', 'essa',
            'esses', 'essas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'este', 'aquilo'
        }
        
        # Dicionário de palavras-chave por categoria
        self.category_keywords = {
            'SPACE': {
                'sol', 'lua', 'estrela', 'galáxia', 'universo', 'planeta', 'satélite', 'foguete',
                'astronauta', 'espaço', 'orbit', 'nasa', 'júpiter', 'marte', 'venus', 'saturno',
                'neptuno', 'urano', 'plutão', 'cometa', 'asteróide', 'meteorito', 'galáxias',
                'nebulosas', 'buraco negro', 'via láctea', 'sistema solar'
            },
            'ANIMALS': {
                'cachorro', 'gato', 'elefante', 'leão', 'tigre', 'urso', 'panda', 'golfinho',
                'baleia', 'passaro', 'papagaio', 'pato', 'ganso', 'cavalo', 'vaca', 'boi',
                'porco', 'ovelha', 'bode', 'coelho', 'camundongo', 'rato', 'galo', 'galinha',
                'macaco', 'gorila', 'chimpanzé', 'zebra', 'girafa', 'hipopótamo', 'rinoceronte'
            },
            'SCIENCE': {
                'experimento', 'laboratório', 'científico', 'pesquisa', 'descoberta', 'teoria',
                'hipótese', 'método', 'análise', 'resultado', 'dados', 'química', 'física',
                'biologia', 'matemática', 'genética', 'evolução', 'microscópio', 'telescópio',
                'fórmula', 'lei', 'princípio', 'conceito', 'estudo', 'observação'
            },
            'NATURE': {
                'floresta', 'árvore', 'planta', 'flor', 'folha', 'raiz', 'semente', 'fruto',
                'montanha', 'rio', 'mar', 'oceano', 'lago', 'praia', 'deserto', 'caverna',
                'vale', 'canyon', 'água', 'fogo', 'ar', 'terra', 'vento', 'chuva', 'sol',
                'nuvem', 'céu', ' lua', 'estrela', 'natureza', 'ambiente', 'ecossistema'
            },
            'HISTORY': {
                'história', 'passado', 'antigo', 'medieval', 'moderno', 'império', 'rei',
                'rainha', 'castelo', 'catedral', 'monumento', 'guerra', 'batalha', 'revolução',
                'independência', 'colônia', 'descoberta', 'explorador', 'conquistador',
                'nascimento', 'morte', 'época', 'século', 'ano', 'data', 'evento'
            },
            'TECHNOLOGY': {
                'tecnologia', 'computador', 'internet', 'software', 'hardware', 'aplicativo',
                'sistema', 'programa', 'código', 'algoritmo', 'inteligência artificial',
                'robô', 'automação', 'digital', 'eletrônico', 'máquina', 'dispositivo',
                'conexão', 'dados', 'informação', 'rede', 'website', 'app', 'smartphone'
            },
            'CULTURE': {
                'cultura', 'arte', 'música', 'pintura', 'escultura', 'dança', 'teatro',
                'cinema', 'livro', 'poesia', 'literatura', 'filosofia', 'religião',
                'tradição', 'costume', 'festividade', 'comida', 'bebida', 'vestimenta'
            },
            'PSYCHOLOGY': {
                'psicologia', 'mente', 'emoção', 'sentimento', 'comportamento', 'personalidade',
                'caráter', 'temperamento', 'motivação', 'desejo', 'medo', 'alegria', 'tristeza',
                'raiva', 'amor', 'ódio', 'simpatia', 'antipatia', 'consciência', 'subconsciente'
            },
            'GEOGRAPHY': {
                'geografia', 'país', 'cidade', 'estado', 'região', 'continente', 'ocean',
                'montanha', 'rio', 'lago', 'deserto', 'floresta', 'planície', 'planeta',
                'latitude', 'longitude', 'clima', 'temperatura', 'população', 'demo'
            },
            'FOOD': {
                'comida', 'alimento', 'prato', 'refeição', 'café', 'chá', 'suco', 'água',
                'pão', 'arroz', 'feijão', 'carne', 'peixe', 'frango', 'verdura', 'fruta',
                'doce', 'salgado', 'bom', 'delicioso', 'sabor', 'ingrediente', 'receita',
                'cozinha', 'restaurante', 'chef', 'cozinheiro', 'comer', 'beber', 'fome'
            }
        }
        
        # Dicionário de emoções
        self.emotion_keywords = {
            'positive': {
                'alegria', 'felicidade', 'amor', 'prazer', 'satisfação', 'orgulho', 'esperança',
                'entusiasmo', 'euforia', 'êxtase', 'contentamento', 'benefício', 'sucesso',
                'vitória', 'triunfo', 'conquista', 'realização', 'progresso', 'evolução',
                'feliz', 'animado', 'incrível', 'maravilhoso', 'excelente', 'fantástico',
                'surpreendente', 'genial', 'brilhante', 'perfeito', 'maravilha', 'discoberta'
            },
            'negative': {
                'tristeza', 'depressão', 'angústia', 'sofrimento', 'dor', 'mágoa', 'desespero',
                'raiva', 'ódio', 'ressentimento', 'vingança', 'ciúme', 'inveja', 'medo',
                'terror', 'pavor', 'pânico', 'ansiedade', 'preocupação', 'nervosismo',
                'triste', 'terrível', 'horrível', 'ruim', 'péssimo', 'pior', 'problema',
                'difícil', 'complicado', 'impossível', 'fracasso', 'preocupado'
            },
            'neutral': {
                'informação', 'dados', 'fato', 'conceito', 'processo', 'sistema', 'método',
                'análise', 'resultado', 'observação', 'estudo', 'pesquisa', 'investigação',
                'importante', 'interessante', 'relevante', 'significativo'
            }
        }
        
        # Inicializar spaCy se disponível
        self._init_spacy()
        
        self.logger.info("SemanticAnalyzer inicializado com sucesso")
    
    def _init_spacy(self):
        """Inicializa spaCy se disponível."""
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("pt_core_news_sm")
                self.logger.info("spaCy carregado com sucesso")
            except OSError:
                self.logger.warning("Modelo spaCy pt_core_news_sm não encontrado")
                self.logger.info("Usando análise textual básica")
                self.nlp = None
        else:
            self.nlp = None
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extrai palavras-chave do texto.
        
        Args:
            text: Texto para processar
            max_keywords: Número máximo de palavras-chave
            
        Returns:
            Lista de palavras-chave ordenadas por relevância
        """
        if not text or not text.strip():
            return []
        
        try:
            # Limpar e preparar texto
            clean_text = self._preprocess_text(text)
            
            if self.nlp is not None:
                # Usar spaCy se disponível
                return self._extract_keywords_spacy(clean_text, max_keywords)
            else:
                # Usar análise básica
                return self._extract_keywords_basic(clean_text, max_keywords)
                
        except Exception as e:
            self.logger.error(f"Erro ao extrair palavras-chave: {e}")
            return []
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocessa o texto para análise."""
        # Converter para minúsculas
        text = text.lower()
        
        # Remover pontuação e caracteres especiais
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remover espaços extras
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_keywords_spacy(self, text: str, max_keywords: int) -> List[str]:
        """Extrai palavras-chave usando spaCy."""
        doc = self.nlp(text)
        
        # Extrair substantivos, adjetivos e verbos relevantes
        keywords = []
        for token in doc:
            if (
                not token.is_stop
                and not token.is_punct
                and not token.is_space
                and len(token.text) > 2
                and (token.pos_ in ['NOUN', 'ADJ', 'VERB'])
            ):
                keywords.append(token.lemma_)
        
        # Contar frequência e retornar as mais relevantes
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(max_keywords)]
    
    def _extract_keywords_basic(self, text: str, max_keywords: int) -> List[str]:
        """Extrai palavras-chave usando análise básica."""
        # Dividir em palavras
        words = text.split()
        
        # Filtrar palavras válidas
        valid_words = []
        for word in words:
            word = word.strip().lower()
            if (
                len(word) > 2
                and word not in self.stop_words
                and word.isalpha()
            ):
                valid_words.append(word)
        
        # Contar frequência
        word_counts = Counter(valid_words)
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    def analyze_tone(self, text: str) -> Dict[str, float]:
        """
        Analisa o tom emocional do texto.
        
        Args:
            text: Texto para analisar
            
        Returns:
            Dicionário com scores de emoções
        """
        if not text or not text.strip():
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
        
        try:
            clean_text = self._preprocess_text(text)
            words = clean_text.split()
            
            emotion_scores = {
                'positive': 0.0,
                'negative': 0.0, 
                'neutral': 0.0
            }
            
            # Contar palavras de cada categoria emocional
            positive_count = sum(1 for word in words if word in self.emotion_keywords['positive'])
            negative_count = sum(1 for word in words if word in self.emotion_keywords['negative'])
            neutral_count = sum(1 for word in words if word in self.emotion_keywords['neutral'])
            
            total_emotional_words = positive_count + negative_count + neutral_count
            
            if total_emotional_words > 0:
                emotion_scores['positive'] = positive_count / len(words)
                emotion_scores['negative'] = negative_count / len(words)
                emotion_scores['neutral'] = neutral_count / len(words)
            else:
                emotion_scores['neutral'] = 1.0
            
            # Normalizar scores para somar 1.0
            total = sum(emotion_scores.values())
            if total > 0:
                emotion_scores = {k: v/total for k, v in emotion_scores.items()}
            
            return emotion_scores
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar tom: {e}")
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
    
    def categorize_content(self, text: str) -> Dict[str, float]:
        """
        Categoriza o conteúdo do texto.
        
        Args:
            text: Texto para categorizar
            
        Returns:
            Dicionário com scores de categoria
        """
        if not text or not text.strip():
            return {'UNKNOWN': 1.0}
        
        try:
            clean_text = self._preprocess_text(text)
            words = set(clean_text.split())
            
            category_scores = {}
            
            # Calcular scores para cada categoria
            for category, keywords in self.category_keywords.items():
                matches = len(words.intersection(keywords))
                if keywords:
                    score = matches / len(keywords)
                else:
                    score = 0.0
                category_scores[category] = score
            
            # Normalizar scores
            total_score = sum(category_scores.values())
            if total_score > 0:
                category_scores = {k: v/total_score for k, v in category_scores.items()}
            
            # Se nenhuma categoria teve matches significativos, marcar como UNKNOWN
            if max(category_scores.values()) < 0.01:
                return {'UNKNOWN': 1.0}
            
            return category_scores
            
        except Exception as e:
            self.logger.error(f"Erro ao categorizar conteúdo: {e}")
            return {'UNKNOWN': 1.0}
    
    def get_semantic_embedding(self, text: str, use_clip: bool = True) -> Optional[np.ndarray]:
        """
        Gera embedding semântico do texto usando CLIP se disponível.
        
        Args:
            text: Texto para processar
            use_clip: Se deve usar CLIP quando disponível
            
        Returns:
            Array numpy com embedding ou None se falhar
        """
        if not text or not text.strip():
            return None
        
        try:
            # Tentar usar CLIP se disponível e solicitado
            if use_clip:
                clip_embedding = self._get_clip_embedding(text)
                if clip_embedding is not None:
                    return clip_embedding
            
            # Fallback para embedding básico
            return self._get_basic_embedding(text)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar embedding: {e}")
            return self._get_basic_embedding(text)
    
    def _get_clip_embedding(self, text: str) -> Optional[np.ndarray]:
        """Gera embedding usando CLIP se disponível."""
        try:
            # Lazy import para evitar dependência obrigatória
            from .clip_relevance_scorer import CLIPRelevanceScorer
            
            # Usar instância global ou criar nova
            if not hasattr(self, '_clip_scorer'):
                self._clip_scorer = CLIPRelevanceScorer()
            
            return self._clip_scorer.get_text_embedding(text)
            
        except Exception as e:
            self.logger.debug(f"CLIP não disponível para embedding: {e}")
            return None
    
    def _get_basic_embedding(self, text: str) -> np.ndarray:
        """Gera embedding básico usando características manuais."""
        # Extrair características básicas do texto
        keywords = self.extract_keywords(text, max_keywords=20)
        tone_scores = self.analyze_tone(text)
        category_scores = self.categorize_content(text)
        
        # Criar vetor de características
        features = []
        
        # Adicionar palavras-chave como one-hot
        all_category_keywords = set()
        for keywords_set in self.category_keywords.values():
            all_category_keywords.update(keywords_set)
        
        for keyword in all_category_keywords:
            features.append(1.0 if keyword in keywords else 0.0)
        
        # Adicionar scores de tom
        features.extend([
            tone_scores['positive'],
            tone_scores['negative'],
            tone_scores['neutral']
        ])
        
        # Adicionar scores de categoria
        for category in self.category_keywords.keys():
            features.append(category_scores.get(category, 0.0))
        
        # Normalizar vetor
        embedding = np.array(features, dtype=np.float32)
        if np.linalg.norm(embedding) > 0:
            embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    def process_script(self, script) -> Dict[str, Any]:
        """
        Processa um objeto Script completo.
        
        Args:
            script: Objeto Script do AiShorts v2.0
            
        Returns:
            Dicionário com análise completa do roteiro
        """
        try:
            # Obter texto completo
            if hasattr(script, 'get_full_text'):
                full_text = script.get_full_text()
            else:
                # Fallback para objetos sem método get_full_text
                sections_text = []
                for section in getattr(script, 'sections', []):
                    if hasattr(section, 'content'):
                        sections_text.append(section.content)
                    elif isinstance(section, dict) and 'content' in section:
                        sections_text.append(section['content'])
                full_text = ' '.join(sections_text)
            
            # Analisar texto completo
            script_id = 'unknown'
            if hasattr(script, 'id'):
                script_id = script.id
            elif isinstance(script, dict) and 'id' in script:
                script_id = script['id']
            
            analysis = {
                'script_id': script_id,
                'keywords': self.extract_keywords(full_text),
                'tone': self.analyze_tone(full_text),
                'categories': self.categorize_content(full_text),
                'embedding': self.get_semantic_embedding(full_text).tolist() if self.get_semantic_embedding(full_text) is not None else None,
                'text_length': len(full_text),
                'word_count': len(full_text.split())
            }
            
            # Analisar seções individualmente
            sections_analysis = []
            for section in getattr(script, 'sections', []):
                section_content = ""
                section_type = ""
                
                if hasattr(section, 'content'):
                    section_content = section.content
                    section_type = getattr(section, 'type', 'unknown')
                elif isinstance(section, dict):
                    section_content = section.get('content', '')
                    section_type = section.get('type', 'unknown')
                
                if section_content:
                    section_analysis = {
                        'type': section_type,
                        'keywords': self.extract_keywords(section_content),
                        'tone': self.analyze_tone(section_content),
                        'categories': self.categorize_content(section_content),
                        'length': len(section_content)
                    }
                    sections_analysis.append(section_analysis)
            
            analysis['sections'] = sections_analysis
            
            # Adicionar informações do tema se disponível
            if hasattr(script, 'theme'):
                theme = script.theme
                analysis['theme_title'] = getattr(theme, 'main_title', '')
                analysis['theme_category'] = str(getattr(theme, 'category', ''))
                analysis['theme_keywords'] = getattr(theme, 'keywords', [])
            
            self.logger.info(f"Análise completa do roteiro {analysis['script_id']} finalizada")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erro ao processar roteiro: {e}")
            return {
                'script_id': getattr(script, 'id', 'error'),
                'error': str(e),
                'keywords': [],
                'tone': {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0},
                'categories': {'UNKNOWN': 1.0},
                'embedding': None,
                'text_length': 0,
                'word_count': 0,
                'sections': []
            }


# Exemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Testar analisador
    analyzer = SemanticAnalyzer()
    
    # Texto de exemplo
    texto_exemplo = """
    O universo é cheio de mistérios fascinantes. As estrelas brilhantes no céu noturno 
    nos fazem pensar sobre nossa existência. A lua é um satélite natural da Terra que 
    influencia as marés dos oceanos. Os cientistas estudam constantemente os fenômenos 
    cósmicos para entender melhor o espaço.
    """
    
    print("=== Teste do SemanticAnalyzer ===")
    print(f"Texto: {texto_exemplo.strip()}")
    print()
    
    # Extrair palavras-chave
    keywords = analyzer.extract_keywords(texto_exemplo)
    print(f"Palavras-chave: {keywords}")
    print()
    
    # Analisar tom
    tone = analyzer.analyze_tone(texto_exemplo)
    print(f"Tom emocional: {tone}")
    print()
    
    # Categorizar conteúdo
    categories = analyzer.categorize_content(texto_exemplo)
    print(f"Categorias: {categories}")
    print()
    
    # Gerar embedding
    embedding = analyzer.get_semantic_embedding(texto_exemplo)
    if embedding is not None:
        print(f"Embedding: shape {embedding.shape}")
        print(f"Embedding (primeiros 10 valores): {embedding[:10]}")
    else:
        print("Embedding: None")
    
    print("\n=== Teste concluído ===")