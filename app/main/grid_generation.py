"""
grid_generation.py

Integra a lógica de Programação Linear (PuLP) adaptada do seu script de terminal
para o contexto Flask + SQLAlchemy.

Principais funções exportadas:
- gerar_grade_horaria(turmas_cargas=None, ano_letivo=2025, semestre=1)
    -> Gera as grades para as turmas fornecidas (ou as criadas via popular_dados_iniciais),
       resolve LPs e grava em GradeHorariaAlocacoes. Retorna dict de resultados.

- popular_dados_iniciais()
    -> (Opcional) Popula o banco com disciplinas, turmas, professores fictícios e slots.
       Útil para testes. Não sobrescreve registros existentes com o mesmo identificador/nome.

Notas:
- Ajuste pesos, pontuações e restrições conforme suas regras de negócio.
- Requer a lib PuLP instalada (pip install pulp).
"""

from .. import db
from .models import (
    Usuarios, Cargos, Disciplinas, ProfessoresDisciplinas,
    Turmas, Salas, AlunosHorarios, DisponibilidadeProfessores,
    GradeHorariaAlocacoes
)
import pulp
from sqlalchemy import and_, func
from datetime import time

DEFAULT_PROF_SCORE = 7

# ---------- HELPERS ----------

def _get_professores_do_bd():
    """Retorna lista de dicionários com info dos professores presentes no BD."""
    # busca cargo 'Professor'
    cargo = Cargos.query.filter_by(nome_cargo='Professor').first()
    if not cargo:
        return []

    prof_users = Usuarios.query.filter(Usuarios.id_cargo == cargo.id).all()
    professores = []
    for u in prof_users:
        # disciplínas que esse professor leciona (via ProfessoresDisciplinas)
        pd_rows = ProfessoresDisciplinas.query.filter_by(id_professor=u.id).all()
        disciplinas = []
        for pd in pd_rows:
            disc = Disciplinas.query.get(pd.id_disciplina)
            if disc:
                disciplinas.append(disc.nome)

        # disponibilidade: mapear slots -> dic[dia][slotNumber] = 1/0
        dispon = {}
        disp_rows = DisponibilidadeProfessores.query.filter_by(id_professor=u.id, disponivel=True).all()
        for dr in disp_rows:
            slot = AlunosHorarios.query.get(dr.id_slot_horario)
            if not slot:
                continue
            dia = slot.dia_semana
            # tenta extrair um token curto da descricao: '1', 'N1', etc.
            token = None
            if slot.descricao:
                token = slot.descricao.strip()
            else:
                token = str(slot.id_slot_horario)
            if dia not in dispon:
                dispon[dia] = {}
            # marca disponível no token
            dispon[dia][token] = 1

        # pontuação (se existir atributo, senão valor default)
        pont = getattr(u, 'pontuacao', None)
        if pont is None:
            pont = DEFAULT_PROF_SCORE

        professores.append({
            'id': f'P_{u.id}',  # id string usado internamente
            'db_id': u.id,      # id no banco
            'nome': u.nome,
            'disciplinas': disciplinas,
            'pontuacao': pont,
            'disp': dispon
        })
    return professores

def _map_slots_for_horarios(horarios_dia, dias):
    """
    Monta uma lista de tokens de slot (por exemplo '1','2',...,'N1',...) com base em AlunosHorarios.
    Retorna dict: {dia: [list of slot tokens sorted by horario_inicio]}.
    """
    mapa = {}
    for d in dias:
        rows = AlunosHorarios.query.filter_by(dia_semana=d).order_by(AlunosHorarios.horario_inicio).all()
        if not rows:
            mapa[d] = [str(s) for s in horarios_dia]  # fallback numérico
            continue
        tokens = []
        for r in rows:
            tokens.append(r.descricao if r.descricao else str(r.id_slot_horario))
        mapa[d] = tokens
    return mapa

def _find_slot_id_by_token(token, dia):
    """Procura id_slot_horario com descricao LIKE token e dia_semana == dia."""
    row = AlunosHorarios.query.filter(and_(
        AlunosHorarios.dia_semana == dia,
        AlunosHorarios.descricao.ilike(f'%{token}%')
    )).first()
    if row:
        return row.id_slot_horario
    # fallback: search by exact descricao
    row2 = AlunosHorarios.query.filter(and_(
        AlunosHorarios.dia_semana == dia,
        AlunosHorarios.descricao == token
    )).first()
    if row2:
        return row2.id_slot_horario
    return None

# ---------- PRINCIPAL: GERAR GRADE ----------

def gerar_grade_horaria(turmas_cargas=None, ano_letivo=2025, semestre=1):
    """
    Gera grades para as turmas especificadas e grava alocações em GradeHorariaAlocacoes.
    - turmas_cargas: dict opcional com mapeamento { "NOME TURMA": { "DISCIPLINA": carga, ... }, ... }
      Se None, tenta usar os dados inseridos por popular_dados_iniciais().
    Retorna dict com resultados por turma.
    """
    resultados = {}

    # dias fixos (padrão do seu script)
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

    # Carrega dados do BD
    professores = _get_professores_do_bd()
    salas = Salas.query.all()
    salas_ids = [s.id for s in salas] if salas else []

    # Se turmas_cargas não foi fornecido, tenta criar a partir de Turmas & Disciplinas.carga_horaria_semanal
    if turmas_cargas is None:
        turmas_cargas = {}
        turmas_db = Turmas.query.all()
        # Observação: não existe relação direta turmas->disciplinas no schema; usamos todas as disciplinas com carga_horaria_semanal setada
        disciplinas_all = Disciplinas.query.filter(Disciplinas.carga_horaria_semanal != None).all()
        for t in turmas_db:
            # por falta de relação, tentamos atribuir todas as disciplinas com carga definida (isso é apenas um fallback)
            if disciplinas_all:
                turmas_cargas[t.nome] = {d.nome: d.carga_horaria_semanal for d in disciplinas_all}
            else:
                turmas_cargas[t.nome] = {}
    # Agora iteramos por cada turma e resolvemos o PL similar ao seu script
    for nome_turma, disciplinas in turmas_cargas.items():
        # determina horarios por turma usando heurística: busca campo Turmas.periodo (se existir correspondência)
        turma_row = Turmas.query.filter_by(nome=nome_turma).first()
        if turma_row and turma_row.periodo:
            periodo = turma_row.periodo.lower()
        else:
            periodo = 'integral'

        # define horários_dia e max_aulas com base no periodo
        horarios_integral = list(range(1,9))
        horarios_manha = list(range(1,7))
        horarios_noite = list(range(1,6))
        if 'noite' in periodo or 'n' in periodo and 'noite' in periodo:
            horarios_dia = horarios_noite
            max_aulas_dia = 5
        elif 'manha' in periodo or 'manhã' in periodo or 'matutino' in periodo:
            horarios_dia = horarios_manha
            max_aulas_dia = 6
        elif 'integral' in periodo or 'integral' == periodo:
            horarios_dia = horarios_integral
            max_aulas_dia = None  # variável
        else:
            horarios_dia = horarios_integral
            max_aulas_dia = None

        # Mapeia tokens de slots a partir de AlunosHorarios (fallback para números simples)
        mapa_slots = _map_slots_for_horarios(horarios_dia, dias)

        # monta prof_ids_disc local (professores que podem lecionar cada disciplina)
        prof_ids_disc = {}
        for disc in disciplinas.keys():
            prof_ids_disc[disc] = [p['id'] for p in professores if disc in [d.upper() for d in p['disciplinas']] or disc.upper() in [d.upper() for d in p['disciplinas']]]
            # se nenhum professor encontrado para a disciplina, tentamos correspondência parcial
            if len(prof_ids_disc[disc]) == 0:
                for p in professores:
                    for pd in p['disciplinas']:
                        if pd and pd.upper() in disc.upper():
                            prof_ids_disc[disc].append(p['id'])
            if len(prof_ids_disc[disc]) == 0:
                # ainda vazio -> log e cria vazio
                print(f"AVISO: nenhum professor para disciplina '{disc}' na turma '{nome_turma}'")

        # conjunto de professores envolvidos
        prof_ids = set(pid for proflist in prof_ids_disc.values() for pid in proflist)

        # criar variáveis binárias A[d][h][disc][pid]
        prob = pulp.LpProblem(f"Grade_{nome_turma}", pulp.LpMaximize)
        A = {}
        for d in dias:
            A[d] = {}
            for h in mapa_slots.get(d, horarios_dia):
                A[d][h] = {}
                for disc in disciplinas.keys():
                    A[d][h][disc] = {}
                    for pid in prof_ids_disc.get(disc, []):
                        varname = f"A_{d}_{h}_{disc}_{pid}".replace(' ', '_')
                        A[d][h][disc][pid] = pulp.LpVariable(varname, cat='Binary')

        # slack por disciplina (inteiro)
        slack = {disc: pulp.LpVariable(f"Slack_{disc}".replace(' ', '_'), lowBound=0, cat='Integer') for disc in disciplinas.keys()}

        big_penalty = 1000

        # Objetivo: maximizar soma de pontuações menos penalidade por slack
        prob += (
            pulp.lpSum(
                A[d][h][disc][pid] * next((p['pontuacao'] for p in professores if p['id'] == pid), DEFAULT_PROF_SCORE)
                for d in dias for h in mapa_slots.get(d, horarios_dia) for disc in disciplinas.keys() for pid in prof_ids_disc.get(disc, [])
            ) - pulp.lpSum(slack[disc] * big_penalty for disc in disciplinas.keys())
        )

        # 1) atender carga horária por disciplina (considerando slack)
        for disc, carga in disciplinas.items():
            prob += (
                pulp.lpSum(
                    A[d][h][disc][pid]
                    for d in dias for h in mapa_slots.get(d, horarios_dia) for pid in prof_ids_disc.get(disc, [])
                ) + slack[disc] == carga
            )

        # 2) um professor só pode dar uma aula por horário
        for d in dias:
            for h in mapa_slots.get(d, horarios_dia):
                for pid in prof_ids:
                    prob += (
                        pulp.lpSum(
                            A[d][h][disc][pid]
                            for disc in disciplinas.keys() if pid in prof_ids_disc.get(disc, [])
                        ) <= 1
                    )

        # 3) cada horário/dia só pode ter no máximo uma aula para a turma
        for d in dias:
            for h in mapa_slots.get(d, horarios_dia):
                prob += (
                    pulp.lpSum(
                        A[d][h][disc][pid]
                        for disc in disciplinas.keys() for pid in prof_ids_disc.get(disc, [])
                    ) <= 1
                )

        # 4) só escalar professor disponível no dia/horário
        for d in dias:
            for h in mapa_slots.get(d, horarios_dia):
                for disc in disciplinas.keys():
                    for pid in prof_ids_disc.get(disc, []):
                        prof = next(p for p in professores if p['id'] == pid)
                        # se não há marcação de disponibilidade para o dia/slot assume indisponível (conservador)
                        dispon = prof['disp'].get(d, {})
                        # h pode ser token tipo 'N1' ou '1' etc.
                        if isinstance(h, int):
                            token = str(h)
                        else:
                            token = str(h)
                        if dispon.get(token, 0) == 0:
                            prob += A[d][h][disc][pid] == 0

        # 5) limite máximo de aulas por dia (se especificado)
        if max_aulas_dia:
            for d in dias:
                prob += (
                    pulp.lpSum(
                        A[d][h][disc][pid]
                        for h in mapa_slots.get(d, horarios_dia) for disc in disciplinas.keys() for pid in prof_ids_disc.get(disc, [])
                    ) <= max_aulas_dia
                )

        # Resolver
        prob.solve(pulp.PULP_CBC_CMD(msg=0))

        # Montar grade e salvar alocações no BD
        grade = {d: {h: None for h in mapa_slots.get(d, horarios_dia)} for d in dias}
        faltantes = {}
        # antes de inserir, opcionalmente remover alocações antigas desta turma/ano/semestre
        turma_row = Turmas.query.filter_by(nome=nome_turma).first()
        if turma_row:
            GradeHorariaAlocacoes.query.filter_by(id_turma=turma_row.id, ano_letivo=ano_letivo, semestre=semestre).delete()
            db.session.commit()

        for d in dias:
            for h in mapa_slots.get(d, horarios_dia):
                for disc in disciplinas.keys():
                    for pid in prof_ids_disc.get(disc, []):
                        var = A[d][h][disc].get(pid)
                        if var and pulp.value(var) == 1:
                            prof = next(p for p in professores if p['id'] == pid)
                            prof_nome = prof['nome']
                            grade[d][h] = (disc, prof_nome)
                            # grava em GradeHorariaAlocacoes (precisa de ids reais)
                            if turma_row:
                                id_professor_db = prof['db_id']
                                # escolher sala: primeira disponível (pode melhorar)
                                id_sala = salas_ids[0] if salas_ids else None
                                # mapear slot token para id_slot_horario
                                slot_id = _find_slot_id_by_token(h, d)
                                if id_sala is not None and slot_id is not None:
                                    aloc = GradeHorariaAlocacoes(
                                        id_turma=turma_row.id,
                                        id_disciplina=(Disciplinas.query.filter_by(nome=disc).first().id if Disciplinas.query.filter_by(nome=disc).first() else None),
                                        id_professor=id_professor_db,
                                        id_sala=id_sala,
                                        id_slot_horario=slot_id,
                                        ano_letivo=ano_letivo,
                                        semestre=semestre
                                    )
                                    db.session.add(aloc)
                                else:
                                    # não salvou alocação por falta de sala/slot mapping; apenas registra no resultado
                                    pass

        # avaliar slack (faltantes)
        for disc in disciplinas.keys():
            val = pulp.value(slack[disc])
            if val and val > 0:
                faltantes[disc] = int(val)

        db.session.commit()
        resultados[nome_turma] = {
            'grade': grade,
            'faltantes': faltantes
        }

    return resultados

# ---------- POPULAR DADOS INICIAIS (OPCIONAL) ----------

def popular_dados_iniciais():
    """
    Popula o DB com dados de exemplo (disciplinas, turmas, professores, slots e salas).
    Não sobrescreve registros existentes com o mesmo nome/código.
    Use apenas para testes.
    """
    with db.session.no_autoflush:
        # 1) cargos
        cargo_prof = Cargos.query.filter_by(nome_cargo='Professor').first()
        if not cargo_prof:
            cargo_prof = Cargos(nome_cargo='Professor')
            db.session.add(cargo_prof)
            db.session.commit()

        # 2) algumas disciplinas de exemplo (baseadas no seu script)
        nomes_disciplinas = [
            'MATEMÁTICA','PORTUGUÊS','INGLÊS','FÍSICA','QUÍMICA','BIOLOGIA','HISTÓRIA','GEOGRAFIA',
            'ARTE','EDUCAÇÃO FÍSICA','PROGRAMAÇÃO WEB','BANCO DE DADOS','REDES DE COMPUTADORES'
        ]
        for nd in nomes_disciplinas:
            if not Disciplinas.query.filter_by(nome=nd).first():
                d = Disciplinas(nome=nd, codigo=nd[:10].upper(), carga_horaria_semanal=2)
                db.session.add(d)
        db.session.commit()

        # 3) turmas de exemplo (cria se não existir)
        turmas_ex = [
            ('1º MTEC PI - ADMINISTRAÇÃO_A', 2025, 'Integral'),
            ('3º MTEC - DS', 2025, 'Matutino'),
            ('1º MTEC-N - DS', 2025, 'Noturno'),
            ('3º TDT', 2025, 'Noturno')
        ]
        for nome, ano, periodo in turmas_ex:
            if not Turmas.query.filter_by(nome=nome).first():
                t = Turmas(nome=nome, ano_letivo=ano, periodo=periodo)
                db.session.add(t)
        db.session.commit()

        # 4) criar algumas salas
        if not Salas.query.first():
            s1 = Salas(nome='Sala 101', capacidade=40, tipo='Normal')
            s2 = Salas(nome='Sala 102', capacidade=30, tipo='Laboratório')
            db.session.add_all([s1, s2])
            db.session.commit()

        # 5) criar slots em alunos_horarios (Se não existirem)
        if AlunosHorarios.query.count() == 0:
            # matutino/tarde: 1..9
            horarios = [
                ('Segunda','07:30','08:20','1'),
                ('Segunda','08:20','09:10','2'),
                ('Segunda','09:10','10:00','3'),
                ('Segunda','10:20','11:10','4'),
                ('Segunda','11:10','12:00','5'),
                ('Segunda','12:00','12:50','6'),
                ('Segunda','12:50','13:40','7'),
                ('Segunda','13:40','14:40','8'),
                ('Segunda','14:40','15:30','9'),
            ]
            # cria para todos os dias
            dias = ['Segunda','Terça','Quarta','Quinta','Sexta']
            for d in dias:
                for token, inicio, fim, desc in [(t[3], t[1], t[2], t[3]) for t in horarios]:
                    # map by token to times (very approximate)
                    # create unique descricao like '1', '2', 'N1' etc.
                    # For simplicity times are placeholders; better to adapt
                    try:
                        h_start = time(int(inicio.split(':')[0]), int(inicio.split(':')[1]))
                        h_end = time(int(fim.split(':')[0]), int(fim.split(':')[1]))
                    except:
                        h_start = time(7,30)
                        h_end = time(8,20)
                    ah = AlunosHorarios(dia_semana=d, horario_inicio=h_start, horario_fim=h_end, descricao=desc)
                    db.session.add(ah)
            # Noturno tokens N1..N5
            noite_tokens = [('N1','18:10','19:00'),('N2','19:00','19:50'),('N3','19:50','20:40'),('N4','21:00','21:50'),('N5','21:50','22:40')]
            for d in dias:
                for tok, inicio, fim in noite_tokens:
                    try:
                        h_start = time(int(inicio.split(':')[0]), int(inicio.split(':')[1]))
                        h_end = time(int(fim.split(':')[0]), int(fim.split(':')[1]))
                    except:
                        h_start = time(18,10); h_end = time(19,0)
                    ah = AlunosHorarios(dia_semana=d, horario_inicio=h_start, horario_fim=h_end, descricao=tok)
                    db.session.add(ah)
            db.session.commit()

        # 6) criar professores fictícios e associar disciplinas e disponibilidades
        # Apenas cria alguns exemplos; não duplica por email
        exemplo_profs = [
            {'nome':'Ana CP','email':'ana.cp@example.com','disciplinas':['MATEMÁTICA']},
            {'nome':'Carla P','email':'carla.p@example.com','disciplinas':['PORTUGUÊS']},
            {'nome':'Eduardo GV','email':'eduardo.gv@example.com','disciplinas':['INGLÊS']},
            {'nome':'Zé C','email':'ze.c@example.com','disciplinas':['TEORIAS DA ADMINISTRAÇÃO']},
        ]
        from werkzeug.security import generate_password_hash
        for p in exemplo_profs:
            if not Usuarios.query.filter_by(email=p['email']).first():
                novo = Usuarios(nome=p['nome'], email=p['email'], senha=generate_password_hash('senha123'), id_cargo=cargo_prof.id)
                db.session.add(novo)
                db.session.commit()
                # vincular disciplinas (criar disciplina se não existir)
                for dname in p['disciplinas']:
                    drow = Disciplinas.query.filter_by(nome=dname).first()
                    if not drow:
                        drow = Disciplinas(nome=dname, codigo=dname[:10].upper(), carga_horaria_semanal=2)
                        db.session.add(drow)
                        db.session.commit()
                    # insere na tabela ProfessoresDisciplinas
                    pd = ProfessoresDisciplinas(id_professor=novo.id, id_disciplina=drow.id)
                    db.session.add(pd)
                db.session.commit()
                # marcar disponibilidade completa (todos slots existentes)
                slots = AlunosHorarios.query.all()
                for s in slots:
                    dispo = DisponibilidadeProfessores(id_professor=novo.id, id_slot_horario=s.id_slot_horario, disponivel=True, ano_letivo_referencia=2025)
                    db.session.add(dispo)
                db.session.commit()

    return "Dados iniciais populares (quando necessário)."

# ---------- FIM DO ARQUIVO ----------
