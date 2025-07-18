from flask import request, render_template, session, redirect, url_for, flash, jsonify
from datetime import datetime
from app.main.forms import CadastroInstituicaoForm, MateriaForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from app import db, data_file
from . import main
from .models import Materia, Usuario, Usuarios, Cargos, Disciplinas, ProfessoresDisciplinas, Instituicao, DiretorAcademico
from os import path
from json import load, dump
from .grid_generation import gerar_grade_horaria

# --- Funções originais (JSON) mantidas por desencargo de consciência ---
def carregar_professores():
    if not path.exists(data_file):
        return []
    with open(data_file, 'r', encoding='utf-8') as f:
        return load(f)
    


def salvar_professores(professores):
    with open(data_file, 'w', encoding='utf-8') as f:
        dump(professores, f, ensure_ascii=False, indent=2)

# --- Rotas originais (mantidas intactas) ---
@main.route('/', methods=['GET', 'POST'])
def home():
    return redirect(url_for('main.login'))

@main.route('/index', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        flash("Faça login para continuar.", "warning")
        return redirect(url_for('main.login'))

    professores = carregar_professores()
    return render_template('index.html', professores=professores)

@main.route('/adicionar_professor', methods=['GET', 'POST'])
def adicionar_professor():
    nome = request.form.get('nome')
    materias = request.form.getlist('materias')
    
    disponibilidade = {}
    dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
    periodos = ['manha', 'tarde', 'noite']
    
    for dia in dias:
        disponibilidade[dia] = {}
        for periodo in periodos:
            disponibilidade[dia][periodo] = True if request.form.get(f'disponibilidade[{dia}][{periodo}]') == 'on' else False
    
    novo_professor = {
        'id': datetime.now().strftime("%Y%m%d%H%M%S"),
        'nome': nome,
        'materias': materias,
        'disponibilidade': disponibilidade
    }
    
    professores = carregar_professores()
    professores.append(novo_professor)
    salvar_professores(professores)
    
    return redirect(url_for('main.index'))

@main.route('/editar_professor/<professor_id>', methods=['GET', 'POST'])
def editar_professor(professor_id):
    professores = carregar_professores()
    professor = next((p for p in professores if p['id'] == professor_id), None)
    
    if not professor:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        professor['nome'] = request.form['nome']
        professor['materias'] = request.form.getlist('materias')
        
        dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        periodos = ['manha', 'tarde', 'noite']
        
        for dia in dias:
            for periodo in periodos:
                professor['disponibilidade'][dia][periodo] = True if request.form.get(f'disponibilidade[{dia}][{periodo}]') == 'on' else False
        
        salvar_professores(professores)
        return redirect(url_for('main.index'))
    
    return render_template('edit_teacher.html', professor=professor)

@main.route('/excluir_professor/<professor_id>')
def excluir_professor(professor_id):
    professores = carregar_professores()
    professores = [p for p in professores if p['id'] != professor_id]
    salvar_professores(professores)
    return redirect(url_for('main.index'))

@main.route('/grade_horaria')
def grade_horaria():
    resultado = gerar_grade_horaria()
    return render_template('grid_schedule.html', grade=resultado)

@main.route('/gerar_horarios')
def gerar_horarios():
    professores = carregar_professores()
    return jsonify({"status": "Funcionalidade em desenvolvimento", "professores": len(professores)})

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        email = request.form.get('email')
        password = request.form.get('password')
        codigo = request.form.get('institution_code')

        usuario = Usuario.query.filter_by(email=email, role=role, codigo_instituicao=codigo).first()

        if not usuario:
            flash("Usuário ou código de instituição inválido.", "danger")
            return redirect(url_for('main.login'))

        if not check_password_hash(usuario.senha_hash, password):
            flash("Senha incorreta.", "danger")
            return redirect(url_for('main.login'))

        session['user_id'] = usuario.id
        session['user_role'] = usuario.role
        flash(f"Bem-vindo, {usuario.nome}!", "success")
        return redirect(url_for('main.index'))

    return render_template('login.html')

@main.route('/professor', methods=['GET', 'POST'])
def professor():
    return render_template('professor.html')

@main.route('/professores', methods=['GET', 'POST'])
def professores():
    return render_template('professores.html')

@main.route('/lista_professores', methods=['GET', 'POST'])
def lista_professores():
    return 'lista de professores'

# --- Rotas atualizadas (cadastro + listagem de usuários) ---
@main.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = CadastroInstituicaoForm()
    
    if form.validate_on_submit():
        try:
            # 1. Cadastra a Instituição
            instituicao = Instituicao(
                nome=form.instituicao.data,
                cnpj=form.cnpj.data,
                endereco=form.endereco.data,
                numero=form.numero.data,
                bairro=form.bairro.data,
                cidade=form.cidade.data,
                uf=form.uf.data,
                cep=form.cep.data,
                telefone=form.telefone.data,
                email=form.email.data,
                rede_ensino=form.rede_ensino.data,
                categoria=form.categoria.data
            )
            db.session.add(instituicao)
            db.session.flush()  # Para pegar o id da instituição gerado

            # 2. Cadastra o Diretor Acadêmico e vincula à instituição
            diretor = DiretorAcademico(
                nome=form.diretor_nome.data,
                cpf=form.diretor_cpf.data,
                rg=form.diretor_rg.data,
                sexo=form.diretor_sexo.data,
                telefone=form.diretor_telefone.data,
                endereco=form.diretor_endereco.data,
                instituicao_id=instituicao.id
            )
            db.session.add(diretor)

            # Commit das duas operações
            db.session.commit()

            flash("Cadastro da instituição e diretor realizado com sucesso!", "success")
            return redirect(url_for('main.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Erro no cadastro: {str(e)}", "danger")
    
    return render_template('cadastro.html', form=form)

@main.route('/usuarios')
def usuarios():
    # Consulta otimizada com JOIN para o template usuarios.html
    usuarios = db.session.query(
        Usuarios.id,
        Usuarios.nome,
        Usuarios.email,
        Cargos.nome.label('funcao')
    ).join(
        Cargos, Usuarios.id_cargo == Cargos.id
    ).all()
    
    return render_template('usuarios.html', usuarios=usuarios)

# --- Função auxiliar mantida ---
def obter_id_cargo(nome_cargo):
    cargo = Cargos.query.filter_by(nome=nome_cargo).first()
    if not cargo:
        novo = Cargos(nome=nome_cargo)
        db.session.add(novo)
        db.session.commit()
        return novo.id
    return cargo.id


@main.route('/adicionar_materia', methods=['GET', 'POST'])
def adicionar_materia():
    form = MateriaForm()
    if form.validate_on_submit():
        filename = None
        if form.arquivo.data:
            filename = secure_filename(form.arquivo.data.filename)
            upload_path = os.path.join(main.config['UPLOAD_FOLDER'], filename)
            form.arquivo.data.save(upload_path)

        nova_materia = Materia(
            nome=form.nome.data,
            area=form.area.data,
            arquivo_nome=filename
        )
        db.session.add(nova_materia)
        db.session.commit()
        flash(f'Matéria "{form.nome.data}" cadastrada com sucesso!', 'success')
        return redirect(url_for('main.adicionar_materia'))
    return render_template('adicionarmateria.html', form=form)