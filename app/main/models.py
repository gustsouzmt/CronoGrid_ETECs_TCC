from app import db
from sqlalchemy import text
from sqlalchemy.dialects.mysql import TIMESTAMP
from datetime import datetime

# --- MODELOS PRINCIPAIS (ATUALIZADOS) ---
class Cargos(db.Model):
    __tablename__ = 'cargos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    usuarios = db.relationship('Usuarios', backref='cargo', lazy=True)  # Relação adicionada

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'teacher', 'coordinator', 'school'
    disciplinas = db.Column(db.String(200))
    disponibilidade = db.Column(db.String(500))
    carga_horaria = db.Column(db.Integer)
    codigo_instituicao = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<{self.role.capitalize()} {self.nome}>'

class Usuarios(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)  # Campo único
    senha = db.Column(db.CHAR(60), nullable=False)
    matricula = db.Column(db.String(11), unique=True)  # Campo único
    id_cargo = db.Column(
        db.Integer,
        db.ForeignKey('cargos.id', ondelete='RESTRICT', onupdate='CASCADE'), 
        nullable=False
    )
    ativo = db.Column(db.Boolean, default=True)  # Novo campo
    criado_em = db.Column(
        TIMESTAMP,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP')
    )
    atualizado_em = db.Column(
        TIMESTAMP,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP'),
        server_onupdate=text('CURRENT_TIMESTAMP')
    )
    # Relações
    disciplinas = db.relationship('ProfessoresDisciplinas', backref='professor', lazy=True)

class Disciplinas(db.Model):
    __tablename__ = 'disciplinas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)  # Campo único
    codigo = db.Column(db.String(20), unique=True)
    carga_horaria_semanal = db.Column(db.Integer)
    professores = db.relationship('ProfessoresDisciplinas', backref='disciplina', lazy=True)

class ProfessoresDisciplinas(db.Model):
    __tablename__ = 'professores_disciplinas'
    id_professor = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True
    )
    id_disciplina = db.Column(
        db.Integer,
        db.ForeignKey('disciplinas.id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True
    )

class Instituicao(db.Model):
    __tablename__ = 'instituicoes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    numero = db.Column(db.String(20), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    uf = db.Column(db.String(2), nullable=False)
    cep = db.Column(db.String(20), nullable=False)
    telefone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    rede_ensino = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)

    diretor = db.relationship('DiretorAcademico', backref='instituicao', uselist=False)

class DiretorAcademico(db.Model):
    __tablename__ = 'diretores_academicos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    rg = db.Column(db.String(20), unique=True, nullable=False)
    sexo = db.Column(db.Enum('Masculino', 'Feminino'), nullable=False)
    telefone = db.Column(db.String(30), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)

    instituicao_id = db.Column(db.Integer, db.ForeignKey('instituicoes.id'), nullable=False)


# --- MODELOS---
class Turmas(db.Model):
    __tablename__ = 'turmas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    ano_letivo = db.Column(db.Integer, nullable=False)
    periodo = db.Column(db.String(50), nullable=False)

class AlunosTurmas(db.Model):
    __tablename__ = 'alunos_turmas'
    id_aluno = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id', ondelete='CASCADE', onupdate='CASCADE'), 
        primary_key=True
    )
    id_turma = db.Column(
        db.Integer, 
        db.ForeignKey('turmas.id', ondelete='CASCADE', onupdate='CASCADE'), 
        primary_key=True
    )
    ano_letivo = db.Column(db.Integer, primary_key=True)

class Salas(db.Model):
    __tablename__ = 'salas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    capacidade = db.Column(db.Integer)
    tipo = db.Column(db.String(50))

class AlunosHorarios(db.Model):
    __tablename__ = 'alunos_horarios'
    id_slot_horario = db.Column(db.Integer, primary_key=True)
    dia_semana = db.Column(
        db.Enum('Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'), 
        nullable=False
    )
    horario_inicio = db.Column(db.Time, nullable=False)
    horario_fim = db.Column(db.Time, nullable=False)
    descricao = db.Column(db.String(50))

class Materia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    arquivo_nome = db.Column(db.String(255))  # Nome do arquivo (opcional)


class DisponibilidadeProfessores(db.Model):
    __tablename__ = 'disponibilidade_professores'
    id = db.Column(db.Integer, primary_key=True)
    id_professor = db.Column(
        db.Integer, 
        db.ForeignKey('usuarios.id', ondelete='CASCADE', onupdate='CASCADE'), 
        nullable=False
    )
    id_slot_horario = db.Column(
        db.Integer, 
        db.ForeignKey('alunos_horarios.id_slot_horario', ondelete='CASCADE', onupdate='CASCADE'), 
        nullable=False
    )
    disponivel = db.Column(db.Boolean, default=True)
    ano_letivo_referencia = db.Column(db.Integer, nullable=False)

class GradeHorariaAlocacoes(db.Model):
    __tablename__ = 'grade_horaria_alocacoes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_turma = db.Column(
        db.Integer, 
        db.ForeignKey('turmas.id', ondelete='CASCADE', onupdate='CASCADE'), 
        nullable=False
    )
    id_disciplina = db.Column(
        db.Integer, 
        db.ForeignKey('disciplinas.id', ondelete='CASCADE', onupdate='CASCADE'), 
        nullable=False
    )
    id_professor = db.Column(
        db.Integer, 
        db.ForeignKey('usuarios.id', ondelete='RESTRICT', onupdate='CASCADE'), 
        nullable=False
    )
    id_sala = db.Column(
        db.Integer, 
        db.ForeignKey('salas.id', ondelete='RESTRICT', onupdate='CASCADE'), 
        nullable=False
    )
    id_slot_horario = db.Column(
        db.Integer, 
        db.ForeignKey('alunos_horarios.id_slot_horario', ondelete='RESTRICT', onupdate='CASCADE'), 
        nullable=False
    )
    ano_letivo = db.Column(db.Integer, nullable=False)
    semestre = db.Column(db.Integer, default=1)

class Comunicacoes(db.Model):
    __tablename__ = 'comunicacoes'
    id = db.Column(db.Integer, primary_key=True)
    id_remetente = db.Column(
        db.Integer, 
        db.ForeignKey('usuarios.id', ondelete='CASCADE', onupdate='CASCADE'), 
        nullable=False
    )
    tipo_comunicacao = db.Column(db.Enum('Notificacao', 'Recomendacao'), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    data_expiracao = db.Column(db.TIMESTAMP, nullable=True)

class ComunicacoesDestinatarios(db.Model):
    __tablename__ = 'comunicacoes_destinatarios'
    id = db.Column(db.Integer, primary_key=True)
    id_comunicacao = db.Column(
        db.Integer, 
        db.ForeignKey('comunicacoes.id', ondelete='CASCADE', onupdate='CASCADE'), 
        nullable=False
    )
    id_usuario_destinatario = db.Column(
        db.Integer, 
        db.ForeignKey('usuarios.id', ondelete='CASCADE', onupdate='CASCADE'), 
        nullable=True
    )
    id_cargo_destinatario = db.Column(
        db.Integer, 
        db.ForeignKey('cargos.id', ondelete='CASCADE', onupdate='CASCADE'), 
        nullable=True
    )
    id_turma_destinataria = db.Column(
        db.Integer, 
        db.ForeignKey('turmas.id', ondelete='CASCADE', onupdate='CASCADE'), 
        nullable=True
    )
    lida = db.Column(db.Boolean, default=False)
    data_leitura = db.Column(db.TIMESTAMP, nullable=True)