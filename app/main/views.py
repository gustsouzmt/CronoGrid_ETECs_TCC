from flask import request, render_template, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from .. import db
from . import main
from .models import ProfessoresDisciplinas, Usuarios, Cargos, Disciplinas
from .grid_generation import gerar_grade_horaria
from ..emails import send_email


@main.route('/')
def tela_inicial():
    """
    NOVA ROTA: Renderiza a página inicial/landing page do projeto.
    Antes, a rota '/' redirecionava para o login. Agora mostra a tela de boas-vindas.
    """
    return render_template('tela_inicial.html')


@main.route('/dashboard')
def dashboard():
    """
    NOVA ROTA: Renderiza o painel principal do usuário logado.
    Verifica se o usuário está na sessão antes de permitir o acesso.
    """
    if 'user_id' not in session:
        flash("Faça login para acessar o painel.", "warning")
        return redirect(url_for('main.login'))
    
    return render_template('dashboard.html')

'''@main.route('/professores')
def professores():
    """
    ROTA ATUALIZADA: Agora busca os professores do banco de dados e os envia
    para o template 'professores.html', tornando-o dinâmico.
    """
    # Filtra usuários que têm o cargo de professor (assumindo id_cargo=2 para Professor)
    lista_de_professores = Usuarios.query.join(Cargos).filter(Cargos.nome_cargo == 'Professor').all()
    return render_template('professores.html', professores=lista_de_professores)'''


@main.route('/professor/<int:usuario_id>')
def professor_detalhe(usuario_id):
    """
    ROTA ATUALIZADA: Mostra a página de detalhes de um professor específico.
    Busca o professor pelo ID no banco de dados.
    """
    professor = Usuarios.query.get_or_404(usuario_id)
    return render_template('professor.html', professor=professor)


@main.route('/materias/adicionar', methods=['GET', 'POST'])
def adicionar_materia():
    """
    NOVA ROTA: Renderiza e processa o formulário de adicionar matéria.
    """
    if request.method == 'POST':
        nome_materia = request.form.get('nome')
        area = request.form.get('area')
        
        if not nome_materia or not area:
            flash('Todos os campos são obrigatórios!', 'danger')
            return redirect(url_for('main.adicionar_materia'))
            
        nova_disciplina = Disciplinas(nome=nome_materia, area_conhecimento=area) # Supondo que seu modelo Disciplinas tenha 'area_conhecimento'
        db.session.add(nova_disciplina)
        db.session.commit()
        
        flash(f'Matéria "{nome_materia}" adicionada com sucesso!', 'success')
        return redirect(url_for('main.adicionar_materia'))

    return render_template('adicionarmateria.html')

@main.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """
    ROTA ATUALIZADA: Adicionada a lógica POST para processar o formulário.
    Esta é uma implementação básica. Você precisará expandi-la para salvar todos os campos.
    """
    if request.method == 'POST':
        # Lógica para pegar os dados do formulário de cadastro e salvar no banco
        # Exemplo para o diretor:
        nome_diretor = request.form.get('nome_diretor')
        email_diretor = request.form.get('email_diretor')
        senha_diretor = request.form.get('senha_diretor')
        
        # Busca o ID do cargo 'Diretor'
        cargo_diretor = Cargos.query.filter_by(nome_cargo='Diretor').first()
        
        if not cargo_diretor:
            # Crie o cargo se ele não existir
            cargo_diretor = Cargos(nome_cargo='Diretor')
            db.session.add(cargo_diretor)
            db.session.commit()

        novo_diretor = Usuarios(
            nome_completo=nome_diretor,
            email=email_diretor,
            senha=generate_password_hash(senha_diretor),
            id_cargo=cargo_diretor.id
        )
        if novo_diretor:
            send_email(
                novo_diretor.email, 
                'Bem-vindo ao Sistema!', 
                'emails/boas_vindas', 
                user=novo_diretor
            )
            
        db.session.add(novo_diretor)
        db.session.commit()


        flash('Cadastro realizado com sucesso! Um email de confirmação foi enviado.')
        return redirect(url_for('main.login'))
        
        
    return render_template('cadastro.html')

# Rotas Já existentes para login, logout e outras funcionalidades

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cargo = request.form.get('cargo')
        email = request.form.get('email')
        password = request.form.get('password')
        matricula = request.form.get('matricula')
        
        # Lógica de login simplificada e corrigida
        cargo_valido = Usuarios.query.filter_by(id_cargo=cargo).first() # "1" -> "Aluno", "2" -> "Professor", etc.
        if not cargo_valido:
            flash("Cargo inválido.", "danger")
            return redirect(url_for('main.login'))

        usuario = Usuarios.query.filter_by(email=email, matricula=matricula, id_cargo=cargo).first()
        
        if usuario is None:
            flash("Usuário anulado", "danger")
            return redirect(url_for('main.login'))
        
        matricula_valido = Usuarios.query.filter_by(matricula=matricula).first() # "teacher" -> "Teacher"

        if not matricula_valido:
            flash("código de instituição inválido", "danger")
            return redirect(url_for('main.login'))
        
        if not check_password_hash(usuario.senha, password):
            flash("Senha incorreta.", "danger")
            return redirect(url_for('main.login'))
        
        # Verifica se o usuário está ativo
        if not usuario.ativo:         
            flash("Usuário inativo. Contate o administrador.", "danger")
            return redirect(url_for('main.login'))
          
        # Armazena mais informações na sessão para uso nos templates
        session['user_id'] = usuario.id
        session['user_name'] = usuario.nome
        session['user_role'] = usuario.id_cargo # Acessa o nome do cargo pela relação
        
        flash(f"Bem-vindo, {usuario.nome}!", "success")
        return redirect(url_for('main.dashboard')) # Redireciona para o dashboard
    # Se for GET, apenas renderiza o template de login
    
    if 'user_id' in session:
        flash("Você já está logado.", "info")
        return redirect(url_for('main.dashboard'))
    else:
        flash("Por favor, faça login para continuar.", "warning")
        
    return render_template('login.html')


@main.route('/logout')
def logout():
    """
    NOVA ROTA: Rota para fazer logout do usuário, limpando a sessão.
    """
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for('main.login'))
    
@main.route('/index')
def index():
    """
    ROTA ATUALIZADA: Funciona como o painel de gerenciamento de professores.
    Busca professores e disciplinas do banco de dados.
    """
    if 'user_id' not in session:
        flash("Faça login para continuar.", "warning")
        return redirect(url_for('main.login'))

    # Busca apenas usuários com o cargo de Professor
    professores = Usuarios.query.join(Cargos).filter(Cargos.nome_cargo == 'Professor').all()
    disciplinas = Disciplinas.query.order_by(Disciplinas.nome).all()
    
    return render_template('index.html', professores=professores, disciplinas=disciplinas)

@main.route('/adicionar_professor', methods=['POST'])
def adicionar_professor():
    """
    ROTA ATUALIZADA: Salva um novo professor no banco de dados, associando disciplinas.
    """
    if 'user_id' not in session:
        flash("Ação não autorizada.", "danger")
        return redirect(url_for('main.login'))
    
    nome = request.form.get('nome')
    email = request.form.get('email')
    materias_ids = request.form.getlist('materias')  # Pega lista de IDs das disciplinas selecionadas

    cargo_prof = Cargos.query.filter_by(nome_cargo='Professor').first()
    novo_professor = Usuarios(
        nome=nome,
        email=email,
        senha=generate_password_hash("senha_padrao123"),
        id_cargo=cargo_prof.id
    )
    db.session.add(novo_professor)
    db.session.commit()

    # Associa as disciplinas selecionadas ao professor
    for id_disciplina in materias_ids:
        disciplina = Disciplinas.query.filter_by(nome=id_disciplina).first()
        if disciplina:
            assoc = ProfessoresDisciplinas(id_professor=novo_professor.id, id_disciplina=disciplina.id)
            db.session.add(assoc)
       
    db.session.commit()

    flash("Professor adicionado com sucesso!", "success")
    return redirect(url_for('main.index'))

@main.route('/editar_professor/<int:usuario_id>', methods=['GET', 'POST'])
def editar_professor(usuario_id):
    """
    ROTA ATUALIZADA: Busca e atualiza um professor no banco de dados.
    """
    professor = Usuarios.query.get_or_404(usuario_id)
    
    if request.method == 'POST':
        professor.nome = request.form.get('nome')
        # Adicione aqui a lógica para atualizar disciplinas e disponibilidade
        db.session.commit()
        flash("Professor atualizado com sucesso!", "success")
        return redirect(url_for('main.index'))

    disciplinas = Disciplinas.query.order_by(Disciplinas.nome).all()
    return render_template('edit_teacher.html', professor=professor, disciplinas=disciplinas)


@main.route('/excluir_professor/<int:usuario_id>')
def excluir_professor(usuario_id):
    """
    ROTA ATUALIZADA: Exclui um professor do banco de dados.
    """
    professor = Usuarios.query.get_or_404(usuario_id)
    db.session.delete(professor)
    db.session.commit()
    flash("Professor excluído com sucesso.", "danger")
    return redirect(url_for('main.index'))


@main.route('/grade_horaria')
def grade_horaria():
    """
    ROTA MANTIDA: A lógica interna de gerar_grade_horaria() precisa ser
    adaptada para ler os dados do banco, não de um JSON.
    """
    # TODO: Refatorar 'gerar_grade_horaria' para usar o DB
    resultado = gerar_grade_horaria()
    return render_template('grid_schedule.html', grade=resultado)




@main.route('/lista_professores', methods=['GET', 'POST'])
def lista_professores():
    return 'lista de professores'
