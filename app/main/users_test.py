from flask_sqlalchemy import SQLAlchemy

sql = SQLAlchemy()

class Usuario(sql.Model):
    id = sql.Column(sql.Integer, primary_key=True)
    nome = sql.Column(sql.String(100), nullable=False)
    email = sql.Column(sql.String(100), unique=True, nullable=False)
    senha_hash = sql.Column(sql.String(200), nullable=False)
    role = sql.Column(sql.String(50), nullable=False)  # 'teacher', 'coordinator', 'school'
    disciplinas = sql.Column(sql.String(200))
    disponibilidade = sql.Column(sql.String(500))
    carga_horaria = sql.Column(sql.Integer)
    codigo_instituicao = sql.Column(sql.String(50), nullable=True)

    def __repr__(self):
        return f'<{self.role.capitalize()} {self.nome}>'
    