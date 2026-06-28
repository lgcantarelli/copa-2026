---
name: atualizar-bracket
description: Descobre numa fonte confiável (Wikipedia) quem venceu os jogos do mata-mata da Copa 2026 já encerrados, compara com o bracket (index.html), mostra o diff e — após confirmação — atualiza e publica (GitHub Pages). Também aceita vencedores informados manualmente. Use quando o usuário pedir para atualizar o bracket/chaveamento, cravar resultados, "ver quem ganhou e atualizar o site", ou publicar a atualização.
---

# Atualizar bracket da Copa 2026

Repositório de um site estático (`index.html`) com o chaveamento do mata-mata da
Copa do Mundo 2026, publicado em GitHub Pages:
https://lgcantarelli.github.io/copa-2026/

A skill mantém os **vencedores dos confrontos** em dia. Toda a manipulação do
arquivo é feita pelo script `scripts/set_winner.py`, que edita o objeto `RESULTS`
no `index.html` (a única parte que muda no dia-a-dia) e valida cada vencedor
contra os dois times daquele jogo.

## Quando usar

"Atualiza o bracket", "vê quem ganhou e atualiza o site", "cravar os resultados
de hoje", "Brasil ganhou do Japão", "publica os resultados".

---

## Fluxo principal: descobrir os resultados sozinho (fonte confiável)

Use este fluxo quando o usuário NÃO ditar os placares — ele quer que a skill
descubra. **Nunca grave sem antes mostrar o diff e ter confirmação do usuário.**

1. **Saber o que já está cravado** (pra não refazer trabalho):
   ```bash
   python3 scripts/set_winner.py --list
   ```

2. **Buscar a fonte confiável — Wikipedia (canônica deste projeto).**
   Página do knockout stage:
   `https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_knockout_stage`
   Use WebFetch pedindo, para cada jogo do mata-mata **já encerrado**, o
   **vencedor** (quem avançou) — incluindo decisões por pênaltis. Se a página de
   knockout estiver incompleta, complemente com a página principal
   `2026_FIFA_World_Cup`. Só considere um jogo se o resultado for **final**
   (jogo terminado); ignore jogos não disputados / em andamento.

3. **Mapear cada vencedor para o número do jogo (M73–M104).** A correspondência
   jogo→confronto está em `index.html` (`R32TEAMS` para os 16-avos; `FEED` para a
   árvore). Os 16-avos são M73–M88; veja a numeração completa abaixo. Para um jogo
   de oitavas+ você precisa que os dois feeders já tenham vencedor (crave em ordem
   de rodada).

4. **Mostrar o diff (dry-run, não grava):**
   ```bash
   python3 scripts/set_winner.py --diff 76=Brasil 86=Argentina 84=Espanha ...
   ```
   Isso imprime, por jogo, `antes -> depois`. **Apresente esse diff ao usuário**
   (ex.: "M76: — -> Brasil; M86: — -> Argentina") e pergunte se pode aplicar.

5. **Ao confirmar, aplicar** (mesma linha, sem `--diff`):
   ```bash
   python3 scripts/set_winner.py 76=Brasil 86=Argentina 84=Espanha ...
   ```

6. **Publicar** (se o usuário quiser; o site é público — confirme antes):
   ```bash
   python3 scripts/set_winner.py --deploy   # commit + push; Pages atualiza ~1 min
   # (sem novos picks, só publica o que já está gravado)
   ```
   ou manualmente: `git add index.html && git commit -m "…" && git push`.

> Regra de ouro: **fonte → diff → confirmação → aplicar → publicar.** Em caso de
> dúvida sobre um placar (jogo apertado, pênaltis, fonte ambígua), NÃO crave —
> reporte a incerteza ao usuário.

---

## Fluxo manual: o usuário já disse quem ganhou

Pule a busca. Cada vencedor é `JOGO=TIME`, onde TIME é o **nome** (com/sem acento,
case-insensitive) ou o **seed** (`1ºC`).

```bash
python3 scripts/set_winner.py --diff 76=Brasil 84=Espanha   # confira o diff
python3 scripts/set_winner.py 76=Brasil 84=Espanha           # aplique
python3 scripts/set_winner.py 76=Brasil --deploy             # aplique + publique
```

Outros comandos:
```bash
python3 scripts/set_winner.py --list          # ver vencedores atuais
python3 scripts/set_winner.py --clear 76      # remover um jogo
python3 scripts/set_winner.py --clear-all     # zerar tudo
```

O script é idempotente e valida tudo: recusa time que não está no jogo (mostra as
opções) e jogo derivado ainda incompleto (avisa quais feeders faltam).

## Numeração dos jogos

- **16-avos:** M73–M88
- **Oitavas:** M89–M96 · **Quartas:** M97–M100 · **Semis:** M101, M102 · **Final:** M104

Jogos derivados só aceitam vencedor depois que **os dois jogos que os alimentam já
têm vencedor cravado**. Crave **em ordem de rodada** (16-avos primeiro).

## Verificação visual (opcional)

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-sandbox --hide-scrollbars --window-size=1640,820 \
  --screenshot=/tmp/wc_check.png "file://$PWD/index.html"
```

## Não fazer

- Não gravar sem mostrar o diff e ter confirmação do usuário.
- Não cravar resultado de jogo não finalizado ou de placar incerto.
- Não editar `RESULTS` à mão (use o script — ele valida e comenta).
- Não mexer em `R32TEAMS` (são os 16-avos fixos; só mudam se a classificação dos
  grupos for corrigida — outra tarefa).
- Confirmar com o usuário antes de `--deploy`/push (o site é público).
