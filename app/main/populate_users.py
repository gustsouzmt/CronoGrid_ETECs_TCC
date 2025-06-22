from werkzeug.security import generate_password_hash
from .models import Usuario, db
from .. import create_app

app = create_app('default')

usuarios_iniciais = [
    # Professores
    {
        "nome": "Maria Silva",
        "email": "maria@escola.com",
        "senha": "senha123",
        "role": "teacher",
        "disciplinas": "Matemática",
        "carga_horaria": 20,
        "codigo_instituicao": "ABC123"
    },
    {
        "nome": "João Oliveira",
        "email": "joao@escola.com",
        "senha": "senha456",
        "role": "teacher",
        "disciplinas": "Português",
        "carga_horaria": 15,
        "codigo_instituicao": "ABC123"
    },

    # Coordenadores
    {
        "nome": "Clara Souza",
        "email": "clara@escola.com",
        "senha": "coord123",
        "role": "coordinator",
        "disciplinas": "",
        "carga_horaria": 0,
        "codigo_instituicao": "ABC123"
    },

    # Escola (diretor/gestor)
    {
        "nome": "Diretor Carlos",
        "email": "carlos@escola.com",
        "senha": "gestao2024",
        "role": "school",
        "disciplinas": "",
        "carga_horaria": 0,
        "codigo_instituicao": "ABC123"
    }
]

with app.app_context():
    db.create_all()

    for u in usuarios_iniciais:
        if not Usuario.query.filter_by(email=u["email"]).first():
            novo_usuario = Usuario(
                nome=u["nome"],
                email=u["email"],
                senha_hash=generate_password_hash(u["senha"]),
                role=u["role"],
                disciplinas=u["disciplinas"],
                carga_horaria=u["carga_horaria"],
                codigo_instituicao=u["codigo_instituicao"]
            )
            db.session.add(novo_usuario)
    
    db.session.commit()
    print("Usuários inseridos com sucesso.")
    