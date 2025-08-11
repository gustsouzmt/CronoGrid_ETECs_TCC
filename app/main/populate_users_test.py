#Atenção: Este é um exemplo de script para popular usuários em um banco de dados Flask com SQLAlchemy.

from werkzeug.security import generate_password_hash
from .models import Usuarios
from app import db
from .. import create_app

app = create_app('default')

from datetime import datetime

# Gerando um timestamp atual para usar nos exemplos
timestamp_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Lista de dicionários, cada um representando um usuário
usuarios = [
    {
        "nome_completo": "Ana Clara Medeiros",
        "email": "ana.medeiros@emailaluno.com",
        "senha": "hash_da_senha_da_ana",  # Em uma aplicação real, seria um hash
        "matricula": "ABC123",
        "id_cargo": 1,  # 1: Aluno
        "ativo": True,
        "criado_em": timestamp_atual,
        "atualizado_em": timestamp_atual
    },
    {
        "id_usuario": 2,
        "nome_completo": "Prof. Carlos Andrade",
        "email": "carlos.andrade@email.com",
        "senha": "hash_da_senha_do_carlos",
        "matricula": "ABC123",
        "id_cargo": 2,  # 2: Professor
        "ativo": True,
        "criado_em": timestamp_atual,
        "atualizado_em": timestamp_atual
    },
    {
        "nome_completo": "Coordenadora Beatriz Lima",
        "email": "beatriz.lima@email.com",
        "senha": "hash_da_senha_da_beatriz",
        "matricula": "ABC123",
        "id_cargo": 3,  # 3: Coordenador
        "ativo": True,
        "criado_em": timestamp_atual,
        "atualizado_em": timestamp_atual
    },
    {
        "nome_completo": "Diretor Ricardo Borges",
        "email": "ricardo.borges@email.com",
        "senha": "hash_da_senha_do_ricardo",
        "matricula": "ABC123",
        "id_cargo": 4,  # 4: Diretor
        "ativo": True, # Exemplo de um usuário inativo
        "criado_em": timestamp_atual,
        "atualizado_em": timestamp_atual
    }
]


with app.app_context():
    db.create_all()

    for u in usuarios:
        if not Usuarios.query.filter_by(email=u["email"]).first():
            usuarios = Usuarios(
                db,
                nome_completo=u["nome"],
                email=u["email"],
                senha=generate_password_hash(u["senha"]),
                matricula=u["codigo_instituicao"],
                id_cargo=u["role"],
                ativo=u["ativo"],
                criado_em=u["criado_em"],
                atualizado_em=u["atualizado_em"]
                
            )
            db.session.add(usuarios)
        
           
    
    db.session.commit()
    print("Usuários inseridos com sucesso.")
    