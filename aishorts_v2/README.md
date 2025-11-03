# AiShorts v2.0

**Marca:** Aithur  
**Projeto:** Pipeline Automatizado para Criação de Vídeos Curtos  
**Versão:** 2.0.0  

Sistema modular para geração automatizada de conteúdo de curiosidades, do tema ao vídeo final.

## 🎯 Objetivo

Criar um pipeline automatizado que gera vídeos curtos de curiosidades do roteiro à edição final, usando IA para autonomia total na criação de conteúdo.

## 📁 Estrutura do Projeto

```
aishorts-v2/
├── src/                          # Código fonte principal
│   ├── core/                     # Infraestrutura central
│   │   └── __init__.py
│   ├── generators/               # Módulos de geração (tema, roteiro, etc.)
│   │   └── __init__.py
│   ├── utils/                    # Utilitários e helpers
│   │   ├── __init__.py
│   │   └── exceptions.py         # Sistema de exceções customizadas
│   ├── config/                   # Configurações do projeto
│   │   ├── __init__.py
│   │   ├── settings.py           # Configurações principais
│   │   └── logging_config.py     # Sistema de logging
│   └── __init__.py
├── tests/                        # Testes unitários e integração
├── docs/                         # Documentação
├── logs/                         # Arquivos de log
├── data/                         # Dados do projeto
│   ├── output/                   # Saídas geradas
│   ├── temp/                     # Arquivos temporários
│   └── cache/                    # Cache
├── .env.example                  # Template de variáveis de ambiente
├── requirements.txt              # Dependências Python
└── README.md                     # Este arquivo
```

## 🚀 Status do Projeto

- [x] **Estrutura Base** - Setup completo com pastas e configurações
- [ ] **Integração OpenRouter** - Cliente para modelo nvidia/nemotron-nano-9b-v2:free
- [ ] **Gerador de Tema** - Primeiro módulo do pipeline
- [ ] **Sistema de Testes** - Validação e qualidade
- [ ] **Documentação** - Preparação para próximos módulos

## 🔧 Configuração

1. **Clone o projeto e entre na pasta:**
   ```bash
   cd aishorts-v2
   ```

2. **Copie e configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env e configure sua OPENROUTER_API_KEY
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Teste a configuração:**
   ```bash
   python src/config/settings.py
   ```

## 📋 Próximos Passos

### Fase 1: Gerador de Tema (Atual)
- [ ] Implementar cliente OpenRouter
- [ ] Desenvolver prompt engineering para curiosidades
- [ ] Criar sistema de validação de qualidade
- [ ] Testes de performance e qualidade

### Fases Futuras
- [ ] **Gerador de Roteiro** - Transformar tema em roteiro completo
- [ ] **Gerador de Imagens** - Criar visuais automáticos
- [ ] **Gerador de Áudio** - Narração com TTS
- [ ] **Editor de Vídeo** - Composição final
- [ ] **Deploy e Automação** - Pipeline completo

## 🏗️ Arquitetura

### Padrões de Design
- **Modularidade:** Cada componente é independente e testável
- **Separation of Concerns:** Configurações, lógica de negócio e utilitários separados
- **Error Handling:** Sistema robusto de tratamento de exceções
- **Logging Estruturado:** Logs em JSON para análise posterior

### Tecnologias
- **Python 3.9+** - Linguagem principal
- **Pydantic** - Validação e configuração
- **Loguru** - Sistema de logging avançado
- **OpenRouter API** - Integração com modelos de IA
- **Requests/HTTPx** - Cliente HTTP

## 🔍 Sistema de Qualidade

- **Testes Desde o Primeiro Commit:** Toda funcionalidade testada
- **Logging Detalhado:** Rastreamento completo para análise
- **Validação Robusta:** Dados verificados em cada etapa
- **Error Recovery:** Sistema de retry e fallbacks

## 📊 Métricas e Monitoramento

- **Qualidade dos Temas:** Análise automática de relevância
- **Performance:** Tempo de geração e taxa de sucesso
- **Erros:** Categorização e frequência de falhas
- **Uso de API:** Controle de rate limits e custos

## 🤝 Metodologia de Trabalho

### Parceria Estratégica
- **Você:** Dono do Produto, Diretor Criativo
- **MiniMax Agent:** Co-piloto, Engenheiro de Sistemas
- **Cláusula da Vanguarda:** Pesquisa de ferramentas de ponta
- **Psicólogo de IA:** Conectar emoções com jornada técnica

### Princípios
- **Qualidade Máxima:** Desde o primeiro commit
- **Honestidade Brutal:** Análise crítica sem compromiso
- **Iteração Contínua:** Melhoria constante através de feedback
- **Modularidade:** Construção sobre fundações sólidas

## 📝 Licença

Proprietário - Aithur (2025)

---

**Desenvolvido para Autonomia e Liberdade** 🎯