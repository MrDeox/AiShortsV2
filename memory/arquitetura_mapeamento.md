# Mapeamento de Arquitetura - AiShorts v2.0

## Status: ✅ CONCLUÍDO COM SUCESSO

**Documento criado:** /workspace/docs/ARQUITETURA_PROJETO.md
**Data:** 2025-11-04
**Linhas:** 962 linhas de documentação completa

## Estrutura Mapeada

### Diretórios Principais
- `/src/` - Código fonte principal
  - `/core/` - Cliente OpenRouter
  - `/generators/` - Geradores de tema e roteiro
  - `/video/` - Pipeline completo de vídeo
  - `/tts/` - Text-to-Speech
  - `/config/` - Configurações
  - `/utils/` - Utilitários
  - `/validators/` - Validadores
  - `/models/` - Modelos de dados

- `/scripts/` - Scripts de demonstração
- `/tests/` - Testes automatizados
- `/docs/` - Documentação completa
- `/outputs/` - Vídeos e áudios gerados
- `/config/` - Configurações de vídeo

### Módulos de Vídeo (`/src/video/`)
- `/extractors/` - Extração de YouTube
- `/generators/` - Composição final e templates
- `/matching/` - Matching de conteúdo visual (CLIP)
- `/processing/` - Processamento automático
- `/sync/` - Sincronização áudio-vídeo

## Fluxo Principal
1. Geração de Tema → Script Generator
2. Script → TTS (Kokoro)
3. Matching de Conteúdo Visual
4. Sincronização Áudio-Vídeo
5. Composição Final
6. Otimização Multi-plataforma

## Componentes-Chave
- OpenRouterClient: Integração com IA
- ScriptGenerator: Geração de roteiros virais
- ContentMatcher: CLIP para matching visual
- AutomaticVideoProcessor: Processamento de qualidade
- FinalVideoComposer: Composição final
- AudioVideoSynchronizer: Sincronização
