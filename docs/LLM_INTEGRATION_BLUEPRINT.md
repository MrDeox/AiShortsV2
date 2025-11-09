# LLM Integration Blueprint for AiShortsV2

## Overview
Blueprint detalhado para integrações LLM no AiShortsV2, focado em melhorias incrementais sem quebrar o funcionamento atual.

## 1. Content Generation

### 1.1 Adaptive Theme Strategy Engine

**Location**: `src/pipeline/services/content_generation_service.py:40-63`
- **Hook point**: Após determinar ThemeCategory, antes de criar prompt
- **Responsabilidade**: Gerar tema único e anotado evitando repetições

### 1.2 Script Refinement (Closed-loop)

**Location**: `src/pipeline/services/content_generation_service.py:90-121`
- **Hook point**: Após falha na validação do script
- **Responsabilidade**: Refinar script baseado no ValidationReport

### 1.3 Platform-Specific Variants

**Location**: `src/pipeline/services/content_generation_service.py:120-130`
- **Hook point**: Após aprovação do script
- **Responsabilidade**: Gerar variantes otimizadas para cada plataforma

## 2. Matching & Retrieval

### 2.1 B-roll Query Planner

**Location**: `src/pipeline/services/media_acquisition_service.py:143-187`
- **Hook point**: Dentro de `_generate_search_queries()`
- **Responsabilidade**: Planejar queries específicas com papéis visuais

### 2.2 Semantic Reranker (Top-K)

**Location**: `src/pipeline/services/media_acquisition_service.py:306-352`
- **Hook point**: Após obter candidatos CLIP
- **Responsabilidade**: Rerank baseado em compreensão textual

## 3. Validation & Quality Control

### 3.1 LLM Co-Reviewer

**Location**: `src/validators/script_validator.py:264-280`
- **Hook point**: Após validação determinística
- **Responsibilidade**: Análise qualitativa complementar

### 3.2 Caption Validator

**Location**: `src/pipeline/orchestrator.py:193-209`
- **Hook point**: Após geração de legendas
- **Responsabilidade**: Verificar consistência e estilo

## 4. Tooling

### 4.1 Typed Helpers on AsyncOpenRouterClient

**Location**: `src/core/async_openrouter_client.py`
- **Métodos**: generate_json, plan_broll_queries, rerank_candidates, refine_script
- **Benefícios**: Centralização, reuso, validação automática

### 4.2 Prompt Architect CLI

**Location**: `src/tools/prompt_architect.py` (novo)
- **Uso**: Ferramenta interna para evolução de prompts
- **Funcionalidade**: Analisa logs e sugere melhorias

## Implementation Priority

1. **High Priority**:
   - Theme Strategy Engine (evita repetição)
   - Script Refiner (melhora loops de retry)
   - B-roll Query Planner (estrutura já existe)

2. **Medium Priority**:
   - Semantic Reranker (qualidade B-roll)
   - LLM Co-Reviewer (validação aprofundada)

3. **Low Priority**:
   - Platform Variants (se demandado)
   - Caption Validator (polimento final)
   - Tooling helpers (manutenibilidade)

## Technical Requirements

- Usar `get_async_openrouter_client()`
- Respeitar `graceful_degradation`
- Aproveitar `content_cache` quando aplicável
- Configurações via `src/config/settings.py`
- Formatos estritos com validação JSON
- Temperaturas controladas (0.2-0.8)

## Implementation Notes

- Cada integração deve ser opcional via feature flags
- Manter compatibilidade com comportamento atual
- Logs detalhados para debug e auditoria
- Testes unitários para cada novo componente