import random, time

def interagir_com_objeto(px, py, ch, player, mapa_art, mapa_id, interacoes_contagem, ESTADO_MAPAS, TODOS_OS_ITENS, save_filename, mapas_, salvar_mapa_estado, substituir_caractere):
    feedback_message = ""
    pos = (px, py)
    interacoes_contagem[pos] = interacoes_contagem.get(pos, 0) + 1
    tentativas = interacoes_contagem[pos]
    if player.stm <= 0:
        feedback_message = 'Você não tem energia o suficiente'
    else:
        # ÁRVORE (♣)
        if ch == '♣':
            item_equipado = player.equipa.get("m_ter")
            if item_equipado and item_equipado.nome.lower() == "machado/madeira":
                if tentativas == 1:
                    feedback_message = 'Você iniciou a cortar uma Árvore'
                elif tentativas == 3:
                    feedback_message = 'Você quebrou uma Árvore'
                    mapa_art[py] = mapa_art[py][:px] + '.' + mapa_art[py][px + 1:]
                    interacoes_contagem.pop(pos, None)
                    for _ in range(5):
                        player.inventario.append(TODOS_OS_ITENS["Madeira"])
                    player.inventario.append(TODOS_OS_ITENS['Muda/Arvore'])
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    player.stm -= 15
            if item_equipado and item_equipado.nome.lower() == "machado/pedra":
                if tentativas == 1:
                    feedback_message = 'Você iniciou a cortar uma Árvore'
                elif tentativas == 2:
                    feedback_message = 'Você quebrou uma Árvore'
                    mapa_art[py] = mapa_art[py][:px] + '.' + mapa_art[py][px + 1:]
                    interacoes_contagem.pop(pos, None)
                    for _ in range(5):
                        player.inventario.append(TODOS_OS_ITENS["Madeira"])
                    player.inventario.append(TODOS_OS_ITENS['Muda/Arvore'])
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    player.stm -= 10
            if item_equipado and item_equipado.nome.lower() == "machado/ferro":
                if tentativas == 1:
                    feedback_message = 'Você quebrou uma Árvore'
                    mapa_art[py] = mapa_art[py][:px] + '.' + mapa_art[py][px + 1:]
                    interacoes_contagem.pop(pos, None)
                    for _ in range(5):
                        player.inventario.append(TODOS_OS_ITENS["Madeira"])
                    player.inventario.append(TODOS_OS_ITENS['Muda/Arvore'])
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    player.stm -= 5
            else:
                if tentativas == 1:
                    feedback_message = 'Você iniciou o corte da Arvore'
                if tentativas == 5:
                    feedback_message = 'Você quebrou a Arvore'
                    mapa_art[py] = mapa_art[py][:px] + '.' + mapa_art[py][px + 1:]
                    interacoes_contagem.pop(pos, None)
                    for _ in range(5):
                        player.inventario.append(TODOS_OS_ITENS["Madeira"])
                    player.inventario.append(TODOS_OS_ITENS['Muda/Arvore'])
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    player.stm -= 20
        #BANCADA (C)
        elif ch == 'C':
            feedback_message = "Você coletou a Bancada"
            mapa_art[py] = mapa_art[py][:px] + '.' + mapa_art[py][px + 1:]
            interacoes_contagem.pop(pos, None)
            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
            player.stm -= 5

        #ARBUSTO (♠)
        elif ch == '♠':
            feedback_message = "Você colheu um arbusto"
            mapa_art[py] = mapa_art[py][:px] + 'x' + mapa_art[py][px + 1:]
            interacoes_contagem.pop(pos, None)
            cair = random.randint(1, 5)
            for _ in range(cair):
                player.inventario.append(TODOS_OS_ITENS["Fruta"])
            ESTADO_MAPAS[mapa_id]["regeneracoes"][(px, py)] = {
                "tempo_inicio": time.time(),
                "tempo_regeneracao": 30,
            }
            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
            player.stm -= 2

        #MILHO (¥)
        elif ch == '¥':
            feedback_message = "Você coletou o Milho"
            quantia = random.randint(1, 5)
            mapa_art[py] = mapa_art[py][:px] + '=' + mapa_art[py][px + 1:]
            interacoes_contagem.pop(pos, None)
            for _ in range(quantia):
                player.inventario.append(TODOS_OS_ITENS["Milho"])
            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
            player.stm -= 1

        #ARBUSTO PEQUENO (x)
        elif ch == 'x':
            if tentativas == 1:
                feedback_message = "Você começa a cortar o arbusto..."
            elif tentativas == 2:
                feedback_message = "O arbusto caiu..."
                mapa_art[py] = mapa_art[py][:px] + '.' + mapa_art[py][px + 1:]
                interacoes_contagem.pop(pos, None)
                if pos in ESTADO_MAPAS[mapa_id].get("regeneracoes", {}):
                    del ESTADO_MAPAS[mapa_id]["regeneracoes"][pos]
                for _ in range(2):
                    player.inventario.append(TODOS_OS_ITENS["Madeira"])
                player.inventario.append(TODOS_OS_ITENS['Semente/Arbusto'])
                salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                player.stm -= 10

        # MADEIRA (PRAIA - #)
        elif ch == '#':
            feedback_message = 'Você quebrou a Madeira'
            substituir_caractere(mapa_art, px, py, '.')
            player.inventario.append(TODOS_OS_ITENS['Madeira'])
            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
            player.stm -= 5

        # PEDRA (o)
        elif ch == 'o':
            item_equipado = player.equipa.get("m_ter")
            if item_equipado and item_equipado.nome.lower() == "picareta":
                if tentativas == 1:
                    feedback_message = 'Você iniciou uma Pedra'
                elif tentativas == 3:
                    feedback_message = 'Você quebrou a Pedra'
                    substituir_caractere(mapa_art, px, py, '.')
                    player.inventario.append(TODOS_OS_ITENS['Pedra'])
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    player.stm -= 15
            if item_equipado and item_equipado.nome.lower() == "picareta/pedra":
                if tentativas == 1:
                    feedback_message = 'Você iniciou uma Pedra'
                elif tentativas == 2:
                    feedback_message = 'Você quebrou a Pedra'
                    substituir_caractere(mapa_art, px, py, '.')
                    player.inventario.append(TODOS_OS_ITENS['Pedra'])
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    player.stm -= 10
            if item_equipado and item_equipado.nome.lower() == "picareta/ferro":
                if tentativas == 1:
                    feedback_message = 'Você quebrou uma Pedra'
                    substituir_caractere(mapa_art, px, py, '.')
                    player.inventario.append(TODOS_OS_ITENS['Pedra'])
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    player.stm -= 5
            else:
                feedback_message = 'Você precisa de uma Picareta'

        # CARVÃO (c) 
        elif ch == 'c':
            item_equipado = player.equipa.get("m_ter")
            if item_equipado and item_equipado.nome.lower() == "picareta/madeia":
                if tentativas == 1:
                    feedback_message = 'Você iniciou um carvão'
                elif tentativas == 3:
                    feedback_message = 'Você quebrou o carvão'
                    substituir_caractere(mapa_art, px, py, '.')
                    player.inventario.append(TODOS_OS_ITENS['Carvão'])
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    player.stm -= 15
            if item_equipado and item_equipado.nome.lower() == "picareta/pedra":
                if tentativas == 1:
                    feedback_message = 'Você iniciou um carvão'
                elif tentativas == 2:
                    feedback_message = 'Você quebrou o carvão'
                    substituir_caractere(mapa_art, px, py, '.')
                    player.inventario.append(TODOS_OS_ITENS['Carvão'])
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    player.stm -= 10
            if item_equipado and item_equipado.nome.lower() == "picareta/ferro":
                if tentativas == 1:
                    feedback_message = 'Você quebrou um Carvão'
                    substituir_caractere(mapa_art, px, py, '.')
                    player.inventario.append(TODOS_OS_ITENS['Carvão'])
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    player.stm -= 5
            else:
                feedback_message = 'Você precisa de uma Picareta'

        elif ch == 'u':
            item_equipado = player.equipa.get("m_ter")
            if item_equipado and item_equipado.nome.lower() == "picareta/pedra":
                if tentativas == 1:
                    feedback_message = 'Você iniciou um Ferro'
                elif tentativas == 2:
                    feedback_message = 'Você quebrou o Ferro'
                    substituir_caractere(mapa_art, px, py, '.')
                    player.inventario.append(TODOS_OS_ITENS['Ferro'])
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    player.stm -= 10
            if item_equipado and item_equipado.nome.lower() == "picareta/ferro":
                if tentativas == 1:
                    feedback_message = 'Você quebrou um Ferro'
                    substituir_caractere(mapa_art, px, py, '.')
                    player.inventario.append(TODOS_OS_ITENS['Ferro'])
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    player.stm -= 5
            else:
                feedback_message = 'Você precisa de uma Picareta de Pedra no minimo'

        # TRIGO (‼)
        elif ch == '‼':
            feedback_message = "Você coletou o Trigo"
            quantia = random.randint(1, 5)
            mapa_art[py] = mapa_art[py][:px] + '=' + mapa_art[py][px + 1:]
            interacoes_contagem.pop(pos, None)
            for _ in range(quantia):
                player.inventario.append(TODOS_OS_ITENS["Trigo"])
            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
            player.stm -= 1

        #BAÚ ($)
        elif ch == '$':
            ESTADO = ESTADO_MAPAS[mapa_id]
            baus_armazenamento = ESTADO.setdefault("baus_armazenamento", {})
            if pos in baus_armazenamento:
                conteudo_bau = baus_armazenamento[pos]
                if not conteudo_bau:
                    feedback_message = "Você quebrou um baú vazio."
                    substituir_caractere(mapa_art, px, py, '.')
                    del baus_armazenamento[pos]
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO)
                    player.stm -= 1
                else:
                    feedback_message = "O baú ainda contém itens. Esvazie-o antes de quebrar."
            else:
                feedback_message = "Este baú parece não existir mais no registro."

        return feedback_message

def usar_item(player, entrada, mapa_art, mapa_id, ESTADO_MAPAS, TODOS_OS_ITENS,save_filename, mapas_, salvar_mapa_estado, substituir_caractere):
    feedback_message = ""
    if len(entrada) > 1 and entrada[1].isdigit():
        indice = int(entrada[1]) - 1
        if 0 <= indice < 4:
            slot_nome = f"slot_{indice + 1}"
            material_slot = player.matariais['slots'].get(slot_nome)
            if not material_slot:
                return f"O slot {indice + 1} está vazio."

            item_escolhido = material_slot
            if item_escolhido not in player.inventario:
                player.matariais['slots'][slot_nome] = None
                return f"O item {item_escolhido.nome} não está mais no inventário. Slot liberado."

            nome = item_escolhido.nome

            #Construções básicas
            construcoes = {
                "Madeira": ("#", "Você colocou Madeira."),
                "Bancada": ("C", "Você colocou Bancada."),
                "Pedra": ("#", "Você colocou Pedra."),
                "Bau": ("$", "Você colocou um Baú."),
                'Chão': (':', 'Você colocou um chão'),
            }

            if nome in construcoes:
                char, msg = construcoes[nome]
                substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, char)
                player.inventario.remove(item_escolhido)
                salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                feedback_message = msg

            # ======= Plantio =======
            elif nome in ['Semente/Arbusto', 'Semente/Abobora', 'Semente/Milho', 'Semente/Trigo', 'Muda/Arvore']:
                tipo_map = {
                    "Semente/Trigo": ("trigo", 30 * 60),
                    "Semente/Milho": ("milho", 30 * 60),
                    "Semente/Abobora": ("abobora", 45 * 60),
                    "Muda/Arvore": ("arvore", 45 * 60),
                    "Semente/Arbusto": ("arbusto", 1000)
                }

                tipo, tempo_crescimento = tipo_map[nome]
                terreno = mapa_art[player.y_mapa][player.x_mapa]

                if tipo in ('trigo', 'milho', 'abobora') and terreno != "=":
                    return "Você só pode plantar sementes em solo arado ('=')."
                elif tipo in ('arvore', 'arbusto') and terreno != ".":
                    return "Você só pode plantar a muda em terra ('.')."

                char = "*" if tipo in ('trigo', 'milho', 'abobora') else "1"
                substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, char)
                ESTADO_MAPAS[mapa_id]["plantacoes"][(player.x_mapa, player.y_mapa)] = {
                    "item": tipo,
                    "tempo_plantio": time.time(),
                    "tempo_crescimento": tempo_crescimento,
                }

                player.inventario.remove(item_escolhido)
                salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                feedback_message = f"Você plantou {tipo.capitalize()}!"

            # Outros materiais
            else:
                feedback_message = f"Você usou o material {item_escolhido.nome}!"

            tem_mais = any(i.nome == item_escolhido.nome for i in player.inventario)
            if not tem_mais:
                player.matariais['slots'][slot_nome] = None

        elif indice < len(player.inventario):
            item_escolhido = player.inventario[indice]
            if item_escolhido.tipo == "Material":
                feedback_message = "Você precisa equipar esse material em um slot para usá-lo."
            else:
                feedback_message = f"Você usou o item {item_escolhido.nome}!"
        else:
            feedback_message = "Número inválido."
    else:
        feedback_message = "Use: usar [número]"

    return feedback_message
