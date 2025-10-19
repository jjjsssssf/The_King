import random, os, time, json
from classe_arts import draw_window, linha_inven, linhas, linhas_batalha, clear, art_ascii, clear_region_a
from classe_do_inventario import Item, TODOS_OS_ITENS, magias, TODAS_AS_MAGIAS
from collections import defaultdict
from blessed import Terminal
term = Terminal()
art= art_ascii()
##ARQUIVO DO JOGADOR
class jogador:
    def __init__(self, nome, hp_max, atk, niv, xp_max, defesa, gold, stm_max, intt, mn_max, d_m, art_player, skin, skin_nome, mana_lit=None):
        self.nome = nome
        self.skin = skin
        self.skin_nome = skin_nome
        self.hp_max = hp_max
        self.hp = self.hp_max
        self.mapa_atual = "castelo_1"
        self.mana_max = mn_max
        self.mana = self.mana_max
        self.stm_max = stm_max
        self.stm = self.stm_max
        self.atk = atk
        self.buff_atk = 0
        self.buff_def = 0
        self.intt = intt
        self.niv = niv
        self.ponto = 0
        self.xp_max = xp_max
        self.dano_magico = d_m
        self.xp = 0
        self.defesa = defesa
        self.gold = gold
        self.rodar_jogo = False
        self.aleatorio = 75
        self.art_player = art_player
        self.x_mapa = 0
        self.y_mapa = 0
        self.boss = {'Suny': False}
        self.inventario = []
        self.mana_lit = mana_lit if mana_lit else []
        self.equipa = {
            "m_pri": None,
            "m_seg": None,
            "c_cap": None,
            "p_pet": None,
            "s_crad": None,
        }
        self.itens_coletaodos = {
            "item_1": True,
            "item_2": False,
            "Farol": False,
            "Dentro_Farol": False,
        }
        self.classe = None 

    def save_game(self, filename="demo.json"):
        inventario_nomes = [item.nome for item in self.inventario]
        equipa_nomes = {slot: item.nome if item else None for slot, item in self.equipa.items()}
        player_data = {
            "nome": self.nome,
            "hp_max": self.hp_max,
            "hp": self.hp,
            "atk": self.atk,
            "niv": self.niv,
            "xp_max": self.xp_max,
            "defesa": self.defesa,
            "gold": self.gold,
            "stm_max": self.stm_max,
            "stm": self.stm,
            "intt": self.intt,
            "mn_max": self.mana_max,
            "mana": self.mana,
            "d_m": self.dano_magico,
            "xp": self.xp,
            "aleatorio": self.aleatorio,
            "inventario": inventario_nomes,
            "mana_lit": self.mana_lit,
            "equipa": equipa_nomes,
            "itens_coletaodos": self.itens_coletaodos,
            "rodar": self.rodar_jogo,
            "classes": self.classe,
            "pos_x": self.x_mapa,
            "pos_y": self.y_mapa,
            "mapa_atual": self.mapa_atual,
            "char_skin": self.skin,  # Caractere colorido
            "art_player_nome": self.skin_nome, # Nome da arte ASCII
        }
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(player_data, f, indent=4)
            print(f"Jogo salvo com sucesso em '{filename}'")
        except IOError as e:
            print(f"Erro ao salvar o jogo: {e}")

    @classmethod
    def load_game(cls, filename="demo.json"):
        if not os.path.exists(filename):
            print(f"Nenhum arquivo de salvamento encontrado em '{filename}'.")
            return None
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                player_data = json.load(f)
            SKIN_MAP = {
                "necro": art.necro,
                "guerreiro": art.guerriro,
                "mago": art.mago
            }
            skin_nome_carregado = player_data.get("art_player_nome")
            skin_arte_carregada = SKIN_MAP.get(skin_nome_carregado) or None

            player = cls(
                nome=player_data["nome"],
                hp_max=player_data["hp_max"],
                atk=player_data["atk"],
                niv=player_data["niv"],
                xp_max=player_data["xp_max"],
                defesa=player_data["defesa"],
                gold=player_data["gold"],
                stm_max=player_data["stm_max"],
                intt=player_data["intt"],
                mn_max=player_data["mn_max"],
                d_m=player_data["d_m"],
                art_player=skin_arte_carregada,
                skin=player_data.get("char_skin", "@"),
                skin_nome=skin_nome_carregado,
            )

            player.inventario = [TODOS_OS_ITENS[nome] for nome in player_data.get("inventario", []) if nome in TODOS_OS_ITENS]
            player.equipa = {slot: TODOS_OS_ITENS[nome] if nome and nome in TODOS_OS_ITENS else None for slot, nome in player_data.get("equipa", {}).items()}

            player.hp = player_data["hp"]
            player.aleatorio = player_data["aleatorio"]
            player.mana_lit = player_data.get("mana_lit", [])
            player.itens_coletaodos = player_data.get("itens_coletaodos", {})
            player.xp = player_data["xp"]
            player.mana = player_data["mana"]
            player.stm = player_data["stm"]
            player.rodar_jogo = player_data["rodar"]
            player.classe = player_data["classes"]
            player.x_mapa = player_data.get("pos_x", 0)
            player.y_mapa = player_data.get("pos_y", 0)
            player.mapa_atual = player_data.get("mapa_atual", "castelo_1")

            print(f"Jogo carregado com sucesso de '{filename}'!")
            return player
        except (IOError, json.JSONDecodeError, KeyError) as e:
            print(f"Erro ao carregar o jogo: {e}.")
            return None    

    def barra_de_vida(self, x_l, y_l, largura=25):
        proporcao_hp = max(0, min(self.hp / self.hp_max, 1))
        preenchido_hp = int(proporcao_hp * largura)
        vazio_hp = largura - preenchido_hp
        barra_hp = (
            term.bold_green("=") * preenchido_hp +
            term.green("=") * vazio_hp +
            term.normal
        )
        porcentagem_hp = int(proporcao_hp * 100)
        proporcao_stm = max(0, min(self.stm / self.stm_max, 1))
        preenchido_stm = int(proporcao_stm * largura) 
        vazio_stm = largura - preenchido_stm
        barra_stm = (
            term.bold_yellow("=") * preenchido_stm +
            term.yellow("=") * vazio_stm +
            term.normal
        )
        porcentagem_stm = int(proporcao_stm * 100)
        proporcao_m = max(0, min(self.mana / self.mana_max, 1))
        preenchido_m = int(proporcao_m * largura) 
        vazio_m = largura - preenchido_m
        barra_m = (
            term.bold_magenta("=") * preenchido_m +
            term.magenta("=") * vazio_m +
            term.normal
        )
        porcentagem_m = int(proporcao_m * 100)
        with term.location(x=x_l, y=y_l):
            print(f"HP[{barra_hp}] {porcentagem_hp}%")
        with term.location(x=x_l, y=y_l+1):
            print(f"ST[{barra_stm}] {porcentagem_stm}%")
        with term.location(x=x_l, y=y_l+2):
            print(f"MG[{barra_m}] {porcentagem_m}%")
        with term.location(x=x_l, y=y_l+3):
            print(f"ATK: [{term.bold_red(str(self.atk))}] - DEF: [{term.bold_blue(str(self.defesa))}]")
        with term.location(x=x_l, y=y_l+4):
            print(f"MGA: [{term.bold_magenta(str(self.dano_magico))}] - INT: [{term.bold_gray(str(self.intt))}]")
        with term.location(x=x_l, y=y_l+5):
            print(f"Gold: [{term.bold_yellow(str(self.gold))}] - Nivel: [{term.bold_green(str(self.niv))}]")
        with term.location(x=x_l, y=y_l+6):
            print(f"X: [{term.bold_blue(str(self.x_mapa))}] - Y: [{term.bold_red(str(self.y_mapa))}]")

    def status_art(self ,x_janela, y_janela):
        art_player = self.art_player
        draw_window(term, x=x_janela, y=y_janela, width=31, height=11, text_content=art_player)

    def status_batalha_art(self, x_janela, y_janela, wend, herd):
        art_player = self.art_player
        draw_window(term, x=x_janela, y=y_janela, width=wend, height=herd, text_content=art_player)
        self.status_batalha(x_janela=x_janela, y_janela=y_janela+herd)

    def status_batalha(self, x_janela, y_janela):
        draw_window(term, x=x_janela, y=y_janela, width=31, height=6)
        with term.location(x=x_janela+1, y=y_janela+1):
            print(f"HP: [{term.bold_green(str(self.hp_max))}/{term.green(str(self.hp))}] MP: [{term.bold_blue(str(self.stm_max))}/{term.blue(str(self.stm))}]")
        with term.location(x=x_janela+1, y=y_janela+2):
            print(f"MG: [{term.bold_magenta(str(self.mana_max))}/{term.magenta(str(self.mana))}] MA: [{term.bold_purple(str(self.dano_magico+3))}-{term.purple(str(self.dano_magico-3))}]")
        with term.location(x=x_janela+1, y=y_janela+3):
            print(f"AT: [{term.bold_red(str(self.atk))}-{term.red(str(self.buff_atk))}] DF: [{term.bold_cyan(str(self.defesa))}-{term.cyan(str(self.buff_def))}]")
        with term.location(x=x_janela+1, y=y_janela+4):
            print(f"Nivel: [{term.yellow(str(self.niv))}]")

    def add_xp(self, xp_ganho):
        self.xp += xp_ganho
        while self.xp >= self.xp_max:
            print(term.bold_white("Você subiu de nível!"))
            xp_remaining = self.xp - self.xp_max
            self.xp_max = int(self.xp_max * 1.2)
            self.xp = xp_remaining
            self.niv += 1
            self.ponto += 5
            self.stm = self.stm_max
            time.sleep(1)
        print(f"Você ganhou {xp_ganho} de XP. Total: {self.xp}/{self.xp_max}")
        time.sleep(2)

    def up(self, x, y, werd, herd):
        STATUS_MAP = {
            "HP": ("hp_max", "HP"),
            "MP": ("stm_max", "MP"),
            "ATK": ("atk", "ATK"),
            "DEF": ("defesa", "DEF"),
            "MG": ("mana_max", "Poder Mágico (MG)"),
            "MA": ("dano_magico", "Dano Mágico (MA)"),
            "INT": ("intt", "INT"),
            "SAIR": ("sair", "Sair do menu")
        }

        while True:
            clear_region_a(x=x, start_y=herd, end_y=herd-1, width=werd)

            mensagem = f"""Pontos: [{self.ponto}]
HP: [{self.hp_max}]
MP: [{self.stm_max}]
ATK: [{self.atk}]
DEF: [{self.defesa}]
MG: [{self.mana_max}]
MA: [{self.dano_magico}]
INT: [{self.intt}]
Digite o Nome do Status e Quantidade (ex: HP 5) ou SAIR:"""

            draw_window(term, x=x, y=y, width=werd, height=herd, text_content=mensagem)

            if self.ponto >= 1:
                with term.location(x=werd+1, y=herd-6):
                    up_input = input(">").strip().upper()
            else:
                with term.location(x=werd+1, y=herd-5):
                    print("Você não tem Pontos para melhorar.")
                    input()
                    break

            if up_input == "SAIR":
                break

            parts = up_input.split()
            if len(parts) == 2:
                stat_name, amount_str = parts
                if stat_name in STATUS_MAP and amount_str.isdigit():
                    amount = int(amount_str)
                    if amount <= 0:
                        msg = "Digite um número maior que zero."
                    elif amount > self.ponto:
                        msg = f"Você só tem {self.ponto} ponto(s)."
                    else:
                        attr_name, display_name = STATUS_MAP[stat_name]
                        current_value = getattr(self, attr_name)
                        setattr(self, attr_name, current_value + (amount * 3))
                        self.ponto -= amount
                        msg = f"Você melhorou seu {display_name}"
                else:
                    msg = "Comando inválido.Tente algo como: HP 5"
            else:
                msg = "Formato inválido.Use: STATUS QUANTIDADE"

            with term.location(x=werd+1, y=herd-5):
                print(" " * 50)
            with term.location(x=werd+1, y=herd-5):
                print(msg)
            time.sleep(2)

    def aprender_magias(self, term, x_menu, y_menu, wend, herd):
        term = Terminal()
        tipos_magias = sorted(set(magia.tipo for magia in TODAS_AS_MAGIAS.values()))
        
        while True:
            clear_region_a(x=x_menu, start_y=y_menu, end_y=y_menu + 10, width=wend)
            menu_text = "Escolha o tipo de magia para aprender:\n"
            for i, tipo in enumerate(tipos_magias, start=1):
                menu_text += f"[{i}] {tipo}\n"
            menu_text += "[0] Voltar"
            draw_window(term, x_menu, y_menu, wend, herd+2, text_content=menu_text)

            with term.location(x=x_menu+1, y=y_menu+herd):
                escolha = input(">").strip()

            if escolha == '0':
                break

            if escolha.isdigit() and 1 <= int(escolha) <= len(tipos_magias):
                tipo_escolhido = tipos_magias[int(escolha) - 1]
                magias_disponiveis = [
                    m for m in TODAS_AS_MAGIAS.values()
                    if m.tipo == tipo_escolhido and m.nome not in self.mana_lit
                ]

                if not magias_disponiveis:
                    draw_window(term, x_menu, y_menu, wend, herd+2, text_content="Nenhuma magia disponível.")
                    time.sleep(2)
                    continue

                while True:
                    clear_region_a(x_menu, y_menu, y_menu + 10, wend)
                    conteudo = f"Magias de tipo: {tipo_escolhido}\n"
                    for i, magia in enumerate(magias_disponiveis, 1):
                        conteudo += f"[{i}] {magia.nome} - Requer {magia.xp} Pontos\n"
                    conteudo += "[0] Voltar"
                    draw_window(term, x_menu, y_menu, wend, herd+2, text_content=conteudo)

                    with term.location(x=x_menu+1, y=y_menu+herd):
                        escolha_magia = input(">").strip()

                    if escolha_magia == '0':
                        break

                    if escolha_magia.isdigit() and 1 <= int(escolha_magia) <= len(magias_disponiveis):
                        magia = magias_disponiveis[int(escolha_magia) - 1]

                        if magia.nome in self.mana_lit:
                            draw_window(term, x_menu, y_menu, wend, herd+2, text_content="Você já aprendeu essa magia.")
                            with term.location(x=x_menu+1, y=y_menu+herd):
                                input("Pressione Enter para continuar...")
                            continue
                        if self.ponto >= magia.xp:
                            self.ponto -= magia.xp
                            self.mana_lit.append(magia.nome)
                            draw_window(term, x_menu, y_menu, wend, herd+2, text_content=f"Você aprendeu: {magia.nome}")
                        else:
                            draw_window(term, x_menu, y_menu, wend, herd+2, text_content="XP insuficiente.")
                            with term.location(x=x_menu+1, y=y_menu+herd):
                                input("Pressione Enter para continuar...")
                        break

    def menu_magias(self, x_menu, y_menu, batalha, alvo):
        term = Terminal()
        text_content = ""

        if not self.mana_lit:
            text_content = "Você não conhece nenhuma magia."
        else:
            for nome_magia in self.mana_lit:
                magia_obj = TODAS_AS_MAGIAS.get(nome_magia)
                if magia_obj:
                    text_content += f"{magia_obj.nome} (Custo: {magia_obj.mana_gasta} Mana)\n"
        
        text_content += "Para usar uma magia, digite o nome dela.\nPara sair, digite 'sair'."
        num_linhas_texto = text_content.count('\n') + 1
        herd = num_linhas_texto + 3
        draw_window(term, x_menu, y_menu, width=45, height=herd, title="Livro de Magias", text_content=text_content)
        
        x_input = x_menu + 2
        y_input = y_menu + herd - 2

        with term.location(x_input, y_input):
            escolha = input(">")

        if escolha.lower() == "sair":
            return False
            
        if escolha in self.mana_lit:
            magia_escolhida = TODAS_AS_MAGIAS[escolha]
            if magia_escolhida.batalhas and not batalha:
                feedback_message = "Você só pode usar esta magia em batalha!"
                draw_window(term, x=x_menu, y=y_menu + herd, width=len(feedback_message) + 5, height=5, text_content=feedback_message)
                time.sleep(2)
                return False
            else:
                return self.usar_magia(magia_escolhida, x_menu, y_menu + herd, alvo=alvo)
        else:
            feedback_message = "Magia inválida ou não conhecida."
            draw_window(term, x=x_menu, y=y_menu + herd, width=len(feedback_message) + 5, height=5, text_content=feedback_message)
            time.sleep(2)
            return False

    def usar_magia(self, magia, x_janela, y_janela, alvo):
        text_content = ""
        herd = 3
        sucesso = False       
        if self.mana < magia.mana_gasta:
            text_content = "Mana insuficiente!"
            sucesso = False
        else:
            self.mana -= magia.mana_gasta            
            if magia.tipo == "Cura":
                self.hp += magia.bonus_hp
                if self.hp > self.hp_max:
                    self.hp = self.hp_max
                text_content = f"Você usou {magia.nome} e curou {magia.bonus_hp} de HP."
                sucesso = True
            elif magia.tipo == "Ataque":
                div = self.intt // 4
                soma = self.dano_magico + div
                dano = soma + magia.bonus_atk
                alvo.hp -= dano
                text_content = f"Você lançou {magia.nome} e causou {dano} de dano."
                sucesso = True
            elif magia.tipo == "Ajudante":
                self.buff_def += magia.bonus_def
                self.buff_atk += magia.bonus_atk
                text_content =f"""Você chamou {magia.nome}
ele ira te ajudar na batalhas
ATK: [{magia.bonus_atk}]
DEF: [{magia.bonus_def}]"""
                herd = 6
                sucesso = True
        draw_window(term, x_janela, y_janela, width=35, height=herd, text_content=text_content)
        time.sleep(2)
        return sucesso

    def atake(self, alvo, x_janela, y_janela):
        atak_aleatorio = random.randint(1, 100)
        if self.stm >= 10:
            if self.aleatorio > atak_aleatorio:
                self.stm -= 10
                dano_ale = random.randint(int(self.atk - 3), int(self.atk + 3))
                meno_defsa = alvo.defesa // 4
                dano_final = int(self.buff_atk + dano_ale - meno_defsa)
                if dano_final <= 0:
                    dano_final = 1
                mensagem = f"{str(self.nome)} deu um dano de {str(dano_final)}\nno {str(alvo.nome)}"
                alvo.hp -= dano_final
                time.sleep(1)
            else:
                mensagem = f"{self.nome} errou o ataque"
                time.sleep(1)
        else:
            mensagem = "Você não tem ST suficiente"
            time.sleep(1)
        herd = 4
        draw_window(term, x_janela, y_janela, width=len(mensagem)-5, height=herd, text_content=mensagem)
    
    def inventario_(self, x, y, werd, herd, batalha):
        text_content = ""
        contagem_itens = defaultdict(int)
        lista_itens = []

        for item_obj in self.inventario:
            contagem_itens[item_obj.nome] += 1

        if not self.inventario:
            text_content = "Não tem nada no inventário.\n"
        else:
            index = 1
            for item_nome, quantidade in contagem_itens.items():
                item_obj = TODOS_OS_ITENS[item_nome]
                estado = ""
                if item_obj.slot_equip and self.equipa.get(item_obj.slot_equip) and self.equipa[item_obj.slot_equip].nome == item_obj.nome:
                    estado = "[Equipado]"
                text_content += f"[{index}] {item_obj.nome} (x{quantidade}) {estado}\n"
                lista_itens.append(item_obj)
                index += 1

        text_content += "Escolha um número para usar o item\nDigite 'sair' para sair"
        num_linhas_texto = text_content.count('\n') + 1
        altura_janela = num_linhas_texto + 4

        while True:
            clear_region_a(x=x, start_y=altura_janela, end_y=altura_janela - 1, width=werd)
            draw_window(term, x, y, width=werd, height=altura_janela, title="Inventário", text_content=text_content)
            x_input = x + 2
            y_input = y + altura_janela - 3
            with term.location(x_input, y_input):
                escolha = input(">")

            if escolha.lower() == "sair":
                return False

            if escolha.isdigit():
                escolha_index = int(escolha) - 1
                if 0 <= escolha_index < len(lista_itens):
                    item_escolhido = lista_itens[escolha_index]
                    if batalha:
                        if item_escolhido.tipo == "Consumivel":
                            return self.usar_consumivel(item_escolhido, x, y + altura_janela + 1, werd)
                        elif item_escolhido.tipo == "Equipavel":
                            mensagem = "Você não pode usar\num equipamento em batalha!"
                            draw_window(term, x=x, y=y + altura_janela, width=werd, height=4, text_content=mensagem)
                            time.sleep(3)
                    else:
                        if item_escolhido.tipo == "Consumivel":
                            self.usar_consumivel(item_escolhido, x, y + altura_janela, werd)
                        elif item_escolhido.tipo == "Equipavel":
                            self.gerenciar_equipavel(item_escolhido, x, y + altura_janela, werd)
                else:
                    mensagem = "Número inválido."
                    draw_window(term, x=x, y=y + altura_janela, width=werd, height=3, text_content=mensagem)
                    time.sleep(2)
            else:
                mensagem = "Entrada inválida."
                draw_window(term, x=x, y=y + altura_janela, width=werd, height=3, text_content=mensagem)
                time.sleep(2)

    def usar_consumivel(self, item, x_janela, y_janela, werd):
        altura_mensagem = 3
        clear_region_a(x=x_janela, start_y=y_janela, end_y=y_janela + altura_mensagem, width=werd)
        if item.nome == "Poção de Cura":
            if self.hp >= self.hp_max:
                mensagem = "Seu HP já está no máximo!"
                sucesso = False
            else:
                mensagem = "Você bebeu uma poção de cura."
                self.hp = min(self.hp + item.bonus_hp, self.hp_max)
                self.inventario.remove(item)
                sucesso = True
        elif item.nome == "Elixir":
            if self.mana >= self.mana_max:
                mensagem = "Sua Mana já está no máximo!"
                sucesso = False
            else:
                mensagem = "Você bebeu um elixir."
                self.mana = min(self.mana + item.bonus_mana, self.mana_max)
                self.inventario.remove(item)
                sucesso = True
        elif item.nome == "Suco":
            if self.stm >= self.stm_max:
                mensagem = "Sua Stamina já está no máximo!"
                sucesso = False
            else:
                mensagem = "Você bebeu um suco."
                self.stm = min(self.stm + item.bonus_stm, self.stm_max)
                self.inventario.remove(item)
                sucesso = True

        draw_window(term, x_janela, y_janela, width=werd, height=altura_mensagem, text_content=mensagem)
        time.sleep(2)
        clear_region_a(x_janela, y_janela, y_janela + altura_mensagem, werd)
        return sucesso

    def gerenciar_equipavel(self, item, x_janela, y_janela, werd):
        altura_opcoes = 6
        altura_feedback = 4
        clear_region_a(x_janela, y_janela, y_janela + altura_opcoes + altura_feedback, werd)
        text_content = "O que deseja fazer com o item?\n[1]Equipar\n[2]Desequipar"
        draw_window(term, x_janela, y_janela, width=werd, height=altura_opcoes, title=item.nome, text_content=text_content)
        with term.location(x_janela + 2, y_janela + altura_opcoes - 2):
            esc = input(">")
        if esc == "1":
            if not self.equipa.get(item.slot_equip):
                self.equipa[item.slot_equip] = item
                self.atk += item.bonus_atk
                self.defesa += item.bonus_def
                self.dano_magico += item.bonus_atk_mana
                feedback = f"Você equipou {item.nome}."
            else:
                feedback = "Já tem algo equipado nesse slot!"
        elif esc == "2":
            if self.equipa.get(item.slot_equip) and self.equipa[item.slot_equip].nome == item.nome:
                self.equipa[item.slot_equip] = None
                self.atk -= item.bonus_atk
                self.defesa -= item.bonus_def
                self.dano_magico -= item.bonus_atk_mana
                feedback = f"Você desequipou {item.nome}."
            else:
                feedback = "Este item não está equipado."
        else:
            feedback = "Opção inválida."

        draw_window(term, x_janela, y_janela + altura_opcoes, width=werd, height=altura_feedback, text_content=feedback)
        time.sleep(2)
        clear_region_a(x_janela, y_janela, y_janela + altura_opcoes + altura_feedback, werd)

    def gerenciar_loja(self, x, y, largura):
        while True:
            clear()
            text_content = f"Gold: [{term.bold_yellow(str(self.gold))}]\n"
            text_content += "[1] Comprar Itens\n"
            text_content += "[2] Vender Itens\n"
            text_content += "[3] Sair da Loja"
            
            draw_window(term, x, y, width=largura, height=7, title="Loja", text_content=text_content)
            
            with term.location(x + 2, y + 5):
                escolha = input("> ")
            
            if escolha == "1":
                self.comprar_itens(x+largura, y, largura)
            elif escolha == "2":
                self.vender_itens(x+largura, y, largura)
            elif escolha == "3":
                return
            else:
                print("Opção inválida.", x, y + 8, largura)

    def comprar_itens(self, x, y, largura):
        while True:
            text_content = f"Gold: [{term.bold_yellow(str(self.gold))}]\n"
            text_content += "[1] Itens Equipáveis\n"
            text_content += "[2] Itens Consumíveis\n"
            text_content += "[3] Voltar"
            
            draw_window(term, x, y, width=largura, height=7, title="Comprar", text_content=text_content)

            with term.location(x + 2, y + 5):
                escolha = input("> ")
            
            if escolha == "1":
                self.exibir_itens_por_tipo("Equipavel", x-largura, y + 7, largura)
            elif escolha == "2":
                self.exibir_itens_por_tipo("Consumivel", x-largura, y + 7, largura)
            elif escolha == "3":
                return
            else:
                pass

    def exibir_itens_por_tipo(self, tipo, x, y, largura):
        while True:
            itens = [i for i in TODOS_OS_ITENS.values() if i.tipo == tipo and i.comprável]
            text_content = f"Gold: [{term.bold_yellow(str(self.gold))}]\n"

            if not itens:
                text_content += f"Nenhum item do tipo '{tipo}' disponível.\n[0] Voltar"
            else:
                for idx, item in enumerate(itens, 1):
                    text_content += f"[{idx}] {item.nome} - [{item.preco}]\n"
                text_content += "[0] Voltar"

            altura = text_content.count("\n") + 4
            draw_window(term, x, y, width=largura, height=altura, title=f"Comprar {tipo}", text_content=text_content)

            with term.location(x + 2, y + altura - 2):
                try:
                    escolha = int(input(">"))
                    if escolha == 0:
                        return
                    item_escolhido = itens[escolha - 1]
                    if self.gold >= item_escolhido.preco:
                        self.gold -= item_escolhido.preco
                        self.inventario.append(item_escolhido)
                        with term.location(x=x+largura, y=y + 1):
                            print(f"Você comprou {item_escolhido.nome}.",)
                    else:
                        with term.location(x+largura, y+1):
                            print("Dinheiro insuficiente.")
                except (ValueError, IndexError):
                    pass
    
    def vender_itens(self, x, y, largura):
        while True:
            itens_vendaveis = [item for item in self.inventario if item.vendivel]
            contagem = defaultdict(int)
            for item in itens_vendaveis:
                contagem[item.nome] += 1

            nomes_unicos = list(contagem.keys())

            text_content = f"Gold: [{term.bold_yellow(str(self.gold))}]\n"
            if not nomes_unicos:
                text_content += "Você não tem itens vendáveis.\n[0] Voltar"
                altura = 6
            else:
                for i, nome in enumerate(nomes_unicos, 1):
                    item = TODOS_OS_ITENS[nome]
                    preco = item.preco // 2
                    text_content += f"[{i}] {nome} (x{contagem[nome]}) - [{preco}]\n"
                text_content += "[0] Voltar"
                altura = text_content.count("\n") + 4

            clear_region_a(x, y, y + altura + 4, largura)
            draw_window(term, x, y, width=largura, height=altura, title="Vender Itens", text_content=text_content)

            with term.location(x + 2, y + altura - 2):
                try:
                    escolha = int(input("> "))
                    if escolha == 0:
                        return
                    item_nome = nomes_unicos[escolha - 1]
                    item = TODOS_OS_ITENS[item_nome]
                    preco = item.preco // 2
                    self.gold += preco
                    self.inventario.remove(item)
                    with term.location(x=0, y=altura+1):
                        print(f"Você vendeu {item.nome} por {preco} moedas.")
                except (ValueError, IndexError):
                    with term.location(x=largura, y=y):
                        ("Opção inválida.", x, y + altura, largura)

    def hospital(self, x_, y_):
        with term.location(x=x_, y=y_):
            print("Você dormil essa noite")
        self.hp = self.hp_max
        self.stm = self.stm_max
        self.mana = self.mana_max
        time.sleep(3)

