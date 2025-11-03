"""
Analisador semântico para matching entre roteiro e vídeo.
Utiliza spaCy para processamento de linguagem natural em português.
"""

import spacy
import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import Counter
import re


class SemanticAnalyzer:
    """
    Classe para análise semântica de texto usando spaCy.
    Extrai palavras-chave, analisa tom emocional e categoriza conteúdo.
    """
    
    # Mapeamento de categorias para palavras-chave
    CATEGORY_KEYWORDS = {
        'SPACE': ['espaço', 'galáxia', 'planeta', 'estrela', 'universo', 'astronauta', 
                  'satélite', 'lua', 'sol', 'cosmos', 'astronomia', 'orbits', 'mars'],
        'ANIMALS': ['animal', 'cachorro', 'gato', 'leão', 'tigre', 'elefante', 'pássaro', 
                    'peixe', 'delfim', 'golfinho', 'baleia', 'tubarão', 'zebra', 'macaco'],
        'NATURE': ['natureza', 'floresta', 'árvore', 'flor', 'montanha', 'rio', 'mar', 
                   'praia', 'céu', 'nuvem', 'chuva', 'sol', 'vento', 'paisagem'],
        'TECHNOLOGY': ['tecnologia', 'robô', 'computador', 'internet', 'aplicativo', 
                       'software', 'hardware', 'AI', 'inteligência artificial', 'algoritmo'],
        'FOOD': ['comida', 'alimentação', 'prato', 'receita', 'cozinha', 'gastronomia', 
                 'ingrediente', 'doce', 'salgado', 'bebida', 'restaurante'],
        'SPORTS': ['esporte', 'futebol', 'basquete', 'vôlei', 'tênis', 'corrida', 'natação', 
                   'ginástica', 'olimpíadas', 'competição', 'atleta'],
        'MUSIC': ['música', 'cantor', 'banda', 'instrumento', 'guitarra', 'piano', 'bateria', 
                  'violão', 'show', 'concerto', 'festival', 'canção'],
        'EDUCATION': ['educação', 'ensino', 'aprendizado', 'escola', 'universidade', 'professor', 
                      'aluno', 'livro', 'curso', 'estudo', 'conhecimento'],
        'HEALTH': ['saúde', 'medicina', 'hospital', 'médico', 'doença', 'tratamento', 'remédio', 
                   'corpo', 'exercício', 'dieta', 'bem-estar', 'mental'],
        'TRAVEL': ['viagem', 'destino', 'turismo', 'cidade', 'país', 'continente', 'avião', 
                   'hotel', 'praia', 'montanha', 'cultura', 'aventura']
    }
    
    # Palavras de tom emocional positivo
    POSITIVE_WORDS = ['feliz', 'alegre', 'bonito', 'maravilhoso', 'excelente', 'fantástico', 
                      'incrível', 'espetacular', 'adorável', 'amor', 'paixão', 'diversão']
    
    # Palavras de tom emocional negativo
    NEGATIVE_WORDS = ['triste', 'feio', 'terrível', 'horrível', 'péssimo', 'ruim', 
                      'dor', 'sofrimento', 'guerra', 'conflito', 'problema', 'crise']
    
    # Palavras de tom emocional neutro
    NEUTRAL_WORDS = ['informação', 'dados', 'fato', 'conhecimento', 'estudo', 'análise', 
                     'pesquisa', 'descoberta', 'explicação', 'descrição']
    
    def __init__(self):
        """Inicializa o analisador semântico com modelo spaCy para português."""
        try:
            # Tenta carregar modelo português do spaCy
            self.nlp = spacy.load("pt_core_news_sm")
            self.use_spacy = True
            print("Modelo spaCy pt_core_news_sm carregado com sucesso.")
        except OSError:
            print("Modelo spaCy pt_core_news_sm não encontrado. Usando fallback básico.")
            self.use_spacy = False
            self.nlp = None
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """
        Extrai palavras-chave importantes do texto.
        
        Args:
            text (str): Texto para análise
            max_keywords (int): Número máximo de palavras-chave a retornar
            
        Returns:
            List[str]: Lista de palavras-chave extraídas
        """
        if self.use_spacy and self.nlp:
            return self._extract_keywords_spacy(text, max_keywords)
        else:
            return self._extract_keywords_fallback(text, max_keywords)
    
    def _extract_keywords_spacy(self, text: str, max_keywords: int) -> List[str]:
        """Extrai palavras-chave usando spaCy."""
        doc = self.nlp(text.lower())
        
        # Palavras a serem ignoradas
        stop_words = set(self.nlp.Defaults.stop_words)
        ignore_words = {'ser', 'estar', 'ter', 'fazer', 'ir', 'vir', 'dar', 'dizer', 'ver', 'saber'}
        stop_words.update(ignore_words)
        
        keywords = []
        
        # Extrai substantivos, adjetivos e verbos relevantes
        for token in doc:
            if (not token.is_stop and 
                not token.is_punct and 
                not token.is_space and
                len(token.text) > 2 and
                token.text not in stop_words and
                token.pos_ in ['NOUN', 'ADJ', 'VERB']):
                
                # Adiciona forma normalizada
                if token.lemma_ != token.text:
                    keywords.append(token.lemma_)
                else:
                    keywords.append(token.text)
        
        # Conta frequência e retorna as mais importantes
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(max_keywords)]
    
    def _extract_keywords_fallback(self, text: str, max_keywords: int) -> List[str]:
        """Extrai palavras-chave usando método básico (sem spaCy)."""
        # Lista básica de stop words em português
        basic_stop_words = {
            'a', 'o', 'e', 'é', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas',
            'para', 'por', 'com', 'como', 'que', 'se', 'não', 'sim', 'um', 'uma', 'uns', 'umas',
            'ser', 'estar', 'ter', 'fazer', 'ir', 'vir', 'dar', 'dizer', 'ver', 'saber',
            'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas',
            'aquele', 'aquela', 'aqueles', 'aquelas', 'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas'
        }
        
        # Remove pontuação e converte para minúsculas
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text_clean.split()
        
        # Filtra palavras relevantes
        keywords = []
        for word in words:
            if (len(word) > 2 and 
                word not in basic_stop_words and
                word.isalpha()):
                keywords.append(word)
        
        # Conta frequência e retorna as mais importantes
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(max_keywords)]
    
    def analyze_tone(self, text: str) -> Dict[str, float]:
        """
        Analisa o tom emocional do texto.
        
        Args:
            text (str): Texto para análise de tom
            
        Returns:
            Dict[str, float]: Dicionário com scores de tom (positivo, negativo, neutro)
        """
        text_lower = text.lower()
        
        if self.use_spacy and self.nlp:
            return self._analyze_tone_spacy(text_lower)
        else:
            return self._analyze_tone_fallback(text_lower)
    
    def _analyze_tone_spacy(self, text_lower: str) -> Dict[str, float]:
        """Analisa tom usando spaCy."""
        doc = self.nlp(text_lower)
        
        # Conta ocorrências de palavras de cada categoria
        positive_count = sum(1 for word in self.POSITIVE_WORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_WORDS if word in text_lower)
        neutral_count = sum(1 for word in self.NEUTRAL_WORDS if word in text_lower)
        
        # Conta também palavras extraídas do texto que podem indicar tom
        for token in doc:
            token_text = token.lemma_
            if token_text in self.POSITIVE_WORDS:
                positive_count += 1
            elif token_text in self.NEGATIVE_WORDS:
                negative_count += 1
            elif token_text in self.NEUTRAL_WORDS:
                neutral_count += 1
        
        total_words = positive_count + negative_count + neutral_count
        if total_words == 0:
            return {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
        
        return {
            'positive': positive_count / total_words,
            'negative': negative_count / total_words,
            'neutral': neutral_count / total_words
        }
    
    def _analyze_tone_fallback(self, text_lower: str) -> Dict[str, float]:
        """Analisa tom usando método básico."""
        # Conta ocorrências de palavras de cada categoria
        positive_count = sum(1 for word in self.POSITIVE_WORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_WORDS if word in text_lower)
        neutral_count = sum(1 for word in self.NEUTRAL_WORDS if word in text_lower)
        
        total_words = positive_count + negative_count + neutral_count
        if total_words == 0:
            return {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
        
        return {
            'positive': positive_count / total_words,
            'negative': negative_count / total_words,
            'neutral': neutral_count / total_words
        }
    
    def categorize_content(self, text: str) -> Tuple[str, float]:
        """
        Categoriza o conteúdo do texto em uma das categorias predefinidas.
        
        Args:
            text (str): Texto para categorização
            
        Returns:
            Tuple[str, float]: (categoria, score de confiança)
        """
        keywords = self.extract_keywords(text, max_keywords=50)
        text_lower = text.lower()
        
        category_scores = {}
        
        for category, category_keywords in self.CATEGORY_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in category_keywords:
                    score += 2  # Palavras-chave têm peso maior
            
            # Adiciona pontuação por presença no texto completo
            for keyword in category_keywords:
                if keyword in text_lower:
                    score += 1
            
            category_scores[category] = score
        
        if not category_scores or max(category_scores.values()) == 0:
            return 'GENERAL', 0.0
        
        best_category = max(category_scores, key=category_scores.get)
        max_score = category_scores[best_category]
        
        # Normaliza score de confiança (0-1)
        total_possible = len(keywords) * 2
        confidence = min(max_score / max(total_possible, 1), 1.0)
        
        return best_category, confidence
    
    def get_semantic_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Gera embedding semântico do texto usando spaCy.
        
        Args:
            text (str): Texto para embedding
            
        Returns:
            Optional[np.ndarray]: Vetor de embedding ou None se erro
        """
        if self.use_spacy and self.nlp:
            try:
                doc = self.nlp(text)
                if doc.has_vector:
                    return doc.vector
                else:
                    # Fallback: retorna vetor médio dos tokens
                    vectors = [token.vector for token in doc if token.has_vector]
                    if vectors:
                        return np.mean(vectors, axis=0)
                    else:
                        return None
            except Exception as e:
                print(f"Erro ao gerar embedding: {e}")
                return None
        else:
            return self._generate_fallback_embedding(text)
    
    def _generate_fallback_embedding(self, text: str) -> Optional[np.ndarray]:
        """Gera embedding básico usando hash de palavras."""
        words = text.lower().split()
        vector = np.zeros(300)  # Vetor de 300 dimensões para compatibilidade
        
        for i, word in enumerate(words[:300]):  # Limita a 300 palavras
            hash_val = hash(word) % 300
            vector[hash_val] += 1 / (i + 1)  # Palavras mais próximas têm peso maior
        
        return vector if np.any(vector) else None
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula similaridade semântica entre dois textos.
        
        Args:
            text1 (str): Primeiro texto
            text2 (str): Segundo texto
            
        Returns:
            float: Score de similaridade (0-1)
        """
        embedding1 = self.get_semantic_embedding(text1)
        embedding2 = self.get_semantic_embedding(text2)
        
        if embedding1 is None or embedding2 is None:
            return 0.0
        
        # Calcula similaridade cosseno
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return max(0.0, similarity)  # Garante que não seja negativo
    
    def analyze_script(self, script_text: str) -> Dict:
        """
        Análise completa de um roteiro.
        
        Args:
            script_text (str): Texto do roteiro
            
        Returns:
            Dict: Resultado completo da análise
        """
        return {
            'keywords': self.extract_keywords(script_text),
            'tone': self.analyze_tone(script_text),
            'category': self.categorize_content(script_text)[0],
            'category_confidence': self.categorize_content(script_text)[1],
            'semantic_vector': self.get_semantic_embedding(script_text)
        }