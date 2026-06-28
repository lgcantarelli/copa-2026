#!/usr/bin/env python3
"""Atualiza os vencedores dos confrontos no bracket da Copa 2026 (index.html).

Reescreve o objeto `RESULTS` dentro de index.html. Você informa o vencedor de
cada jogo por NÚMERO do jogo + um identificador do time (nome, ex. "Brasil", ou
seed, ex. "1ºC"). O script resolve quem está em cada jogo replicando a árvore do
bracket (R32TEAMS + FEED), valida, e regrava RESULTS preservando o resto do HTML.

Uso:
  # cravar vencedores (acumula com os já existentes):
  python3 scripts/set_winner.py 76=Brasil 86=Argentina 84="Espanha"
  python3 scripts/set_winner.py 76=1ºC 74=1ºE      # por seed também funciona

  # remover/zerar:
  python3 scripts/set_winner.py --clear 76          # tira só o M76
  python3 scripts/set_winner.py --clear-all         # zera tudo

  # dry-run: mostrar o que mudaria (vs. RESULTS atual) SEM gravar:
  python3 scripts/set_winner.py --diff 76=Brasil 86=Argentina

  # ver o estado atual sem escrever:
  python3 scripts/set_winner.py --list

  # commitar e dar push depois de gravar (deploy via GitHub Pages):
  python3 scripts/set_winner.py 76=Brasil --deploy

Notas:
  - "76=Brasil" = o time Brasil vence o jogo 76. Aceita acento e é
    case-insensitive; aceita também o seed ("1ºC").
  - Para jogos derivados (oitavas+) o time só existe depois que seus dois
    feeders têm vencedor cravado — então crave em ordem (16-avos primeiro).
  - O script é idempotente: rodar de novo com os mesmos args não muda nada.
"""
import argparse
import os
import re
import subprocess
import sys
import unicodedata

HTML = os.path.join(os.path.dirname(__file__), "..", "index.html")

# Estrutura do bracket — espelha FEED no index.html. R32 (73-88) são folhas.
FEED = {
    89: (74, 77), 90: (73, 75), 91: (76, 78), 92: (79, 80),
    93: (83, 84), 94: (81, 82), 95: (86, 88), 96: (85, 87),
    97: (89, 90), 98: (93, 94), 99: (91, 92), 100: (95, 96),
    101: (97, 98), 102: (99, 100), 104: (101, 102),
}
ALL_MATCHES = list(range(73, 89)) + sorted(FEED)


def _norm(s):
    """lower + sem acento, para casar nomes digitados de forma relaxada."""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower().strip()


def read_html():
    with open(HTML, encoding="utf-8") as f:
        return f.read()


def parse_r32(src):
    """Extrai R32TEAMS -> {match: [(seed_a, name_a), (seed_b, name_b)]}."""
    block = re.search(r"var R32TEAMS = \{(.*?)\n  \};", src, re.S)
    if not block:
        sys.exit("ERRO: não achei o bloco R32TEAMS em index.html.")
    teams = {}
    # cada T('flag','nome','seed'[,1]) -> capturamos nome e seed
    for m in re.finditer(
        r"(\d+):\s*\[(.*?)\](?:,|\s*\n)", block.group(1), re.S
    ):
        num = int(m.group(1))
        cells = re.findall(
            r"T\('[^']*','([^']*)','([^']*)'(?:,\s*1)?\)", m.group(2)
        )
        if len(cells) == 2:
            # cells = [(nome, seed), (nome, seed)]
            teams[num] = [(c[1], c[0]) for c in cells]  # (seed, nome)
    return teams


def parse_results(src):
    """Extrai o RESULTS atual (linhas não-comentadas) -> {match: seed}."""
    block = re.search(r"var RESULTS = \{(.*?)\n  \};", src, re.S)
    if not block:
        sys.exit("ERRO: não achei o bloco RESULTS em index.html.")
    res = {}
    for line in block.group(1).splitlines():
        code = line.split("//", 1)[0]  # ignora comentários
        for m in re.finditer(r"(\d+)\s*:\s*'([^']+)'", code):
            res[int(m.group(1))] = m.group(2)
    return res


def build_resolver(r32):
    """Devolve teamsOf(match, results) -> [(seed,nome) ou None, (seed,nome) ou None].

    Replica teamOf/applyResults do HTML: o time de um slot derivado é o vencedor
    cravado do feeder correspondente (ou None se ainda indefinido).
    """
    def winner_team(match, results):
        seed = results.get(match)
        if seed is None:
            return None
        for t in teams_of(match, results):
            if t and t[0] == seed:
                return t
        return None

    def teams_of(match, results):
        if match in r32:
            return list(r32[match])
        fa, fb = FEED[match]
        return [winner_team(fa, results), winner_team(fb, results)]

    return teams_of, winner_team


def resolve_seed(match, token, teams_of, results):
    """Dado '76' e 'Brasil' (ou '1ºC'), devolve o seed daquele time no jogo."""
    slots = teams_of(match, results)
    present = [t for t in slots if t]
    if len(present) < 2:
        names = [f"{t[1]} ({t[0]})" for t in present] or ["(nenhum ainda)"]
        sys.exit(
            f"ERRO: jogo M{match} ainda não tem os dois times definidos "
            f"(crave os feeders antes). Times presentes: {', '.join(names)}"
        )
    tok = _norm(token)
    for seed, name in present:
        if _norm(seed) == tok or _norm(name) == tok:
            return seed
    opts = " | ".join(f"{n} ({s})" for s, n in present)
    sys.exit(f"ERRO: '{token}' não bate com nenhum time do M{match}. Opções: {opts}")


def render_results_block(results, r32, teams_of):
    """Gera o miolo do objeto RESULTS, com um comentário do nome do vencedor."""
    if not results:
        body = (
            "    // (vazio) crave vencedores com: "
            "python3 scripts/set_winner.py <jogo>=<time>\n"
        )
        return body
    lines = []
    for m in sorted(results):
        seed = results[m]
        # acha o nome para o comentário
        name = "?"
        for s, n in (teams_of(m, results) or []):
            if s == seed:
                name = n
                break
        lines.append(f"    {m}: '{seed}',  // {name}")
    return "\n".join(lines) + "\n"


def write_results(src, body):
    new, n = re.subn(
        r"(var RESULTS = \{\n).*?(\n  \};)",
        lambda mo: mo.group(1) + body + "  };",
        src,
        count=1,
        flags=re.S,
    )
    if n != 1:
        sys.exit("ERRO: falha ao reescrever o bloco RESULTS.")
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(new)


def cmd_list(r32, teams_of, results):
    if not results:
        print("Nenhum vencedor cravado ainda.")
        return
    print("Vencedores cravados:")
    for m in sorted(results):
        seed = results[m]
        name = next((n for s, n in teams_of(m, results) if s == seed), "?")
        print(f"  M{m}: {name} ({seed})")


def deploy():
    root = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
    print("Deploy: commit + push…")
    subprocess.run(["git", "-C", root, "add", "index.html"], check=True)
    subprocess.run(
        ["git", "-C", root, "commit", "-m", "chore: atualizar vencedores do bracket"],
        check=True,
    )
    subprocess.run(["git", "-C", root, "push"], check=True)
    print("Push OK — GitHub Pages atualiza em ~1 min: https://lgcantarelli.github.io/copa-2026/")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("picks", nargs="*", help="pares jogo=time, ex.: 76=Brasil 84=1ºH")
    ap.add_argument("--clear", type=int, metavar="JOGO", help="remove o vencedor de um jogo")
    ap.add_argument("--clear-all", action="store_true", help="zera todos os vencedores")
    ap.add_argument("--list", action="store_true", help="mostra os vencedores atuais e sai")
    ap.add_argument("--diff", action="store_true",
                    help="dry-run: mostra o que mudaria (vs. RESULTS atual) e NÃO grava")
    ap.add_argument("--deploy", action="store_true", help="commit + push após gravar")
    args = ap.parse_args()

    src = read_html()
    r32 = parse_r32(src)
    teams_of, _ = build_resolver(r32)
    current = parse_results(src)

    if args.list:
        cmd_list(r32, teams_of, current)
        return

    # Constrói o estado-alvo a partir do atual + clears + picks.
    results = {} if args.clear_all else dict(current)
    if args.clear is not None:
        results.pop(args.clear, None)

    for pick in args.picks:
        if "=" not in pick:
            sys.exit(f"ERRO: '{pick}' não está no formato jogo=time (ex.: 76=Brasil).")
        num_s, token = pick.split("=", 1)
        if not num_s.strip().isdigit():
            sys.exit(f"ERRO: número de jogo inválido em '{pick}'.")
        match = int(num_s.strip())
        if match not in ALL_MATCHES:
            sys.exit(f"ERRO: jogo M{match} não existe (válidos: 73–88, 89–102, 104).")
        seed = resolve_seed(match, token, teams_of, results)
        results[match] = seed

    diff = compute_diff(current, results, teams_of)
    print_diff(diff)

    if args.diff:
        return  # dry-run: nunca grava

    if not diff:
        return

    body = render_results_block(results, r32, teams_of)
    write_results(src, body)
    print("\nindex.html atualizado.")

    if args.deploy:
        deploy()


def compute_diff(current, target, teams_of):
    """Lista (match, antes, depois) para cada jogo que mudaria. Vazio = nada muda."""
    def label(match, results, seed):
        if seed is None:
            return "—"
        name = next((n for s, n in teams_of(match, results) if s == seed), "?")
        return f"{name} ({seed})"

    out = []
    for m in sorted(set(current) | set(target)):
        before, after = current.get(m), target.get(m)
        if before != after:
            out.append((m, label(m, current, before), label(m, target, after)))
    return out


def print_diff(diff):
    if not diff:
        print("Sem mudanças: o RESULTS já está em dia com o que foi informado.")
        return
    print("Mudanças a aplicar:")
    for m, before, after in diff:
        print(f"  M{m}: {before}  ->  {after}")


if __name__ == "__main__":
    main()
