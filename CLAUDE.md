---
tipo: contexto
projeto: Copa 2026 bracket
criado: 2026-06-28
atualizado: 2026-06-28
status: 16-avos definidos · mata-mata em andamento
---

# Contexto — Bracket HTML da Copa do Mundo 2026

Documento de referência para o arquivo interativo do chaveamento do mata-mata da
Copa 2026. Substitui o handoff antigo ("Atualizar 16-avos"), cuja tarefa já foi
concluída em 28/jun (fase de grupos encerrada, 16-avos reescritos com os dados
finais). A partir de agora a manutenção é só **cravar vencedores conforme os
jogos acontecem**.

## Arquivo

- **Único arquivo a editar:** `index.html` (na raiz deste repo).
  - Standalone (`<meta charset="utf-8">`), pode ser servido avulso.
- Manutenção do dia-a-dia: usar o script `scripts/set_winner.py` (valida e
  comenta o objeto `RESULTS`).

## O que o arquivo faz

- Bracket completo do mata-mata: 16-avos (M73–M88) → oitavas → quartas → semis →
  final (M104), desenhado da esquerda para a direita com as duas metades.
- **16-avos vêm preenchidos**; das oitavas em diante começa "a definir" e vai
  sendo preenchido pelos resultados/cliques.
- **Interativo:** clicar numa célula = aquele time vence e avança. Re-clicar no
  escolhido = desmarca (cascata pra frente). Trocar de palpite limpa o caminho à
  frente. Botão "Reiniciar" volta aos **resultados oficiais** (não zera tudo).

## Como atualizar conforme os jogos acontecem (a tarefa recorrente)

Editar **somente** o objeto `RESULTS` (perto da linha 183, logo abaixo de
`R32TEAMS`). Para cravar o vencedor de qualquer jogo — das oitavas à final —
adicionar/descomentar uma linha:

```js
var RESULTS = {
  76:  '1ºC',   // Brasil vence o M76
  89:  '1ºE',   // vencedor do M89 (use o seed do time que ganhou aquele confronto)
  104: '1ºJ',   // campeão
};
```

- **Chave** = número do jogo (M73..M104).
- **Valor** = o **seed** que aparece na célula do time vencedor: `1ºC`, `2ºH`,
  `3ºD`… (o mesmo rótulo mostrado na UI).
- Funciona em todas as fases. Nas rodadas derivadas (oitavas+), use o seed do
  time que efetivamente venceu — ele cascateia sozinho pro próximo jogo via
  `applyResults()`.
- Comentar/remover a linha devolve o jogo a "em aberto".
- Seed errado ou time ainda indefinido → `console.warn('RESULTS: jogo Mxx ...')`,
  o resto continua funcionando.
- Cliques no bracket continuam funcionando por cima dos resultados cravados.

### Verificação visual headless (sem erro de JS, bandeiras intactas)

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-sandbox --hide-scrollbars --window-size=1640,820 \
  --screenshot=/tmp/wc_check.png "file://$PWD/index.html"
```

Abrir o PNG e conferir.

## Estrutura interna (mapa do código)

| O quê | Onde (linha aprox.) | Papel |
|---|---|---|
| `function T(f,n,s,third)` | 156 | Fábrica de time: `{f:flag, n:nome, s:seed, third:bool}` |
| `R32TEAMS` | 157 | Os 16 jogos dos 16-avos (folhas fixas). Só se mexe aqui se a fase de grupos mudar |
| `RESULTS` | 183 | **Onde se edita no dia-a-dia.** Vencedores cravados por jogo |
| `applyResults()` | 195 | Semeia o estado `winner` a partir de `RESULTS`, em ordem de rodada |
| `FEED` | 212 | Árvore do bracket: cada jogo derivado conhece seus dois feeders |
| `winner` | 224 | Estado: por jogo, `{slot:'a'|'b', team:<obj>}` (ausente = indefinido) |
| `cleanup()` | 242 | Cascata: dropa picks cujo time-origem mudou (identidade de objeto) |
| `pick(m,slot)` | 253 | Handler de clique |
| `<div class="sub">` | 109 | Subtítulo (hoje: "Fase de grupos encerrada · 16-avos definidos") |

### Estrutura do chaveamento (VALIDADA — não regredir)

```
R32 (16-avos): M73..M88 (folhas com times fixos)
R16:  89:[74,77] 90:[73,75] 91:[76,78] 92:[79,80]
      93:[83,84] 94:[81,82] 95:[86,88] 96:[85,87]
QF:   97:[89,90] 98:[93,94] 99:[91,92] 100:[95,96]
SF:   101:[97,98]   102:[99,100]
Final:104:[101,102]
```

Fato confirmado: **Brasil (M76) e Argentina (M86) estão na MESMA metade** → se
cruzariam na semi (M102), não na final.

## Estado dos 16-avos (FINAL, fase de grupos encerrada — 28/jun/2026)

Reescrito com a classificação final dos 12 grupos. Os 8 melhores terceiros vêm
dos grupos **{B, D, E, F, I, J, K, L}**; alocação confirmada pela tabela oficial
da FIFA (template do Wikipedia → colunas 1A,1B,1D,1E,1G,1I,1K,1L =
`3E,3J,3B,3D,3I,3F,3L,3K`) e batendo com o bracket oficial.

| M | Mandante (1º/2º) | Visitante |
|---|---|---|
| 73 | 2ºA África do Sul | 2ºB Canadá |
| 74 | 1ºE Alemanha | 3ºD Paraguai |
| 75 | 1ºF Holanda | 2ºC Marrocos |
| 76 | 1ºC Brasil | 2ºF Japão |
| 77 | 1ºI França | 3ºF Suécia |
| 78 | 2ºE Costa do Marfim | 2ºI Noruega |
| 79 | 1ºA México | 3ºE Equador |
| 80 | 1ºL Inglaterra | 3ºK RD Congo |
| 81 | 1ºD EUA | 3ºB Bósnia |
| 82 | 1ºG Bélgica | 3ºI Senegal |
| 83 | 2ºK Portugal | 2ºL Croácia |
| 84 | 1ºH Espanha | 2ºJ Áustria |
| 85 | 1ºB Suíça | 3ºJ Argélia |
| 86 | 1ºJ Argentina | 2ºH Cabo Verde |
| 87 | 1ºK Colômbia | 3ºL Gana |
| 88 | 2ºD Austrália | 2ºG Egito |

## Fontes de dados (para qualquer revalidação futura)

- Classificação dos grupos / bracket: NBC Sports (tabela dos 12 grupos),
  FIFA standings, Wikipedia (`2026_FIFA_World_Cup_knockout_stage`).
- Tabela oficial de alocação dos terceiros (495 combinações) — NÃO usar WebFetch
  nessa página, baixar o RAW:
  ```bash
  curl -s "https://en.wikipedia.org/wiki/Template:2026_FIFA_World_Cup_third-place_table?action=raw" > /tmp/wc3rd.wiki
  ```
  O parser certo: cada linha de dados tem os grupos presentes como `'''X'''` e
  os 8 terceiros como os últimos tokens `3X`, na ordem 1A,1B,1D,1E,1G,1I,1K,1L.
  Achar a linha cujo conjunto de grupos == os 8 grupos dos terceiros classificados.
