# Requisitos Técnicos e Melhores Práticas Visuais para TikTok, YouTube Shorts e Instagram Reels (2025)

## 1. Sumário executivo: o que importa em 2025 (e por quê)

Em 2025, o vídeo curto continua a ser o formato dominante nos feeds sociais, exigindo execução técnica impecável e uma linguagem visual otimizada para consumo em smartphone. As três plataformas convergem em fundamentos — proporción vertical 9:16, resolução 1080x1920, taxa de quadros a partir de 30 quadros por segundo (fps) —, mas mantêm nuances relevantes em duração, tamanho de arquivo, tolerâncias de aspect ratio, presença ou não de miniaturas, e recomendações de “zona segura” para textos e elementos críticos. A seguir, um panorama rápido:

- TikTok. Prefere 9:16 em 1080p, com 30 fps como base e 60 fps para conteúdo mais dinâmico. Oferece suporte a MP4/MOV e codecs H.264/AAC; a duração vai de segundos a até 10 minutos, com diretrizes oficiais extensas. Limites de tamanho de arquivo variam por fonte e uso (orgânico/ads), com referências a 72 MB (Android), 287,6 MB (iOS), 500 MB e 2 GB para faixas de duração mayores; é essencial validar no momento da publicação devido a variações reportadas por diferentes guias. Boas práticas criativas destacam o gancho nos primeiros 3–6 segundos, uso de texto sobreposto (5–10 palavras por segundo), manutenção de elementos na “zona segura” e estética nativa de UGC (user-generated content). [^7][^8][^9][^10]
- YouTube Shorts. Padrão 9:16 em 1080x1920, tipicamente entre 15 e 60 segundos, com suporte a 24–60 fps e bitrates sugeridos na faixa de 1–6 Mbps. Há tolerância para 1:1 (1080x1080). Miniaturas não aparecem dentro do player de Shorts, mas são exibidas na aba “Shorts” do canal. As áreas seguras recomendam manter elementos no centro do quadro para evitar sobreposições de interface. [^11][^12][^13][^14]
- Instagram Reels. Aspect ratio entre 1.91:1 e 9:16, com 9:16 como ideal para tela cheia. Requisitos oficiais indicam no mínimo 720p e 30 fps. Em 2025, a duração permitida chega a 90 segundos, com размер de arquivo até 4 GB. A plataforma valoriza estética mais polida, capas personalizadas, legendas com bom contraste e CTAs claros. [^1][^15][^16][^17]

Por que isso importa? O desempenho nos feeds é determinado por retenção e tempo de visualização — os algoritmos privilegiam peças que mantêm o espectador nos primeiros segundos e oferecem variedade visual ao longo do clipe. Do ponto de vista de produção, padrões de corte e transições rhythm-driven (alinhados à batida), speed ramping e loops planejados aumentam o watch-time e reduzem quedas abruptas na curva de retenção. A qualidade técnica (1080p, 30+ fps, legibilidade do texto, contraste e áudio limpo) é um pré-requisito para que a narrativa entregar seu impacto. [^5][^3][^4]

O que fazer agora (resumo):
- Padronizar renderização em 1080x1920, 9:16, 30 fps (usar 60 fps quando o conteúdo for muito dinâmico).
- Planejar ganchos visuais/sonoros nos primeiros 1–3 segundos e reforçar a proposta de valor até o segundo 6.
- Introduzir nova informação/visual a cada 3–5 segundos.
- Usar texto sobreposto com parcimônia e legibilidade (TikTok: 5–10 palavras por segundo).
- Validar limites de tamanho de arquivo e duração por plataforma antes de publicar e ajustar conforme evoluções.
- Testar variações de hooks, primeiros frames e transições com monitoramento de retenção.

Para orientar o planejamento de produção, a Tabela 1 compara de forma sintética as especificações técnicas-chaves.

Tabela 1 — Comparativo rápido das especificações técnicas por plataforma
| Plataforma | Aspect ratio | Resolução | Duração | FPS | Formatos/Codecs | Tamanho de arquivo |
|---|---|---|---|---|---|---|
| TikTok | 9:16 (suporta 1:1 e 16:9) | 1080x1920 (ideal); 720p mínimo | 1 s a 10 min (recom. 9–15 s) | 30 (60 para movimento intenso) | MP4/MOV; H.264/AAC | 72 MB (Android), 287,6 MB (iOS), 500 MB, 2 GB (varia por fonte) |
| YouTube Shorts | 9:16 (1:1 tolerado) | 1080x1920 (ideal) | 15–60 s | 24–60 | MP4/MOV; H.264; AAC/MP3 | Diretrizes variáveis (bitrate 1–6 Mbps sugerido) |
| Instagram Reels | 1.91:1 a 9:16 (9:16 ideal) | 1080x1920 (ideal); 720p mínimo | Até 90 s | 30+ | MP4/MOV; H.264/AAC (implícito por contêineres) | Até 4 GB |

Observação sobre lacunas de informação:
- Limites de tamanho de arquivo para TikTok variam entre fontes; recomenda-se validação no momento da publicação. [^7][^8][^9]
- YouTube não publica uma especificação oficial completa dedicada exclusivamente a Shorts; as diretrizes são inferidas de documentação geral e guias de terceiros. [^11][^12][^13][^14]
- Diretrizes formais sobre zonas seguras para Reels e TikTok não são públicas; inferências baseiam-se em melhores práticas de UI/UX e guias de terceiros. [^1][^9][^11]

## 2. Metodologia, escopo e fontes

Este guia cobre especificações técnicas oficiais e práticas recomendadas para publicação orgânica e paga em TikTok, YouTube Shorts e Instagram Reels, com foco em execução mobile-first. As informações são baseadas em: documentação oficial das plataformas (p. ex., Instagram Help Center e TikTok For Business), guias técnicos atualizados de referência (Riverside, Descript, BigMotion), e análises de tendências e benchmarks de edição e performance (Onadverts, StackInfluence, Sprout Social). [^1][^3][^4][^2][^7][^8][^11][^12][^13][^14][^5][^6][^18]

Critérios de seleção:
- Atualização (2024–2025), clareza técnica e alinhamento com práticas de produção de conteúdo curto.
- Preferência por fontes oficiais e guias widely cited no mercado.

Limitação e lacunas de informação:
- Limites de tamanho de arquivo para TikTok e YouTube Shorts divergem entre fontes; recomenda-se validação no fluxo de publicação e atualização contínua do protocolo interno. [^7][^8][^9][^11][^12][^13][^14]
- Zonas seguras (safe areas) não são documentadas formalmente por todas as plataformas; adotamos recomendações conservadoras com centralização de elementos críticos. [^1][^9][^11]

## 3. Especificações técnicas por plataforma

A seguir, detalhamento operacional por plataforma, com implicações práticas para filmagem, edição, exportação e controle de qualidade.

### 3.1 TikTok

Especificações principais. O formato nativo é 9:16, com 1080x1920 como resolução ideal e 720p como mínimo de qualidade. MP4 e MOV com H.264 para vídeo e AAC para áudio são os mais Compatíveis, e 30 fps é a base recomendada, subindo para 60 fps em conteúdos de alta velocidade/movimento. [^7][^8]

Aspect ratio e cortes. Suporta 9:16, 1:1 e 16:9, mas o comportamento no feed e a experiência mobile favorecem vertical. Conteúdos horizontais podem exibir barras pretas e perder imersão, afetando o engajamento. [^8]

Duração e tamanho de arquivo. A duração vai de segundos a 10 minutos. Os limites de tamanho de arquivo variam conforme a fonte e o tipo de uso (orgânico vs. anúncios): há menções a 72 MB (Android), 287,6 MB (iOS), 500 MB e 2 GB para arquivos entre 3 e 10 minutos. Em dúvida, padronizar exportação otimizada e validar no momento do upload, registrando variações por versão de app/sistema. [^7][^8][^9]

Boas práticas de interface. Manter elementos críticos (rostos, títulos, CTAs) dentro de uma zona segura central, evitando sobreposições de UI. Para texto sobreposto, uma taxa de 5–10 palavras por segundo ajuda a reter atenção sem saturar a tela. [^3]

Tabela 2 — Matriz de especificações TikTok (orgânico e anúncios)
| Parâmetro | Orgânico | Anúncios (In-Feed/TopView/Pangle etc.) |
|---|---|---|
| Aspect ratio | 9:16 (suporta 1:1 e 16:9) | 9:16 (1:1 e 16:9 tolerados por formato) |
| Resolução | 1080x1920 (ideal); 720p (mínimo) | 720p–1080p |
| Duração | 1 s a 10 min; 9–15 s recomendado para performance | 5–60 s (varia por formato); 9–15 s recomendado |
| FPS | 30 (60 para movimento rápido) | 30 (60 quando aplicável) |
| Formatos/Codecs | MP4/MOV; H.264/AAC | MP4/MOV/MPEG/3GP/AVI; H.264/AAC |
| Tamanho de arquivo | 72 MB (Android); 287,6 MB (iOS); 500 MB; 2 GB (3–10 min) | Até 500 MB (varia por formato) |

Interpretação. A matriz reforça o padrão 9:16 em 1080p/30 fps como baseline e explicita a tolerância a outras proporções por razões de reutilização. A divergência nos limites de tamanho sugere um protocolo de exportação conservador (bitrate moderado, compressão eficiente) e testes pré-publicação para evitar rejeições ou recompressão agressiva da plataforma. [^7][^8][^9][^3]

### 3.2 YouTube Shorts

Especificações principais. Shorts seguem o padrão 9:16 em 1080x1920 e funcionam melhor entre 15 e 60 segundos. As taxas de quadros variam de 24 a 60 fps, com bitrate sugerido entre 1 e 6 Mbps. O contêiner MP4/MOV com H.264 para vídeo e AAC/MP3 para áudio atende à maioria dos fluxos. [^11][^12][^13][^14]

Thumbnails e áreas seguras. Miniaturas não aparecem dentro do player de Shorts, mas sim na aba “Shorts” do canal — reforçando a importância de títulos e primeiros frames para compensar a ausência de thumbnail no player. A recomendação prática é centralizar elementos no “80% central” do quadro para reduzir cortes e sobreposições em diferentes dispositivos e sistemas operacionais. [^11]

Tabela 3 — Resumo técnico YouTube Shorts
| Parâmetro | Diretriz |
|---|---|
| Aspect ratio | 9:16 (1:1 tolerado) |
| Resolução | 1080x1920 (ideal) |
| Duração | 15–60 s |
| FPS | 24–60 |
| Bitrate | 1–6 Mbps |
| Formatos/Codecs | MP4/MOV; H.264; AAC/MP3 |
| Thumbnails | Não aparecem no player; visíveis na aba “Shorts” |

Interpretação. A combinação de duração típica (até 60 s) e bitrate sugerido reforça a necessidade de cortes efficients e legendas legíveis no momento — dado que o espectador está em rolagem vertical e decide em segundos. O posicionamento central dos elementos maximiza a resiliência a variações de UI entre dispositivos. [^11][^12][^13][^14]

### 3.3 Instagram Reels

Especificações principais. O aspect ratio aceita de 1.91:1 a 9:16, sendo 9:16 ideal para tela cheia. O requisito mínimo é 720p e 30 fps. A duração pode chegar a 90 segundos, e o tamanho de arquivo até 4 GB. Capas personalizadas (thumbnails) são recomendadas; a estética tende a ser mais polida que TikTok, mantendo autenticidade. [^1][^15][^16][^17]

Tabela 4 — Requisitos e opções de Instagram Reels
| Parâmetro | Diretriz |
|---|---|
| Aspect ratio | 1.91:1 a 9:16 (9:16 ideal) |
| Resolução | 1080x1920 (ideal); 720p mínimo |
| Duração | Até 90 s |
| FPS | 30+ |
| Formatos/Codecs | MP4/MOV; H.264/AAC (implícito) |
| Tamanho de arquivo | Até 4 GB |
| Capas | Tamanho recomendado: ~420×654 px |

Interpretação. A tolerância de 1.91:1 a 9:16 permite reaproveitamento de vídeos horizontais com moldura central, mas o 9:16 maximiza tela cheia. A ênfase em 30+ fps e 720p mínimo garante estabilidade e clareza, enquanto capas e legendas consistentes elevam o branding sem sacrificar legibilidade. [^1][^15][^16][^17]

## 4. Boas práticas visuais por plataforma

As três plataformas premiam autenticidade, clareza e ritmo. O que muda é o “como” — o grau de polimento, o uso de tendências/áudios, e as expectativas de storytelling.

### 4.1 TikTok: “TikTok-first” e retenção

A estética UGC e nativa da plataforma, com pessoas em primeiro plano e uma narrativa menos polida, ajuda a capturar atenção rapidamente. Estruture o conteúdo em gancho (primeiros 3–6 segundos), proposição de valor e CTA claro. Para texto sobreposto, use 5–10 palavras por segundo e mantenha tudo dentro da zona segura, longe da UI. Sincronize cortes com a batida e explore duetos/stitches e desafios para acelerar a distribuição orgânica. [^3][^4]

### 4.2 YouTube Shorts: abertura forte e conclusão que converte

Shorts pede uma abertura que entrega o “payoff” rapidamente, com uma conclusão que direciona para a peça longa ou outro ativo do canal. Explore teaser/trechos de vídeos longos e end screens quando a experiência pedir continuidade. Centralize elementos no quadro para lidar com variações de UI entre dispositivos. [^11][^21]

### 4.3 Instagram Reels: estética, capa e legendas claras

A estética mais polida funciona bem, desde que mantenha autenticidade. Use capa personalizada, legendas com contraste, elementos AR quando agregam, e CTAs explícitos (seguir, comentar, salvar). Planeje publicações consistentes e crosspromoção (sem marcas d’água), posicionando o primeiro frame como “mini-capa” para maximizar o clique em feeds contextuais. [^17][^19]

## 5. Transições e elementos visuais que mais performam

O objetivo da edição em vídeo curto é sustentar atenção com variação significativa a cada poucos segundos, sem perder coesão narrativa. Padrões eficazes incluem jumpcuts estratégicos, micro-transições (flashes, wipes, speed ramping), loops que promovem replays e overlays gráficos que guiam a leitura. Tipografia cinética de alto contraste ajuda a destacar mensagens-chave. UGC autêntico e BTS (behind-the-scenes) aumentam confiança, enquanto otimização “sem som” (text overlays e legendas) garante compreensão em rolagem silenciosa. [^5][^2][^20]

### 5.1 TikTok: transições nativas e interação

Use transições rápidas e efeitos nativos, sempre sincronizados ao áudio, e recursos como duets/stitches para engajar com a comunidade. Os overlays de texto devem ser concisos, dentro da zona segura, e orientados à retenção. [^3][^4]

### 5.2 YouTube Shorts: ritmo com abertura e finais impactantes

Alinhe cortes à batida, trabalhando com speed ramping e micro-transições suaves para manter fluxo. Construa teasers que prometem um payoff claro e utilize end screens para guiar o próximo passo (ex.: assistir ao vídeo completo). [^11][^21]

### 5.3 Instagram Reels: suavidade e polimento

Prefira transições limpas, usando recursos nativos como o Align (mudança de roupa, continuidade). Capas e legendas devem ser estratégicas e com contraste alto; emojis dão ritmo à legenda, e AR pode reforçar a estética sem sobrecarregar a narrativa. [^17]

## 6. Otimização de timing para máximo engajamento

O timing é o amplifier da retenção: ganchos em 1–3 segundos e variação visual a cada 3–5 segundos reduzem quedas na curva. Hooks visuais que interrompem padrões (p. ex., foco borrado que lentamente se resolve, reflexos inesperados) e áudio design (sons tipo ASMR, silêncios estratégicos) elevam o watch-time. [^5][^22]

Para sistematizar, a Tabela 5 apresenta uma blueprint de cronograma sugerida, aplicável aos três formatos.

Tabela 5 — Blueprint de cronograma (hook → valor → payoff → CTA)
| Janela | Conteúdo | Objetivo | Exemplos de execução |
|---|---|---|---|
| 0–3 s | Hook visual/sonoro | Parar o scroll; ativar curiosidade | Revelação com Post-It; foco borrado que converge; “saindo da tela do celular” |
| 3–6 s | Proposta de valor | Explicar o porquê de ficar | Overlay curto com benefício-chave; corte para demonstração |
| 6–20 s | Entrega de valor | Sustentar watch-time | Micro-transições, speed ramping, overlays gráficos; variabilidade visual a cada 3–5 s |
| 20–s-final | Payoff | Entregar o “momentoaha” | Transformação; antes/depois; demonstração inequívoca |
| Final | CTA | Orientar próximo passo | “Seguir para tutorial completo”; “Link na bio”; end screen (Shorts) |

Interpretação. A cadência descrita maximiza a probabilidade de retenção ao longo do clipe e prepara um fechamento com direção clara. O ritmo de variação visual (3–5 s) evita monotonia e a sequência hook → payoff ajusta expectativas, reduzindo abandono. [^5][^22]

### 6.1 Framework de timing: “Gancho → Entrega → Payoff → CTA”

Os primeiros 3 segundos precisam carregar o impacto central da peça. Ganchos baseados em curiosidade e interrupção de padrão aumentam a chance de retenção até o payoff. CTAs não devem competir com o fechamento: permita que a conclusão seja clara e depois convide à ação. [^22]

### 6.2 Ritmo e variedade visual (3–5 s)

Adote padrões de edição com speed ramping e jumpcuts estratégicos, alternando close-ups e planos abertos. Variety não é ruído: é a manutenção da atenção, desde que a narrativa retenha coesão. [^5]

### 6.3 Áudio e “modo sem som”

Layering de som ambiente e ASMR, com sincronização de cortes à batida, reforça o ritmo. Em paralelo, otimize para “sem som”: text overlays legíveis e legendas cuidam da compreensão no scroll silencioso, preservando a mensagem. [^2]

## 7. Produção, QA e entrega: do plano ao upload

Pré-produção. Defina o aspect ratio (9:16), resolusi target (1080x1920) e framing com margens seguras. Planeje texto, cores e tipografia com contraste, e prepare storyboard para janelas de timing (hook, variações, payoff).

Filmagem. Padronize 30 fps (60 fps quando necessário), use iluminação natural/difusa, garanta estabilidade e registre áudio limpo (microfone externo quando possível). Evite cortes abruptos, planeje transições a serem executadas no场内.

Edição. Estruture cortes por beat; assegure legibilidade de overlays, contraste e marcação de CTAs. Remova marcas d’água de outras plataformas, especialmente ao crosspromover para Instagram.

QA. Valide duração versus limites da plataforma; confirme tamanho do arquivo; prefira H.264/AAC em contêiner MP4/MOV; teste a experiência sem som e a legibilidade do primeiro frame. [^1][^3][^11]

Publicação. Use capas personalizadas (quando aplicável), legendas com contexto, hashtags relevantes e consistência de postagem (ex.: 3–5 Reels/semana quando o objetivo for crescimento). [^17]

Para consolidar, a Tabela 6 sugere presets de exportação por plataforma, a serem validados em QA.

Tabela 6 — Presets de exportação sugeridos (a validar em QA)
| Plataforma | Container/Codec | Resolução | FPS | Bitrate | Duração alvo |
|---|---|---|---|---|---|
| TikTok | MP4/MOV; H.264/AAC | 1080x1920 | 30 (60 se movimento intenso) | Moderado (evitar exceder limites de tamanho) | 9–15 s (orgânico), 5–60 s (ads) |
| YouTube Shorts | MP4/MOV; H.264; AAC/MP3 | 1080x1920 | 24–60 | 1–6 Mbps | 15–60 s |
| Instagram Reels | MP4/MOV; H.264/AAC | 1080x1920 | 30+ | Moderado (até 4 GB) | 15–30 s (tutoriais: 30–60 s); até 90 s |

Interpretação. A adoção de presets padronizados reduz erros de compatibilidade e recompressão. Ajustes finos de bitrate devem considerar o equilíbrio entre qualidade e limites de arquivo, especialmente no TikTok. [^7][^8][^1][^11]

## 8. Medição e experimentação contínua

Métricas prioritárias. Concentre-se na curva de retenção (queda nos primeiros segundos), Completion Rate (taxa de conclusão), engajamento (curtidas, comentários, compartilhamentos, salvamentos) e CTR quando houver CTA.

Testes A/B. Variações de hook, primeiro frame, timing de transições e soundscape. Execute rotinas de atualização de criativos para mitigar fadiga (queda de performance de hooks após 7 dias) e registre sistemicamente as variantes vencedoras. [^22]

Ferramentas e benchmarks. Use Video Insights (TikTok) e analytics do YouTube Studio para entender retenção e replay; busque benchmarks de engajamento por plataforma para calibrar metas e metas de creativa. [^25][^6]

Fluxo de aprendizado. Adote sprints quinzenais, library viva de hooks e padrões de edição, e calendários de rotação criativa para manter freshness.

## 9. Apêndices

### 9.1 Glossário técnico
- Aspect ratio: relação largura/altura do vídeo (ex.: 9:16).
- FPS (frames por segundo): taxa de quadros; 30 fps é o padrão comum.
- Bitrate: taxa de bits por segundo; influencia qualidade e tamanho do arquivo.
- Safe area: região do quadro onde elementos críticos não são sobrepostos pela UI.
- UGC: user-generated content; estética nativa e autêntica.
- BTS: behind-the-scenes; bastidores que humanizam a marca.
- Speed ramping: variação intencional de velocidade para enfatizar momentos.
- CTA: call to action; convite claro para uma ação.

### 9.2 Notas sobre atualizações e validação

As plataformas podem alterar parâmetros de forma dinâmica. Valide sempre no momento do upload: duração máxima, tolerância de aspect ratio, limites de tamanho de arquivo, presença de miniaturas, e zonas seguras. Mantenha um log de versões com data e fonte. [^18][^23][^24]

### 9.3 Referências

[^1]: Instagram Help Center. Instagram Reel requirements. https://help.instagram.com/1038071743007909  
[^2]: Superside. 7 Short-Form Video Trends to Maximize Impact in 2025. https://www.superside.com/blog/short-form-video-trends  
[^3]: TikTok For Business. Creative best practices for performance ads. https://ads.tiktok.com/help/article/creative-best-practices?lang=en  
[^4]: TikTok For Business. What’s Next 2025 Trend Report (PDF). https://ads.tiktok.com/business/library/TikTok_Whats_Next_2025_Trend_Report_en_AUNZ.pdf  
[^5]: Onadverts. Top Video Editing Trends for Social Media in 2025. https://onadverts.com/top-video-editing-trends-for-social-media-in-2025/  
[^6]: Sprout Social. Social Media Video Statistics (2025). https://sproutsocial.com/insights/social-media-video-statistics/  
[^7]: Riverside. TikTok Video Size Guide: Best Dimensions for 2025. https://riverside.com/blog/tiktok-video-size  
[^8]: Descript. TikTok Video Dimensions in 2025: The Complete Guide. https://www.descript.com/blog/article/tiktok-video-size  
[^9]: Fliki. The Ultimate Guide to TikTok Video Size for 2025. https://fliki.ai/blog/tiktok-video-size  
[^10]: Adobe Community. Best settings for rendering TikTok 1080×1920. https://community.adobe.com/t5/after-effects-discussions/best-settings-for-rendering-tiktok-1080-1920/td-p/12468460  
[^11]: BigMotion. YouTube Shorts Dimensions in 2025. https://www.bigmotion.ai/blog/youtube-shorts-dimensions-in-2025  
[^12]: Riverside. YouTube Video Size Full Guide: Best Dimensions for 2025. https://riverside.com/blog/youtube-video-size  
[^13]: Hootsuite. YouTube Shorts: Everything you need to know in 2025. https://blog.hootsuite.com/youtube-shorts/  
[^14]: PostFast. YouTube Shorts Size & Dimensions Guide 2025. https://postfa.st/sizes/youtube/shorts/2025  
[^15]: Outfy. Instagram Reels Size and Dimensions in 2025. https://www.outfy.com/blog/instagram-reel-size/  
[^16]: Influencer Marketing Hub. Instagram Video Sizes & Formats in 2025. https://influencermarketinghub.com/instagram-video-size/  
[^17]: Riverside. Instagram Reels Dimensions 101 | Size & Formatting Guide (2025). https://riverside.com/blog/instagram-reels-dimensions  
[^18]: Socialinsider. TikTok vs. Reels vs. Shorts (A Study by Socialinsider). https://www.socialinsider.io/blog/tiktok-vs-reels-vs-shorts/  
[^19]: StackInfluence. Video Content Optimization in 2025: TikTok, Reels, YouTube. https://stackinfluence.com/video-content-optimization-in-2025/  
[^20]: TechSmith. 12 Video Marketing Trends Reshaping Content Strategy in 2025. https://www.techsmith.com/blog/video-marketing-trends/  
[^21]: YouTube Blog. Transitioning your long-form content to YouTube Shorts. https://blog.youtube/creator-and-artist-stories/transitioning-your-long-form-content-to-youtube-shorts/  
[^22]: Motion. 25 Video Ad Hooks that Convert in 2025. https://motionapp.com/blog/best-dtc-meta-ad-hooks-2025  
[^23]: Wayin AI. Instagram Video Length Limits 2025: Ultimate Guide. https://wayin.ai/blog/instagram-video-length-limit/  
[^24]: SocialPilot. Instagram Video Sizes, Dimensions & Formats in 2025. https://www.socialpilot.co/instagram-marketing/instagram-video-size-specifications  
[^25]: TikTok For Business. Video Insights. https://ads.tiktok.com/help/article/video-insights