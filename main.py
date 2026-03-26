# importando as bibliotecas necessárias
from time import sleep
from unidecode import unidecode
from random import choice
from os import path
from json import dump

# criação de utilitários
TP = 0.05 # tempo de digitação padrão

def digit(msg, fim=0, t=None):
    if t is None: t = TP
    for l in msg:
        print(l, end='', flush=True)
        sleep(t)
    if fim == 1: return input()
    if fim == 2: print(end=''); return
    print()


def val_resp(msg, conj_resp, erro_msg, fim=1, t=None, z=1):
    resp = digit(msg, 1, t).strip().replace(' ', '').upper()
    if z != 1: resp = resp[0]
    while resp not in conj_resp:
        digit(erro_msg, fim)
        resp = digit(msg, 1, t).strip().replace(' ', '').upper()
        if z != 1: resp = resp[0]
    return resp


# cores
RESET  = '\033[0m'
BOLD   = '\033[1;38;5;15m'
GREEN  = '\033[1;38;5;108m'
YELLOW = '\033[1;38;5;220m'


# introduzindo o jogador ao jogo
digit(f'Seja bem vindo ao jogo {BOLD}LETRIMAX{RESET}, você terá {BOLD}6{RESET} chances para advinhar a {BOLD}PALAVRA SECRETA{RESET}, que tem {BOLD}5{RESET} letras. ', 1)
digit(f'A cada palavra digitada você verá sua palavra novamente, mas algumas letras estarão pintadas.\n{GREEN}C A{RESET} {BOLD}U {YELLOW}S A{RESET}')
digit(f'No exemplo anterior, o {BOLD}C{RESET} e o {BOLD}A{RESET} estão na palavra e na posição correta, pois estão na cor verde.\nAs letras {BOLD}S{RESET} e {BOLD}A{RESET} estão na posição errada, mas estão na palavra.\nE a letra {BOLD}U{RESET} não está na palavra. ', 1)
digit(f'{GREEN}C A M A S{RESET}\nNesse caso, a palavra foi descoberta.')
digit('Já vou avisando, parece simples, mas não é. ', 1)

# escolha da velocidade de digitação
digit('Mas antes de começar... ', 2)
while True:
    try:
        ent = digit('Digite a velocidade da escrita em segundos (padrão = 0.05): ', 1).replace(' ', '').replace(',', '.')
        if ent != '':
            TP = float(ent)
        if TP < 0:
            TP = 0.05
            digit('Erro! Sua entrada não pode ser menor que 0.')
            raise ValueError
        elif TP >= 1.5:
            TP = 0.05
            digit('Tá de sacanagem, né?! Escolha um valor menor que 1.5.')
            raise ValueError
        
        digit('Texto de exemplo')

        conf = val_resp('Deseja manter nessa velocidade? [S/N] ', ['S', 'N'], 'Resposta inválida, tente novamente. ', t=0.05, z=0)
        if conf == 'N':
            continue
        break
    except Exception:
        digit('Tente novamente. ', 2)

digit('\nAperte enter para começar ', 1)
digit('')

# importando lista de todas as palavras com 5 letras da lingua portuguesa
palavras = []
try:
    with open('br-utf8.txt', encoding='utf-8') as txt:
        for linha in txt:
            palavra = linha.strip().upper()
            if len(palavra) == 5 and palavra.isalpha():
                palavras.append(palavra)
except Exception:
    digit('Erro: verifique se o arquivo "br-utf8.txt" está na mesma pasta que o programa.')
    exit()

backup_palavras = palavras.copy()
txt_json = []

placar = {'Vitórias': 0, 'Derrotas': 0}
while True:
    if len(palavras) == 0:
        digit('Infelizmente as palavras acabaram. ', 2)
        reinit = val_resp('Deseja reiniciar o jogo? [S/N] ', ['S', 'N'], 'Resposta inválida, tente novamente. ', 2, z=0)
        if reinit == 'S': palavras = backup_palavras
        else: break
    
    pcerta = choice(palavras)
    certa = unidecode(pcerta)
    palavras.remove(pcerta)
    m = 1
    while m <= 6:
        usu = unidecode(val_resp(f'{m}/6 - ', palavras, f'Palavra não identificada, tente novamente. ', 2))
        resultado = [RESET] * 5
        letras_usadas = [False] * 5
        m += 1

        # letras corretas em posições corretas
        for i in range(5):
            if usu[i] == certa[i]:
                resultado[i] = GREEN
                letras_usadas[i] = True
        
        # estão na palavra, mas em posições diferentes
        for i in range(5):
            if resultado[i] == GREEN: 
                continue
            for j in range(5):
                if not letras_usadas[j] and usu[i] == certa[j]:
                    resultado[i] = YELLOW
                    letras_usadas[j] = True
                    break
        
        # mostra a palavra corrogida
        for i in range(5):
            if i < 4:
                print(resultado[i] + usu[i], end=' ')
            else:
                print(resultado[i] + usu[i], end=f'{RESET}\n', flush=True)
            sleep(TP)
        
        if usu == certa:
            acertou = True
            digit(f'Você acertou a {BOLD}PALAVRA SECRETA{RESET}! {BOLD}{pcerta}{RESET}', 1)
            break
    else:
        acertou = False
        digit(f'Suas tentativas acabaram.\nA {BOLD}PALAVRA SECRETA{RESET} era {BOLD}{pcerta}{RESET} ', 1)
    
    txt_json.append({'palavra': pcerta, 'tentativas': m, 'acertou': acertou})

    if acertou: placar['Vitórias'] += 1
    else: placar['Derrotas'] += 1
    mostrar_placar = val_resp('Quer ver seu placar? [S/N] ', ['S', 'N'], 'Resposta inválida, tente novamente. ', 2, z=0)
    if mostrar_placar == 'S':
        for key, value in placar.items():
            digit(f'{key}: {value}')
    print()

    continuar = val_resp('Quer jogar mais uma vez? [S/N] ', ['S', 'N'], 'Resposta inválida, tente novamente. ', 2, z=0)
    if continuar == 'N': 
        break

txt_json.insert(0, placar)
json = val_resp('Quer salvar o histórico do jogo em um arquivo .json? [S/N] ', ['S', 'N'], 'Resposta inválida, tente novamente. ', 2, z=0)
if json == 'S':
    if path.exists('historico_letrimax.json'):
        contador = 1
        while True:
            if not path.exists(f'historico_letrimax_{contador}.json'):
                nome_arquivo = f'historico_letrimax_{contador}.json'
                break
            contador += 1
        
        with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
            dump(txt_json, arquivo)

digit(f'\nObrigado por ter jogado {BOLD}LETRIMAX{RESET}!')