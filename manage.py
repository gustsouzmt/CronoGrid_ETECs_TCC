from app import create_app, db
from app.main.models import Cargos, Usuarios
from flask_migrate import Migrate
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Configura o Flask-Migrate para gerenciar as migrações do banco de dados
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Cargos=Cargos, Usuarios=Usuarios)


@app.cli.command('seed_db')
def seed_db_command():
    """Popula o banco de dados com dados iniciais."""
    from werkzeug.security import generate_password_hash
    
    # Lista de dicionários, cada um representando um usuário
    usuarios = [
        {
            "nome": "Ana Clara Medeiros",
            "email": "ana.medeiros@emailaluno.com",
            "senha": "hash_da_senha_da_ana",  # Em uma aplicação real, seria um hash
            "matricula": "ABC123",
            "id_cargo": 1,  # 1: Aluno
            "ativo": True,
        },  
        {

            "nome": "Carlos Andrade",
            "email": "carlos.andrade@email.com",
            "senha": "hash_da_senha_do_carlos",
            "matricula": "ABC123",
            "id_cargo": 2,  # 2: Professor
            "ativo": True,
          
        },
        {
            "nome": "Beatriz Lima",
            "email": "beatriz.lima@email.com",
            "senha": "hash_da_senha_da_beatriz",
            "matricula": "ABC123",
            "id_cargo": 3,  # 3: Coordenador
            "ativo": True,
        },
        {
            "nome": " Jubileu Borges",
            "email": "ricardo.borges@email.com",
            "senha": "hash_da_senha_do_ricardo",
            "matricula": "ABC123",
            "id_cargo": 4,  # 4: Diretor
            "ativo": True, 
            
            # Exemplo de um usuário inativo
        },
            {
            "nome": "Ricardo Borges",
            "email": "ricardo.borges@email.com",
            "senha": "hash_da_senha_do_ricardo",
            "matricula": "ABC123",
            "id_cargo": 4,  # 4: Diretor
            "ativo": False, 
            
        }
    ]
    with app.app_context():
        db.create_all()

        for u in usuarios:
            try:
                if not Usuarios.query.filter_by(email=u["email"]).first():
                    plain_text_password = u.pop('senha')
                
                # Gera o hash da senha antes de criar o usuário                
                    hashed_password = generate_password_hash(plain_text_password)
                    novo_usuario = Usuarios(**u, senha=hashed_password)
                    db.session.add(novo_usuario)
                    db.session.commit() # <--- COMMIT DENTRO DO LOOP
                print(f"SUCESSO: Usuário {u['email']} adicionado.")
            except Exception as e:
                print(f"FALHA ao adicionar {u.get('email', 'usuário desconhecido')}: {e}")
                db.session.rollback() # Desfaz a tentativa de adicionar este usuário
         
    
    db.session.commit()
    print("Usuários inseridos com sucesso.")

    
    return "Banco de dados populado com sucesso!"