"""
Gerador de Tema - AiShorts v2.0

Módulo principal para geração de temas de curiosidades usando IA.
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from src.config.settings import config
from src.core.openrouter_client import openrouter_client
from src.generators.prompt_engineering import PromptEngineering, ThemeCategory, prompt_engineering
from src.utils.exceptions import ThemeGenerationError, ValidationError, ErrorHandler


@dataclass
class GeneratedTheme:
    """Representa um tema gerado com metadados."""
    content: str
    category: ThemeCategory
    quality_score: float
    response_time: float
    timestamp: datetime
    usage: Optional[Dict[str, int]] = None
    metrics: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização."""
        return {
            "content": self.content,
            "category": self.category.value,
            "quality_score": self.quality_score,
            "response_time": self.response_time,
            "timestamp": self.timestamp.isoformat(),
            "usage": self.usage,
            "metrics": self.metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneratedTheme':
        """Cria instância a partir de dicionário."""
        return cls(
            content=data["content"],
            category=ThemeCategory(data["category"]),
            quality_score=data["quality_score"],
            response_time=data["response_time"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            usage=data.get("usage"),
            metrics=data.get("metrics")
        )


@dataclass
class ThemeGenerationResult:
    """Resultado da geração de múltiplos temas."""
    themes: List[GeneratedTheme]
    best_theme: Optional[GeneratedTheme]
    total_time: float
    generation_stats: Dict[str, Any]
    
    def save_to_file(self, filepath: Path) -> None:
        """Salva resultado em arquivo JSON."""
        data = {
            "themes": [theme.to_dict() for theme in self.themes],
            "best_theme": self.best_theme.to_dict() if self.best_theme else None,
            "total_time": self.total_time,
            "generation_stats": self.generation_stats,
            "timestamp": datetime.now().isoformat()
        }
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: Path) -> 'ThemeGenerationResult':
        """Carrega resultado de arquivo JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        themes = [GeneratedTheme.from_dict(theme_data) for theme_data in data["themes"]]
        best_theme = GeneratedTheme.from_dict(data["best_theme"]) if data["best_theme"] else None
        
        return cls(
            themes=themes,
            best_theme=best_theme,
            total_time=data["total_time"],
            generation_stats=data["generation_stats"]
        )


class ThemeGenerator:
    """Gerador principal de temas para vídeos curtos."""
    
    def __init__(self):
        self.config = config.theme_gen
        self.prompt_engineering = prompt_engineering
        self.openrouter = openrouter_client
        
        # Configurações de qualidade
        self.min_quality_score = 0.7
        self.max_attempts = self.config.max_attempts
        
        logger.info(f"ThemeGenerator inicializado - Categoria: {self.config.categories}")
    
    def generate_single_theme(self, 
                            category: Optional[ThemeCategory] = None,
                            custom_requirements: List[str] = None) -> GeneratedTheme:
        """
        Gera um único tema de alta qualidade.
        
        Args:
            category: Categoria específica (random se None)
            custom_requirements: Requisitos específicos para o tema
            
        Returns:
            GeneratedTheme com tema de alta qualidade
        """
        # Escolher categoria se não especificada
        if category is None:
            category = self._choose_random_category()
        
        try:
            # Criar prompt
            prompt_data = self.prompt_engineering.create_generation_prompt(
                category=category,
                custom_requirements=custom_requirements
            )
            
            # Log do início da geração
            logger.info(f"Iniciando geração de tema - Categoria: {category.value}")
            
            # Gerar conteúdo usando OpenRouter
            start_time = time.time()
            
            response = self.openrouter.generate_content(
                prompt=prompt_data["user_prompt"],
                system_message=prompt_data["system_message"],
                max_tokens=config.openrouter.max_tokens_theme,
                temperature=0.8  # Mais criatividade para temas
            )
            
            generation_time = time.time() - start_time
            
            # Processar resposta
            theme_content = self._clean_response(response.content)
            
            # Validar resposta
            self._validate_theme_response(theme_content, category)
            
            # Calcular métricas de qualidade
            quality_metrics = self.prompt_engineering.get_quality_metrics(theme_content, category)
            quality_score = quality_metrics["overall_quality"]
            
            # Criar tema gerado
            theme = GeneratedTheme(
                content=theme_content,
                category=category,
                quality_score=quality_score,
                response_time=generation_time,
                timestamp=datetime.now(),
                usage=response.usage,
                metrics=quality_metrics
            )
            
            # Log do resultado
            logger.info(
                f"Tema gerado - Categoria: {category.value}, "
                f"Qualidade: {quality_score:.2f}, "
                f"Tempo: {generation_time:.2f}s"
            )
            
            return theme
        
        except Exception as e:
            logger.error(f"Erro na geração de tema - Categoria: {category.value}, Erro: {e}")
            raise ThemeGenerationError(f"Falha na geração: {str(e)}", category=category.value)
    
    def generate_multiple_themes(self, 
                               count: int = 5,
                               categories: Optional[List[ThemeCategory]] = None,
                               min_quality_score: float = None) -> ThemeGenerationResult:
        """
        Gera múltiplos temas e seleciona os melhores.
        
        Args:
            count: Quantidade de temas a gerar
            categories: Lista de categorias (random se None)
            min_quality_score: Score mínimo de qualidade
            
        Returns:
            ThemeGenerationResult com melhores temas
        """
        if min_quality_score is None:
            min_quality_score = self.min_quality_score
        
        start_time = time.time()
        themes = []
        generation_stats = {
            "total_attempts": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "categories_used": set(),
            "quality_scores": [],
            "response_times": []
        }
        
        logger.info(f"Iniciando geração de {count} temas")
        
        for attempt in range(count * 2):  # Tentar até 2x mais para garantir qualidade
            if len(themes) >= count:
                break
            
            generation_stats["total_attempts"] += 1
            
            try:
                # Escolher categoria
                if categories and len(categories) > 0:
                    category = categories[attempt % len(categories)]
                else:
                    category = self._choose_random_category()
                
                generation_stats["categories_used"].add(category.value)
                
                # Gerar tema
                theme = self.generate_single_theme(category)
                
                # Verificar qualidade mínima
                if theme.quality_score >= min_quality_score:
                    themes.append(theme)
                    generation_stats["successful_generations"] += 1
                    generation_stats["quality_scores"].append(theme.quality_score)
                    generation_stats["response_times"].append(theme.response_time)
                    
                    logger.info(f"Tema aceito - Score: {theme.quality_score:.2f}")
                else:
                    logger.warning(f"Tema rejeitado - Score baixo: {theme.quality_score:.2f}")
                    generation_stats["failed_generations"] += 1
                
            except Exception as e:
                logger.error(f"Falha na tentativa {attempt + 1}: {e}")
                generation_stats["failed_generations"] += 1
        
        total_time = time.time() - start_time
        
        # Encontrar melhor tema
        best_theme = None
        if themes:
            best_theme = max(themes, key=lambda t: t.quality_score)
        
        # Finalizar estatísticas
        generation_stats["categories_used"] = list(generation_stats["categories_used"])
        if generation_stats["quality_scores"]:
            generation_stats["avg_quality_score"] = sum(generation_stats["quality_scores"]) / len(generation_stats["quality_scores"])
            generation_stats["min_quality_score"] = min(generation_stats["quality_scores"])
            generation_stats["max_quality_score"] = max(generation_stats["quality_scores"])
        
        if generation_stats["response_times"]:
            generation_stats["avg_response_time"] = sum(generation_stats["response_times"]) / len(generation_stats["response_times"])
        
        result = ThemeGenerationResult(
            themes=themes,
            best_theme=best_theme,
            total_time=total_time,
            generation_stats=generation_stats
        )
        
        logger.info(
            f"Geração concluída - {len(themes)}/{count} temas aceitos, "
            f"Melhor score: {best_theme.quality_score:.2f if best_theme else 0:.2f}, "
            f"Tempo total: {total_time:.2f}s"
        )
        
        return result
    
    def _choose_random_category(self) -> ThemeCategory:
        """Escolhe uma categoria aleatória das disponíveis."""
        import random
        # Converter string para enum ThemeCategory
        category_str = random.choice(self.config.categories)
        return ThemeCategory(category_str)
    
    def _clean_response(self, response: str) -> str:
        """
        Limpa a resposta do modelo removendo formatação desnecessária.
        
        Args:
            response: Resposta bruta do modelo
            
        Returns:
            Resposta limpa
        """
        # Remover quebras de linha extras
        response = response.strip()
        
        # Remover texto antes/depois se necessário
        lines = response.split('\n')
        
        # Se tem muitas linhas, pegar apenas a primeira linha significativa
        if len(lines) > 3:
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    return line.strip()
        
        return response
    
    def _validate_theme_response(self, response: str, category: ThemeCategory) -> None:
        """
        Valida se a resposta é um tema válido.
        
        Args:
            response: Resposta a validar
            category: Categoria do tema
            
        Raises:
            ValidationError: Se a resposta for inválida
        """
        logger.debug(f"Validando resposta da categoria {category.value}:\n{response}")
        
        if not response or len(response.strip()) < 5:  # Reduzido para 5 caracteres
            raise ValidationError("Tema muito curto ou vazio", field="content", value=response)
        
        if len(response) > 300:  # Aumentado para 300 caracteres
            logger.warning(f"Resposta muito longa, truncando: {response[:300]}")
            response = response[:300]
        
        # Verificar formato - tornar mais flexível
        try:
            if not prompt_engineering.validate_prompt_format(response):
                # Se a validação falhar, tentar validação manual básica
                if len(response.strip()) >= 10 and any(char.isalpha() for char in response):
                    logger.info("Validação manual passou para resposta")
                    pass
                else:
                    raise ValidationError("Formato de tema inválido", field="format", value=response)
        except Exception as e:
            logger.warning(f"Erro na validação de formato: {e}, usando validação manual")
            if len(response.strip()) >= 10:
                pass  # Passa na validação manual
            else:
                raise ValidationError("Tema muito curto para validação manual", field="content", value=response)
        
        # Verificar se é realmente uma pergunta ou curiosidade
        curiosity_words = ['?', 'por que', 'como', 'o que', 'quando', 'onde', 'será que', 'você sabia', 'vocês sabiam']
        has_curiosity = any(word in response.lower() for word in curiosity_words)
        
        if not has_curiosity:
            logger.warning(f"Tema pode não ter formato de curiosidade: {response}")
            # Não levantar erro, apenas warning
        
        # Verificar se é realmente uma pergunta ou curiosidade
        if not any(word in response.lower() for word in ['?', 'por que', 'como', 'o que', 'quando', 'onde', 'será que', 'você sabia']):
            logger.warning(f"Tema pode não ter formato de curiosidade: {response}")
    
    def save_generation_result(self, result: ThemeGenerationResult, filename: str = None) -> Path:
        """
        Salva resultado da geração em arquivo.
        
        Args:
            result: Resultado da geração
            filename: Nome do arquivo (auto-gerado se None)
            
        Returns:
            Caminho do arquivo salvo
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"theme_generation_{timestamp}.json"
        
        filepath = config.storage.output_dir / filename
        result.save_to_file(filepath)
        
        logger.info(f"Resultado salvo em: {filepath}")
        return filepath
    
    def analyze_themes(self, themes: List[GeneratedTheme]) -> Dict[str, Any]:
        """
        Analisa uma lista de temas gerados.
        
        Args:
            themes: Lista de temas para analisar
            
        Returns:
            Análise detalhada dos temas
        """
        if not themes:
            return {"error": "Nenhum tema para analisar"}
        
        analysis = {
            "total_themes": len(themes),
            "categories": {},
            "quality_stats": {},
            "performance_stats": {},
            "best_themes": [],
            "patterns": []
        }
        
        # Análise por categoria
        for theme in themes:
            cat = theme.category.value
            if cat not in analysis["categories"]:
                analysis["categories"][cat] = {
                    "count": 0,
                    "avg_quality": 0,
                    "avg_time": 0
                }
            analysis["categories"][cat]["count"] += 1
        
        # Calcular médias por categoria
        for cat_data in analysis["categories"].values():
            cat_themes = [t for t in themes if t.category.value == cat]
            cat_data["avg_quality"] = sum(t.quality_score for t in cat_themes) / len(cat_themes)
            cat_data["avg_time"] = sum(t.response_time for t in cat_themes) / len(cat_themes)
        
        # Estatísticas de qualidade
        quality_scores = [t.quality_score for t in themes]
        analysis["quality_stats"] = {
            "avg_quality": sum(quality_scores) / len(quality_scores),
            "min_quality": min(quality_scores),
            "max_quality": max(quality_scores),
            "std_quality": self._calculate_std_dev(quality_scores)
        }
        
        # Estatísticas de performance
        response_times = [t.response_time for t in themes]
        analysis["performance_stats"] = {
            "avg_time": sum(response_times) / len(response_times),
            "min_time": min(response_times),
            "max_time": max(response_times)
        }
        
        # Melhores temas
        sorted_themes = sorted(themes, key=lambda t: t.quality_score, reverse=True)
        analysis["best_themes"] = [
            {
                "content": theme.content,
                "quality_score": theme.quality_score,
                "category": theme.category.value
            }
            for theme in sorted_themes[:5]
        ]
        
        # Detectar padrões
        analysis["patterns"] = self._detect_patterns(themes)
        
        return analysis
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calcula desvio padrão."""
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _detect_patterns(self, themes: List[GeneratedTheme]) -> List[str]:
        """Detecta padrões nos temas gerados."""
        patterns = []
        
        # Análise de categorias mais populares
        category_counts = {}
        for theme in themes:
            cat = theme.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        if category_counts:
            most_popular = max(category_counts, key=category_counts.get)
            patterns.append(f"Categoria mais popular: {most_popular}")
        
        # Análise de palavras frequentes nas perguntas
        words = []
        for theme in themes:
            # Extrair palavras das perguntas
            question_words = ['por que', 'como', 'o que', 'quando', 'onde', 'por que', 'será que']
            for word in question_words:
                if word in theme.content.lower():
                    words.append(word)
        
        if words:
            from collections import Counter
            word_counts = Counter(words)
            most_common_word = word_counts.most_common(1)[0][0]
            patterns.append(f"Palavra mais comum em perguntas: '{most_common_word}'")
        
        return patterns


# Instância global do gerador
theme_generator = ThemeGenerator()

if __name__ == "__main__":
    # Teste do gerador de temas
    print("=== Teste do Gerador de Tema ===")
    
    try:
        # Teste de geração única
        print("1. Teste de geração única:")
        theme = theme_generator.generate_single_theme(ThemeCategory.SCIENCE)
        print(f"📝 Tema: {theme.content}")
        print(f"⭐ Qualidade: {theme.quality_score:.2f}")
        print(f"⏱️ Tempo: {theme.response_time:.2f}s")
        
        # Teste de geração múltipla
        print("\n2. Teste de geração múltipla:")
        result = theme_generator.generate_multiple_themes(count=3)
        print(f"✅ {len(result.themes)} temas gerados")
        print(f"🏆 Melhor: {result.best_theme.content if result.best_theme else 'Nenhum'}")
        
        # Salvar resultado
        filepath = theme_generator.save_generation_result(result)
        print(f"💾 Salvo em: {filepath}")
        
        # Análise
        print("\n3. Análise dos temas:")
        analysis = theme_generator.analyze_themes(result.themes)
        for key, value in analysis.items():
            print(f"   {key}: {value}")
    
    except Exception as e:
        print(f"❌ Erro no teste: {e}")