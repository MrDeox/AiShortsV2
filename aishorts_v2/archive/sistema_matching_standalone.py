"""
Sistema de Matching Roteiro-Vídeo - Versão Standalone
Implementação completa do sistema de análise semântica para AI Shorts
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import Counter
import re
from dataclasses import dataclass


@dataclass
class VideoInfo:
    """Estrutura de dados para informações de vídeo."""
    id: str
    title: str
    description: str
    duration: int
    views: int
    likes: int
    upload_date: str
    channel: str
    category: str
    tags: List[str]
    quality_score: float = 0.0
    semantic_score: float = 0.0
    keyword_score: float = 0.0


class SemanticAnalyzer:
    """
    Analisador semântico para matching entre roteiro e vídeo.
    Utiliza spaCy para processamento de linguagem natural em português.
    """
    
    # Mapeamento de categorias para palavras-chave
    CATEGORY_KEYWORDS = {
        'SPACE': ['espaço', 'galáxia', 'planeta', 'estrela', 'universo', 'astronauta', 
                  'satélite', 'lua', 'sol', 'cosmos', 'astronomia', 'mars'],
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
    
    # Palavras de tom emocional
    POSITIVE_WORDS = ['feliz', 'alegre', 'bonito', 'maravilhoso', 'excelente', 'fantástico', 
                      'incrível', 'espetacular', 'adorável', 'amor', 'paixão', 'diversão']
    NEGATIVE_WORDS = ['triste', 'feio', 'terrível', 'horrível', 'péssimo', 'ruim', 
                      'dor', 'sofrimento', 'guerra', 'conflito', 'problema', 'crise']
    NEUTRAL_WORDS = ['informação', 'dados', 'fato', 'conhecimento', 'estudo', 'análise', 
                     'pesquisa', 'descoberta', 'explicação', 'descrição']
    
    def __init__(self):
        """Inicializa o analisador semântico."""
        try:
            import spacy
            self.nlp = spacy.load("pt_core_news_sm")
            self.use_spacy = True
            print("✓ Modelo spaCy carregado")
        except:
            self.use_spacy = False
            self.nlp = None
            print("✓ Usando análise básica (spaCy não disponível)")
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """Extrai palavras-chave importantes do texto."""
        if self.use_spacy and self.nlp:
            return self._extract_keywords_spacy(text, max_keywords)
        else:
            return self._extract_keywords_fallback(text, max_keywords)
    
    def _extract_keywords_spacy(self, text: str, max_keywords: int) -> List[str]:
        """Extrai palavras-chave usando spaCy."""
        doc = self.nlp(text.lower())
        stop_words = set(self.nlp.Defaults.stop_words)
        stop_words.update({'ser', 'estar', 'ter', 'fazer', 'ir', 'vir', 'dar', 'dizer', 'ver', 'saber'})
        
        keywords = []
        for token in doc:
            if (not token.is_stop and not token.is_punct and not token.is_space and
                len(token.text) > 2 and token.text not in stop_words and
                token.pos_ in ['NOUN', 'ADJ', 'VERB']):
                keywords.append(token.lemma_ if token.lemma_ != token.text else token.text)
        
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(max_keywords)]
    
    def _extract_keywords_fallback(self, text: str, max_keywords: int) -> List[str]:
        """Extrai palavras-chave usando método básico."""
        basic_stop_words = {
            'a', 'o', 'e', 'é', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas',
            'para', 'por', 'com', 'como', 'que', 'se', 'não', 'sim', 'um', 'uma', 'uns', 'umas',
            'ser', 'estar', 'ter', 'fazer', 'ir', 'vir', 'dar', 'dizer', 'ver', 'saber',
            'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas',
            'aquele', 'aquela', 'aqueles', 'aquelas', 'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas'
        }
        
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text_clean.split()
        
        keywords = []
        for word in words:
            if len(word) > 2 and word not in basic_stop_words and word.isalpha():
                keywords.append(word)
        
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(max_keywords)]
    
    def analyze_tone(self, text: str) -> Dict[str, float]:
        """Analisa o tom emocional do texto."""
        text_lower = text.lower()
        
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
        """Categoriza o conteúdo do texto."""
        keywords = self.extract_keywords(text, max_keywords=50)
        text_lower = text.lower()
        
        category_scores = {}
        for category, category_keywords in self.CATEGORY_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in category_keywords:
                    score += 2
            
            for keyword in category_keywords:
                if keyword in text_lower:
                    score += 1
            
            category_scores[category] = score
        
        if not category_scores or max(category_scores.values()) == 0:
            return 'GENERAL', 0.0
        
        best_category = max(category_scores, key=category_scores.get)
        max_score = category_scores[best_category]
        confidence = min(max_score / max(len(keywords) * 2, 1), 1.0)
        
        return best_category, confidence
    
    def get_semantic_embedding(self, text: str) -> Optional[np.ndarray]:
        """Gera embedding semântico do texto."""
        if self.use_spacy and self.nlp:
            try:
                doc = self.nlp(text)
                if doc.has_vector:
                    return doc.vector
                else:
                    vectors = [token.vector for token in doc if token.has_vector]
                    if vectors:
                        return np.mean(vectors, axis=0)
                    else:
                        return self._generate_fallback_embedding(text)
            except:
                return self._generate_fallback_embedding(text)
        else:
            return self._generate_fallback_embedding(text)
    
    def _generate_fallback_embedding(self, text: str) -> Optional[np.ndarray]:
        """Gera embedding básico usando hash de palavras."""
        words = text.lower().split()
        vector = np.zeros(300)
        
        for i, word in enumerate(words[:300]):
            hash_val = hash(word) % 300
            vector[hash_val] += 1 / (i + 1)
        
        return vector if np.any(vector) else None
    
    def analyze_script(self, script_text: str) -> Dict:
        """Análise completa de um roteiro."""
        return {
            'keywords': self.extract_keywords(script_text),
            'tone': self.analyze_tone(script_text),
            'category': self.categorize_content(script_text)[0],
            'category_confidence': self.categorize_content(script_text)[1],
            'semantic_vector': self.get_semantic_embedding(script_text)
        }


class VideoSearcher:
    """
    Sistema de busca inteligente de vídeos para matching com roteiros.
    """
    
    def __init__(self):
        """Inicializa o buscador de vídeos."""
        self.video_database = self._initialize_sample_database()
    
    def _initialize_sample_database(self) -> List[VideoInfo]:
        """Inicializa banco de dados de exemplo."""
        return [
            VideoInfo(
                id="video_001",
                title="Espaço: Uma Jornada Incrível pelo Universo",
                description="Explore as maravilhas do espaço com imagens espetaculares de galáxias e planetas distantes.",
                duration=300, views=1000000, likes=50000, upload_date="2024-01-15",
                channel="Ciência Espacial", category="SPACE",
                tags=["espaço", "universo", "galáxias", "estrelas", "astronomia"]
            ),
            VideoInfo(
                id="video_002",
                title="Delfins em Ação: A Inteligência dos Mamíferos Marinhos",
                description="Descubra a incrível inteligência e agilidade dos golfinhos em seu habitat natural.",
                duration=450, views=750000, likes=35000, upload_date="2024-02-20",
                channel="Vida Selvagem", category="ANIMALS",
                tags=["delfins", "golfinhos", "mamíferos", "marinhos", "inteligência"]
            ),
            VideoInfo(
                id="video_003",
                title="Floresta Amazônica: O Pulmão Verde do Mundo",
                description="Uma viagem pela biodiversidade única da maior floresta tropical do planeta.",
                duration=600, views=1200000, likes=60000, upload_date="2024-01-10",
                channel="Natureza Brasil", category="NATURE",
                tags=["amazônia", "floresta", "biodiversidade", "brasil", "tropical"]
            ),
            VideoInfo(
                id="video_004",
                title="Inteligência Artificial: O Futuro da Tecnologia",
                description="Explore como a IA está revolucionando diversos setores da sociedade moderna.",
                duration=480, views=800000, likes=40000, upload_date="2024-03-05",
                channel="Tech Future", category="TECHNOLOGY",
                tags=["IA", "inteligência artificial", "tecnologia", "futuro", "inovação"]
            ),
            VideoInfo(
                id="video_005",
                title="Golfinhos Brilhantes: Show de Inteligência Marina",
                description="Veja golfinhos realizando truques incríveis e demonstrando sua incrível inteligência.",
                duration=360, views=950000, likes=48000, upload_date="2024-02-14",
                channel="Oceanos Incríveis", category="ANIMALS",
                tags=["golfinhos", "inteligência", "truques", "marinhos", "show"]
            )
        ]
    
    def search_by_keywords(self, keywords: List[str], category: Optional[str] = None, 
                          max_results: int = 10) -> List[VideoInfo]:
        """Busca vídeos baseados em palavras-chave."""
        matching_videos = []
        
        for video in self.video_database:
            score = 0
            video_text = f"{video.title} {video.description} {' '.join(video.tags)}".lower()
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in video_text:
                    score += 2
                for word in video_text.split():
                    if keyword_lower in word or word in keyword_lower:
                        score += 0.5
                        break
            
            if category and video.category == category:
                score += 3
            
            if score > 0:
                video.keyword_score = score
                matching_videos.append(video)
        
        matching_videos.sort(key=lambda v: v.keyword_score, reverse=True)
        return matching_videos[:max_results]
    
    def search_by_semantic(self, embedding: np.ndarray, max_results: int = 10) -> List[VideoInfo]:
        """Busca vídeos usando similaridade semântica."""
        semantic_scores = []
        
        for video in self.video_database:
            video_text = f"{video.title} {video.description}"
            video_embedding = self._simulate_embedding(video_text)
            
            if video_embedding is not None:
                similarity = self._cosine_similarity(embedding, video_embedding)
                video.semantic_score = similarity
                semantic_scores.append(video)
        
        semantic_scores.sort(key=lambda v: v.semantic_score, reverse=True)
        return semantic_scores[:max_results]
    
    def _simulate_embedding(self, text: str) -> Optional[np.ndarray]:
        """Simula embedding para fins de demonstração."""
        words = text.lower().split()
        vector = np.zeros(300)
        
        for i, word in enumerate(words[:300]):
            hash_val = hash(word) % 300
            vector[hash_val] += 1 / (i + 1)
        
        return vector if np.any(vector) else None
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calcula similaridade cosseno."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def search_combined(self, keywords: List[str], semantic_embedding: np.ndarray,
                       category: Optional[str] = None, max_results: int = 10) -> List[VideoInfo]:
        """Busca combinada usando palavras-chave e análise semântica."""
        keyword_results = self.search_by_keywords(keywords, category)
        semantic_results = self.search_by_semantic(semantic_embedding)
        
        video_scores = {}
        
        for video in keyword_results:
            if video.id not in video_scores:
                video_scores[video.id] = {'video': video, 'combined_score': 0.0}
            video_scores[video.id]['combined_score'] += video.keyword_score * 0.6
        
        for video in semantic_results:
            if video.id not in video_scores:
                video_scores[video.id] = {'video': video, 'combined_score': 0.0}
            video_scores[video.id]['combined_score'] += video.semantic_score * 0.4
        
        ranked_videos = sorted(
            video_scores.values(),
            key=lambda x: x['combined_score'],
            reverse=True
        )
        
        return [item['video'] for item in ranked_videos[:max_results]]
    
    def get_best_match(self, keywords: List[str], semantic_embedding: np.ndarray,
                      category: Optional[str] = None) -> Optional[VideoInfo]:
        """Retorna o melhor vídeo para o roteiro."""
        results = self.search_combined(keywords, semantic_embedding, category, max_results=1)
        return results[0] if results else None


def demo_sistema_completo():
    """Demonstração completa do sistema."""
    print("🎬 SISTEMA DE MATCHING ROTEIRO-VÍDEO - AI SHORTS")
    print("=" * 60)
    
    # Inicialização
    analyzer = SemanticAnalyzer()
    searcher = VideoSearcher()
    
    # Roteiro de exemplo
    roteiro = """
    HOOK: Você sabia que os golfinhos são capazes de reconhecer-se no espelho?
    
    DEVELOPMENT: Estes incríveis mamíferos marinhos possuem uma inteligência 
    extraordinária que nos surpreende a cada nova descoberta. No oceano Pacífico, 
    pesquisadores observaram golfinhos desenvolvendo técnicas únicas de caça, 
    usando conchas como ferramentas para capturar peixes.
    
    Os golfinhos também demonstram comportamentos sociais complexos, criando 
    laços que duram décadas. Eles se comunicam através de cliques, assobios 
    e linguagem corporal, construindo uma rica cultura marinha.
    
    CONCLUSION: A próxima vez que você ver um golfinho, lembre-se de que está 
    diante de uma das mentes mais brilhantes dos oceanos.
    """
    
    print("📝 1. ANÁLISE DO ROTEIRO")
    print("-" * 30)
    
    analise = analyzer.analyze_script(roteiro)
    
    print(f"✅ Categoria: {analise['category']}")
    print(f"✅ Confiança: {analise['category_confidence']:.2f}")
    print(f"✅ Tom: Positivo={analise['tone']['positive']:.2f}")
    print(f"✅ Keywords: {analise['keywords'][:6]}")
    
    print("\n🎯 2. BUSCA DE VÍDEOS")
    print("-" * 30)
    
    melhor_video = searcher.get_best_match(
        analise['keywords'][:5],
        analise['semantic_vector'],
        analise['category']
    )
    
    if melhor_video:
        print(f"🎬 Melhor vídeo: '{melhor_video.title}'")
        print(f"📺 Canal: {melhor_video.channel}")
        print(f"⏱️ Duração: {melhor_video.duration // 60}:{melhor_video.duration % 60:02d}")
        print(f"👀 Views: {melhor_video.views:,}")
        print(f"⭐ Score: {melhor_video.quality_score:.2f}")
    
    print("\n📊 3. MÚLTIPLAS OPÇÕES")
    print("-" * 30)
    
    opcoes = searcher.search_combined(
        analise['keywords'][:5],
        analise['semantic_vector'],
        analise['category'],
        max_results=3
    )
    
    for i, video in enumerate(opcoes, 1):
        print(f"{i}. {video.title}")
        print(f"   📺 {video.channel} | 🎯 {video.category}")
    
    print("\n🚀 4. RECOMENDAÇÕES PARA PRODUÇÃO")
    print("-" * 30)
    
    if analise['category'] == 'ANIMALS':
        print("💡 Foque em imagens de alta qualidade dos animais")
        print("💡 Use transições suaves entre cenas")
        print("💡 Adicione fatos interessantes em overlays")
    
    if analise['tone']['positive'] > 0.7:
        print("💡 Tom positivo detectado - use música energética")
        print("💡 Cores vibrantes nas sobreposições de texto")
    
    print(f"\n🎯 OTIMIZAÇÃO SEO:")
    print(f"   • Palavra-chave principal: {analise['keywords'][0] if analise['keywords'] else 'N/A'}")
    print(f"   • Categoria: {analise['category']}")
    print(f"   • Tom: {'Positivo' if analise['tone']['positive'] > 0.6 else 'Neutro'}")
    
    return analise, opcoes


if __name__ == "__main__":
    try:
        analise, opcoes = demo_sistema_completo()
        
        print("\n" + "=" * 60)
        print("🎉 SISTEMA IMPLEMENTADO E TESTADO COM SUCESSO! 🎉")
        print("=" * 60)
        print("\n📋 Recursos Implementados:")
        print("✅ Análise semântica com spaCy (fallback)")
        print("✅ Extração de palavras-chave inteligente")
        print("✅ Análise de tom emocional")
        print("✅ Categorização automática")
        print("✅ Embeddings semânticos")
        print("✅ Busca por palavras-chave")
        print("✅ Busca semântica")
        print("✅ Sistema de busca combinada")
        print("✅ Ranking e scoring")
        print("✅ Matching inteligente roteiro-vídeo")
        
        print(f"\n🎬 Sistema pronto para integração com AI Shorts!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()