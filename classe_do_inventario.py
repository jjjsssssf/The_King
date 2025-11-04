from collections import defaultdict

class Item:
    """Representa um item no jogo."""
    def __init__(self, nome, tipo,bonus_hp=0, bonus_stm = 0,bonus_mana=0, bonus_atk=0, bonus_def=0, bonus_atk_mana=0, bonus_hp_max=0,preco=0, slot_equip=None, vendivel=True, comprável=True):
        self.nome = nome
        self.vendivel = vendivel
        self.comprável = comprável
        self.tipo = tipo
        self.bonus_hp = bonus_hp
        self.bonus_hp_max = bonus_hp_max
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
    ###ARMAS
    "Espada": Item(nome="Espada", tipo="Equipavel", preco=100, bonus_atk=10, slot_equip="m_pri"),
    "Picareta": Item(nome='Picareta', tipo='Equipavel', preco=100, bonus_atk=5, slot_equip="m_pri"),
    "Pá": Item(nome='Pá', tipo='Equipavel', preco=100, bonus_atk=2, slot_equip="m_pri"),
    "Enchada": Item(nome='Enchada', tipo='Equipavel', preco=100, bonus_atk=2, slot_equip="m_pri"),
    'Machado': Item(nome='Machado', tipo='Equipavel', preco=100, bonus_atk=2, slot_equip="m_pri"),
    ##CONS
    "Fruta": Item(nome="Fruta", tipo="Consumivel", preco=50, bonus_hp=25, bonus_stm=25),
    'Bolo de Milho': Item(nome="Bolo de Milho", tipo="Consumivel", preco=50, bonus_hp=25, bonus_stm=25),
    "Elixir": Item(nome="Elixir", tipo="Consumivel", preco=50, bonus_mana=50),
    "Suco": Item(nome="Suco", tipo="Consumivel", preco=50, bonus_stm=50),
    "Cura Total":Item(nome="Cura Total", tipo="Consumivel", preco=1000, bonus_hp=50, bonus_mana=50),
    "Trigo": Item(nome="Trigo", tipo="Produto", preco=10),
    "Milho": Item(nome="Milho", tipo="Produto", preco=25,),
    "Abobora": Item(nome="Abobora", tipo="Produto", preco=50, bonus_hp=25, bonus_stm=25),
    "Pão": Item(nome="Pão", tipo="Consumivel", preco=50, bonus_hp=50, bonus_stm=50),
    ##ARDUR
    "Peitoral": Item(nome="Peitoral", tipo="Equipavel", preco=150, bonus_def=5, bonus_hp_max=50,slot_equip="p_pet"),
    "Elmo": Item(nome="Elmo", tipo="Equipavel", preco=100, bonus_def=2, bonus_hp_max=25,slot_equip="c_cap"),
    ##Chaves
    "Chave": Item(nome='Chave', tipo="Chave", preco=0, vendivel=False, comprável=False),
    "Chave do Dragão": Item(nome='Chave do Dragão', tipo="Chave", preco=0, vendivel=False, comprável=False),
    ##Coletaveis
    "Madeira": Item(nome="Madeira", tipo="Material", slot_equip="slots"),
    "Bau": Item(nome="Bau", tipo="Material", slot_equip="slots"),
    "Pedra": Item(nome="Pedra", tipo="Material", slot_equip="slots"),
    "Bancada": Item(nome="Bancada", tipo="Material", slot_equip="slots"),
    "Semente/Trigo": Item(nome="Semente/Trigo", tipo="Material", slot_equip="slots"),
    "Semente/Abobora": Item(nome="Semente/Abobora", tipo="Material", slot_equip="slots"),
    "Semente/Milho": Item(nome="Semente/Milho", tipo="Material", slot_equip="slots"),
    'Muda/Arvore': Item(nome="Muda/Arvore", tipo="Material", slot_equip="slots"),
    'Semente/Arbusto': Item(nome="Semente/Arbusto", tipo="Material", slot_equip="slots"),    
}

RECEITAS = {
    'Pão':{
    'Trigo': 5
    },
    'Enchada':{
    'Madeira': 2,
    'Pedra': 3
    },
    'Pá':{
    'Madeira': 2,
    'Pedra': 3
    },
    'Espada':{
    'Pedra': 5,
    'Graveto': 5
    },
    'Bolo de Milho':{
    'Milho': 5
    },
    'Machado': {
    'Madeira': 5,
    'Pedra': 5
    }, 
    'Bau': {
    'Madeira':5,
    'Pedra': 1
    }

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
}