# Importando as bibliotecas necessárias
from time import sleep
from unidecode import unidecode
from random import choice
from os import path
from json import dump
from typing import Sequence
from rich import print as rprint
from enum import Enum

# Criação de utilitários
TEMPO_PADRAO = 0.05  # Tempo de digitação padrão


class TipoFim(Enum):
    NOVA_LINHA = 0
    VAZIO = 1
    INPUT = 2


def digitar(
    mensagem: str,
    /,
    tipo_fim: TipoFim = TipoFim.NOVA_LINHA,
    tempo: int | float | None = None,
) -> str:
    if tempo is None:
        tempo = TEMPO_PADRAO

    for letra in mensagem:
        rprint(letra, end="", flush=True)
        sleep(tempo)
    if tipo_fim == TipoFim.INPUT:
        return input()
    if tipo_fim == TipoFim.VAZIO:
        print(end="")
    else:
        print()
    return ""


def validar_resposta(
    mensagem: str,
    conjunto_resposta: Sequence[str],
    mensagem_erro: str,
    /,
    tipo_fim: TipoFim = TipoFim.NOVA_LINHA,
    tempo: int | float | None = None,
    num_caracteres: int = -1,
) -> str:
    respostas_validas = [
        unidecode(resposta).replace(" ", "").upper() for resposta in conjunto_resposta
    ]

    while True:
        resposta = digitar(
            mensagem,
            tipo_fim=TipoFim.INPUT,
            tempo=tempo,
        ).strip()
        resposta = unidecode(resposta).replace(" ", "").upper()
        if num_caracteres > 0:
            resposta = resposta[:num_caracteres]
        if resposta in respostas_validas:
            return resposta
        digitar(mensagem_erro, tipo_fim, tempo)


# Introduzindo o jogador ao jogo
digitar(
    "Seja bem vindo ao jogo [bold]LETRIMAX[/], você terá "
    "[bold]6[/] chances para adivinhar a [bold]PALAVRA SECRETA[/], "
    "que tem [bold]5[/] letras.",
    TipoFim.VAZIO,
)

digitar(
    "A cada palavra digitada você verá sua palavra novamente, "
    "mas algumas letras estarão pintadas.\n"
    "[green]C A[/] [bold]U[/] [yellow]S A[/]"
)

digitar(
    "No exemplo anterior, o [bold]C[/] e o primeiro [bold]A[/] "
    "estão na palavra e na posição correta, pois estão na cor verde.\n"
    "As letras [bold]S[/] e o outro [bold]A[/] estão na posição errada, "
    "mas estão na palavra.\n"
    "E a letra [bold]U[/] não está na palavra.",
    TipoFim.INPUT,
)

digitar("[green]C A M A S[/]\nNesse caso, a palavra foi descoberta.")

digitar("Já vou avisando, parece simples, mas não é.", TipoFim.INPUT)

# Escolha da velocidade de digitação
while True:
    try:
        ent = (
            digitar(
                "Digite a velocidade da escrita em segundos (padrão = 0.05): ",
                TipoFim.INPUT,
            )
            .replace(" ", "")
            .replace(",", ".")
        )

        if ent != "":
            TEMPO_PADRAO = float(ent)
        if TEMPO_PADRAO < 0:
            digitar("Erro! Sua entrada não pode ser menor que 0.")
            continue
        if TEMPO_PADRAO >= 1.5:
            digitar("Tá de sacanagem, né?! Escolha um valor menor que 1.5.")
            continue

        digitar("Texto de exemplo")
        conf = validar_resposta(
            "Deseja manter nessa velocidade? [S/N] ",
            ["S", "N"],
            "Resposta inválida, tente novamente.",
            tempo=0.05,
            num_caracteres=1,
        )
        if conf == "S":
            break
    except ValueError:
        digitar("Tente novamente.")

digitar("\nAperte enter para começar ", TipoFim.INPUT)

# Importando lista de todas as palavras com 5 letras da língua portuguesa
palavras = []

try:
    with open("br-utf8.txt", encoding="utf-8") as txt:
        for linha in txt:
            palavra = linha.strip().upper()
            if len(palavra) == 5 and palavra.isalpha():
                palavras.append(palavra)
except FileNotFoundError:
    digitar(
        'Erro: verifique se o arquivo "br-utf8.txt" '
        "está na mesma pasta que o programa."
    )
    raise SystemExit

backup_palavras = palavras.copy()
txt_json = []

placar = {
    "Vitórias": 0,
    "Derrotas": 0,
}

while True:
    if not palavras:
        digitar("Infelizmente as palavras acabaram.")
        reinit = validar_resposta(
            "Deseja reiniciar o jogo? [S/N] ",
            ["S", "N"],
            "Resposta inválida, tente novamente.",
            num_caracteres=1,
        )
        if reinit == "S":
            palavras = backup_palavras.copy()
        else:
            break

    # Escolhe a palavra secreta
    pcerta = choice(palavras)
    certa = unidecode(pcerta).upper()
    palavras.remove(pcerta)

    acertou = False
    tentativas = 0

    while tentativas < 6:
        tentativas += 1
        usu = unidecode(
            validar_resposta(
                f"{tentativas}/6 - ",
                backup_palavras,  # CORRIGIDO: Usa a lista intacta para não rejeitar a palavra sorteada
                "Palavra não identificada, tente novamente.",
                num_caracteres=5,
            )
        ).upper()

        # Resultado visual das letras
        resultado = [""] * 5
        # Controla quais letras da palavra secreta já foram utilizadas
        letras_usadas = [False] * 5

        # Letras corretas nas posições corretas
        for i in range(5):
            if usu[i] == certa[i]:
                resultado[i] = "[green]"
                letras_usadas[i] = True

        # Letras presentes, mas nas posições erradas
        for i in range(5):
            if resultado[i] == "[green]":
                continue
            for j in range(5):
                if not letras_usadas[j] and usu[i] == certa[j]:
                    resultado[i] = "[yellow]"
                    letras_usadas[j] = True
                    break

        # Mostra a palavra colorida
        for i in range(5):
            cor = resultado[i]
            if cor:
                rprint(f"{cor}{usu[i]}[/]", end="")
            else:
                rprint(usu[i], end="")
            if i < 4:
                print(end=" ")
            sleep(TEMPO_PADRAO)
        print()

        if usu == certa:
            acertou = True
            digitar(f"Você acertou a [bold]PALAVRA SECRETA[/]! " f"[bold]{pcerta}[/]")
            break

    if not acertou:
        digitar(
            "Suas tentativas acabaram.\n"
            f"A [bold]PALAVRA SECRETA[/] era [bold]{pcerta}[/]"
        )

    # Salva o histórico da partida
    txt_json.append(
        {
            "palavra": pcerta,
            "tentativas": tentativas,
            "acertou": acertou,
        }
    )

    # Atualiza o placar
    if acertou:
        placar["Vitórias"] += 1
    else:
        placar["Derrotas"] += 1

    mostrar_placar = validar_resposta(
        "Quer ver seu placar? [S/N] ",
        ["S", "N"],
        "Resposta inválida, tente novamente.",
        num_caracteres=1,
    )

    if mostrar_placar == "S":
        for chave, valor in placar.items():
            digitar(f"{chave}: {valor}")
    print()

    continuar = validar_resposta(
        "Quer jogar mais uma vez? [S/N] ",
        ["S", "N"],
        "Resposta inválida, tente novamente.",
        num_caracteres=1,
    )

    if continuar == "N":
        break

# Adiciona o placar ao início do histórico
txt_json.insert(0, placar)

salvar_json = validar_resposta(
    "Quer salvar o histórico do jogo em um arquivo .json? [S/N] ",
    ["S", "N"],
    "Resposta inválida, tente novamente.",
    num_caracteres=1,
)

if salvar_json == "S":
    nome_arquivo = "historico_letrimax.json"
    contador = 1
    while path.exists(nome_arquivo):
        nome_arquivo = f"historico_letrimax_{contador}.json"
        contador += 1

    with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
        dump(
            txt_json,
            arquivo,
            ensure_ascii=False,
            indent=4,
        )
    digitar(f"Histórico salvo em [bold]{nome_arquivo}[/].")

digitar("\nObrigado por ter jogado [bold]LETRIMAX[/]!")
