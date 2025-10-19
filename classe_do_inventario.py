from collections import defaultdict

class Item:
    """Representa um item no jogo."""
    def __init__(self, nome, tipo, bonus_hp=0, bonus_stm = 0,bonus_mana=0, bonus_atk=0, bonus_def=0, bonus_atk_mana=0, preco=0, slot_equip=None, vendivel=True, comprável=True):
        self.nome = nome
        self.vendivel = vendivel
        self.comprável = comprável
        self.tipo = tipo
        self.bonus_hp = bonus_hp
        self.bonus_mana = bonus_mana
        self.bonus_stm = bonus_stm
        self.bonus_atk = bonus_atk
        self.preco = preco
        self.bonus_atk_mana = bonus_atk_mana
        self.bonus_def = bonus_def
        self.slot_equip = slot_equip

    def __repr__(self):
        return f"Item(nome='{self.nome}', tipo='{self.tipo}', comprável={self.comprável})"

TODOS_OS_ITENS = {
    "Espada": Item(nome="Espada", tipo="Equipavel", preco=100, bonus_atk=5, slot_equip="m_pri", comprável=False),
    "Poção de Cura": Item(nome="Poção de Cura", tipo="Consumivel", preco=50, bonus_hp=20),
    "Elixir": Item(nome="Elixir", tipo="Consumivel", preco=50, bonus_mana=20),
    "Suco": Item(nome="Suco", tipo="Consumivel", preco=50, bonus_stm=20),
    "Cura Total":Item(nome="Cura Total", tipo="Consumivel", preco=1000, bonus_hp=50, bonus_mana=50),
    "Peitoral de Ferro": Item(nome="Peitoral de Ferro", tipo="Equipavel", preco=150, bonus_def=10, slot_equip="p_pet"),
    "Escudo": Item(nome="Escudo", tipo="Equipavel", preco=100, bonus_def=5, slot_equip="m_seg"),
    "Cajado": Item(nome="Cajado", tipo="Equipavel", preco=100, bonus_atk_mana=5, slot_equip="m_pri"),
    "Anel Lendário": Item(nome="Anel Lendário", tipo="Equipavel", preco=5000, bonus_def=25),
    "Crucifixo": Item(nome="Crucifixo", tipo="Equipavel", preco=0, vendivel=False, comprável=False,bonus_def=25, bonus_atk_mana=25, slot_equip="s_crad", ),
    "Chave": Item(nome='Chave', tipo="Chave", preco=0, vendivel=False, comprável=False),
    "Chave do Dragão": Item(nome='Chave do Dragão', tipo="Chave", preco=0, vendivel=False, comprável=False)
    }

class magias:
    def __init__(self, nome, tipo, bonus_hp=0, bonus_atk=0, bonus_def=0, bonus_stm=0, batalhas=False, mana_gasta=0, xp=0):
        self.nome = nome
        self.tipo = tipo
        self.bonus_hp = bonus_hp
        self.bonus_atk = bonus_atk
        self.bonus_def = bonus_def
        self.bonus_stm = bonus_stm
        self.batalhas = batalhas
        self.mana_gasta = mana_gasta
        self.xp = xp

    def __repr__(self):
        return f"magias(nome='{self.nome}', tipo='{self.tipo}')"

TODAS_AS_MAGIAS = {
    "Cura Leve": magias(nome="Cura Leve", tipo="Cura", bonus_hp=20, mana_gasta=10, xp=5),
    "Benção da Natureza": magias(nome="Benção da Natureza", tipo="Cura", bonus_hp=50, bonus_stm=10, mana_gasta=25, xp=10),
    "Tempestade de Raios": magias(nome="Tempestade de Raios", tipo="Ataque", bonus_atk=30, batalhas=True, mana_gasta=30, xp=10),
    "Bola de Fogo": magias(nome="Bola de Fogo", tipo="Ataque", bonus_atk=15, batalhas=True, mana_gasta=15, xp=5),
    "Regruta": magias(nome="Regruta", tipo="Ajudante", bonus_atk=5, bonus_def=5,mana_gasta=15, xp=5),
    "Arqueiro": magias(nome="Arqueiro", tipo="Ajudante", bonus_atk=10, mana_gasta=15, xp=5),
}