---
name: atualizar-bracket
description: Atualiza os vencedores dos confrontos do bracket da Copa 2026 (index.html) conforme os jogos acontecem, e opcionalmente faz o deploy (commit + push p/ GitHub Pages). Use quando o usuário disser quem venceu um ou mais jogos, pedir para cravar resultados, atualizar o chaveamento, ou publicar a atualização do site.
---

# Atualizar bracket da Copa 2026

Este repositório é um site estático (`index.html`) com o chaveamento do mata-mata
da Copa do Mundo 2026, publicado em GitHub Pages: https://lgcantarelli.github.io/copa-2026/

A skill atualiza os **vencedores dos confrontos** conforme os jogos terminam.
Toda a lógica está no script `scripts/set_winner.py`, que edita o objeto
`RESULTS` dentro do `index.html` (a única parte que muda no dia-a-dia).

## Quando usar

O usuário diz algo como "Brasil ganhou do Japão", "cravar Argentina e Espanha",
"Alemanha passou nas oitavas", "atualiza o bracket: …", ou "publica os resultados".

## Como usar

Rode sempre a partir da raiz do repo. Cada vencedor é `JOGO=TIME`, onde TIME pode
ser o **nome** (com ou sem acento, case-insensitive) ou o **seed** (ex.: `1ºC`).

```bash
# cravar um ou vários vencedores (acumula com os já existentes):
python3 scripts/set_winner.py 76=Brasil 86=Argentina 84=Espanha

# ver o estado atual sem escrever nada:
python3 scripts/set_winner.py --list

# remover o resultado de um jogo / zerar tudo:
python3 scripts/set_winner.py --clear 76
python3 scripts/set_winner.py --clear-all

# gravar E publicar (commit + push -> GitHub Pages atualiza em ~1 min):
python3 scripts/set_winner.py 76=Brasil --deploy
```

O script é seguro e idempotente: valida o time contra os dois que estão naquele
jogo, recusa em caso de erro (time inexistente, jogo ainda incompleto), e não
muda nada se o resultado já estava cravado.

## Numeração dos jogos

- **16-avos:** M73–M88
- **Oitavas:** M89–M96 · **Quartas:** M97–M100 · **Semis:** M101, M102 · **Final:** M104

Os jogos derivados (oitavas em diante) só aceitam um vencedor depois que **os dois
jogos que os alimentam já têm vencedor cravado**. Portanto crave **em ordem de
rodada** (16-avos primeiro). Se você tentar cravar um jogo incompleto, o script
avisa quais times faltam.

## Fluxo recomendado

1. Descobrir/confirmar quem venceu (o usuário informa, ou busque na web se pedir).
2. Rodar `set_winner.py` com os pares `JOGO=TIME`.
3. Conferir com `--list`.
4. (Opcional, mas em geral é o que o usuário quer) publicar: rodar de novo com
   `--deploy`, OU commitar e dar push manualmente:
   ```bash
   git add index.html && git commit -m "chore: atualizar vencedores do bracket" && git push
   ```
5. Confirmar a URL ao usuário: https://lgcantarelli.github.io/copa-2026/

## Verificação visual (opcional)

Para conferir que o HTML continua válido e os times avançaram certo:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-sandbox --hide-scrollbars --window-size=1640,820 \
  --screenshot=/tmp/wc_check.png "file://$PWD/index.html"
```

## Não fazer

- Não editar o `RESULTS` à mão se der pra usar o script (ele valida e comenta).
- Não mexer em `R32TEAMS` por aqui — aquilo são os 16-avos fixos (só muda se a
  classificação dos grupos for corrigida, que é outra tarefa).
- Antes de `--deploy` / push, confirme com o usuário se ele quer mesmo publicar
  (o site é público).
