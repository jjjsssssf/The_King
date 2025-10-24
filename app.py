from jogo import mini_mapa, carregar_mapa_estado, limpar_todos_os_saves, limpar_todos_os_saves_p, carregar_jogo_global
from classe_arts import draw_window, term, clear, mini_mapa_
import random, time, string
from classe_do_jogador import jogador
from classe_do_inimigo import inimigo
from classe_arts import art_ascii, Cores
from mm import tocar_musica, escolher_e_tocar_musica, parar_musica, tocando_musica
from classe_do_inventario import TODOS_OS_ITENS
##arquivo do jogo
ascii = art_ascii()
mapas = mini_mapa_()
C = Cores()
jj = jogador(nome="", hp_max=100, atk=15, niv=1, xp_max=100, defesa=10, gold=0, stm_max=100, intt=10, mn_max=100,d_m=20, art_player=ascii.necro, skin="0",skin_nome='')
ee = inimigo(nome="", hp_max=0, atk=0, niv=0, xp=0, defesa=0, gold=0, art_ascii="",atk1="",atk2="")
thread_musica = None

def menu_inicial(x_l, y_l):
    NOME_DO_ARQUIVO = "Title_.mp3"
    escolher_e_tocar_musica(NOME_DO_ARQUIVO)
    while True:
        clear()
        menu_art = ascii.titulo
        opcoes = "[1] Jogar\n[2] Carregar\n[3] Sair"
        herd = menu_art.count("\n")
        draw_window(term, x=x_l, y=y_l, width=90, height=24, text_content=menu_art)
        draw_window(term, x=x_l+25, y=y_l+herd+1, width=25, height=6, text_content=opcoes)
        with term.location(x=x_l+27, y=y_l+herd+5):
            escolha = input(">")
        if escolha == "1":
            limpar_todos_os_saves()
            limpar_todos_os_saves_p()
            dificuldade_key = escolher_dificudade(x_l, y_l, menu_art)
            nome = solicitar_nome(x_l, y_l, menu_art)
            skin_arte, cor_final, skin_nome = escolher_personagem(x_l, y_l) 
            jj = jogador(
                nome=nome,
                hp_max=50,
                atk=5,
                niv=1,
                xp_max=100,
                defesa=0,
                gold=0,
                stm_max=100,
                intt=0,
                mn_max=50,
                d_m=10,
                art_player=skin_arte, 
                skin=cor_final,     
                skin_nome=skin_nome 
            )
            jj.dificuldade_atual = dificuldade_key
            if jj.dificuldade_atual == 'Facil':
                jj.ponto += 15
            elif jj.dificuldade_atual == 'Normal':
                jj.ponto += 10
            elif jj.dificuldade_atual == 'Dificil':
                jj.ponto += 5
            clear()
            jj.up(x=x_l, y=y_l, werd=35, herd=15, x_i=-34)
            obs = {'#', 'H', '♣', '/', 'K', '~', '&'}
            cor = {'#':term.gray, 'H':term.gray, '♣': term.green, '/':term.bold_brown, 'K':term.yellow, '~':term.blue, '"': term.green, '\\': term.brown, '&': term.bold_blue
            }
            
            mini_mapa(
                x_l=0,
                y_l=0,
                player=jj,
                ascii=ascii,
                mapas_=mapas.castelo.split('\n'),
                camera_w=35,
                camera_h=15,
                x_p=3,
                y_p=2,
                menager="",
                mapa_nome='Pantano de Argos',
                obstaculos_custom=obs,
                cores_custom=cor)

        elif escolha == "2":
            # Carrega o jogo global (player + mapas)
            player_carregado, mapas_carregados = carregar_jogo_global(filename="save_global.json")
            if player_carregado:
                jj = player_carregado
                ESTADO_MAPAS = mapas_carregados

                mapa_nome_load = jj.mapa_atual
                mapa_art_para_load = {
                    "Castelo de Argos 2": mapas.castelo_1.split('\n'),
                    "Castelo de Argos": mapas.castelo.split('\n'),
                    "Pantano de Argos": mapas.inicil.split('\n')
                }.get(mapa_nome_load, mapas.castelo.split('\n'))

                x_p_load = jj.x_mapa
                y_p_load = jj.y_mapa
                mini_mapa(
                    x_l=0,
                    y_l=0,
                    player=jj,
                    ascii=ascii,
                    mapas_=mapa_art_para_load,
                    camera_w=35,
                    camera_h=15,
                    x_p=x_p_load,
                    y_p=y_p_load,
                    menager="",
                    mapa_nome=mapa_nome_load,
                    obstaculos_custom=None,
                    cores_custom=None,
                    ESTADO_GLOBAL_LOAD=mapas_carregados

                )
            else:
                with term.location(x_l+27, y=y_l+herd+6):
                    print(term.red("Nenhum save encontrado!"))
                    input("Pressione ENTER para continuar...")

        elif escolha == "3":
            exit()

def solicitar_nome(x_l, y_l, menu_art):
    while True:
        clear()
        prompt = "Qual será seu Nome:\n(max 8 caracteres)"
        num_linhas = prompt.count("\n") + 4
        draw_window(term, x=x_l, y=y_l, width=90, height=24, text_content=menu_art)
        draw_window(term, x=x_l+25, y=y_l+num_linhas+3, width=27, height=num_linhas, text_content=prompt)

        with term.location(x=x_l+26, y=y_l+num_linhas+6):
            nome = input(">")

        if len(nome) > 8:
            mostrar_mensagem(x_l+26, y_l+num_linhas+6, "Nome muito extenso")
        elif len(nome) < 1:
            mostrar_mensagem(x_l+26, y_l+num_linhas+6, "Digite pelo menos 1 letra")
        else:
            return nome
        
def escolher_personagem(x_l, y_l):
    personagens = {
        "1": {"nome": "necro", "arte": ascii.necro},
        "2": {"nome": "guerreiro", "arte": ascii.guerriro},
        "3": {"nome": "mago", "arte": ascii.mago}
    }
    while True:
        clear()
        draw_window(term, x=x_l, y=y_l, width=90, height=24)
        draw_window(term, x=x_l+2, y=y_l+1, width=25, height=11, title="1", text_content=ascii.necro)
        draw_window(term, x=x_l+32, y=y_l+1, width=25, height=11, title="2", text_content=ascii.guerriro)
        draw_window(term, x=x_l+64, y=y_l+1, width=25, height=11, title="3", text_content=ascii.mago)

        with term.location(x=x_l+2, y=y_l+12):
            escolha = input("Escolha uma Skin: ")

        if escolha in personagens:
            skin_data = personagens[escolha]
            skin_arte = skin_data["arte"]
            skin_nome = skin_data["nome"]
            
            caractere = solicitar_caractere(x_l, y_l)
            cor_final = escolher_cor(caractere, x_l, y_l)
            
            return skin_arte, cor_final, skin_nome

def solicitar_caractere(x_l, y_l):
    while True:
        with term.location(x=x_l+2, y=y_l+13):
            print("Escolha um caractere do seu personagem: ")
        with term.location(x=x_l+2, y=y_l+14):
            caractere = input(">")
        if len(caractere) == 1:
            return caractere
        else:
            with term.location(x=x_l+2, y=y_l+15):
                print("Use apenas UM caractere")

def escolher_cor(caractere, x_l, y_l):
    cores = {
        "1": C.AZUL,
        "2": C.AMARELO,
        "3": C.VERDE,
        "4": C.VERMELHO
    }
    while True:
        with term.location(x=x_l+2, y=y_l+15):
            print("Escolha um Cor: ")
        with term.location(x=x_l+2, y=y_l+16):
            print(f"{C.AZUL}[1]Azul {C.AMARELO}[2]Amarelo {C.VERDE}[3]Verde {C.VERMELHO}[4]Vermelho")
        with term.location(x=x_l+2, y=y_l+17):
            escolha = input(">")
        if escolha in cores:
            return f"{cores[escolha]}{caractere}{C.RESET}"

def mostrar_mensagem(x, y, mensagem):
    with term.location(x, y):
        print(mensagem)

def escolher_dificudade(x_l, y_l, menu_art):
    while True:
        clear()
        prompt = "Escolha a Dificuldade\n[1] Fácil (x0.5)\n[2] Normal (x1.0)\n[3] Difícil (x2.0)"
        num_linhas = prompt.count("\n") + 4        
        draw_window(term, x=x_l, y=y_l, width=90, height=24, text_content=menu_art)
        draw_window(term, x=x_l+25, y=y_l+num_linhas+1, width=27, height=num_linhas, text_content=prompt)

        with term.location(x=x_l+26, y=y_l+num_linhas+6):
            dif = input(">")
            
        if dif == '1':
            return 'Facil'
        elif dif == '2':
            return 'Normal'
        elif dif == '3':
            return 'Dificil'
        else:
            mostrar_mensagem(x_l+26, y_l+num_linhas+6, "Opção inválida. Use 1, 2 ou 3.")


menu_inicial(x_l=0, y_l=0)