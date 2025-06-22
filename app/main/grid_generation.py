import pulp
import json

# Carrega os dados dos professores
def carregar_professores():
    with open('professores.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Define as cargas horárias das matérias
CARGA_HORARIA = {
    "Matemática": 5,
    "Português": 5,
    "Física": 3,
    "Química": 3,
    "Biologia": 3,
    "História": 2,
    "Geografia": 2,
    "Inglês": 2,
    "Educação Física": 2,
    "Filosofia": 2,
    "Sociologia": 1
}

# Dias da semana, turnos e aulas por dia
DIAS = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
TURNOS = ['manha', 'tarde', 'noite']
AULAS_POR_DIA = 6

def gerar_grade_horaria():
    professores = carregar_professores()

    # Cria o problema de otimização
    prob = pulp.LpProblem("Grade_Horaria_3_turmas", pulp.LpMinimize)

    # Variáveis de decisão: x[p,d,a,t] = 1 se professor p dá aula no dia d, aula a, turno t
    variaveis = pulp.LpVariable.dicts(
        "aula",
        [(p['id'], d, a, t) for p in professores for d in DIAS for a in range(AULAS_POR_DIA) for t in TURNOS],
        cat='Binary'
    )

    # Variável de folga para permitir relaxar restrições se necessário
    folga = pulp.LpVariable("folga", lowBound=0, cat='Continuous')
    prob += folga  # Objetivo: minimizar a folga

    # Restrição: Cada aula em cada dia e turno pode ter no máximo um professor
    for d in DIAS:
        for a in range(AULAS_POR_DIA):
            for t in TURNOS:
                prob += pulp.lpSum(
                    variaveis[(p['id'], d, a, t)]
                    for p in professores
                    if p['disponibilidade'][d][t]
                ) <= 1 + folga

    # Restrição: Cada matéria deve ter sua carga horária atendida para cada turma (turno)
    for t in TURNOS:
        for materia, carga in CARGA_HORARIA.items():
            prob += pulp.lpSum(
                variaveis[(p['id'], d, a, t)]
                for p in professores if materia in p['materias']
                for d in DIAS if p['disponibilidade'][d][t]
                for a in range(AULAS_POR_DIA)
            ) >= carga - folga

    # Restrição: Professor só pode dar aula se estiver disponível naquele dia e turno
    for p in professores:
        for d in DIAS:
            for t in TURNOS:
                if not p['disponibilidade'][d][t]:
                    for a in range(AULAS_POR_DIA):
                        prob += variaveis[(p['id'], d, a, t)] == 0

    # Restrição: Professor não pode dar mais de uma aula por dia e turno
    for p in professores:
        for d in DIAS:
            for t in TURNOS:
                prob += pulp.lpSum(
                    variaveis[(p['id'], d, a, t)]
                    for a in range(AULAS_POR_DIA)
                ) <= 1 + folga

    # Resolve o problema
    prob.solve(pulp.PULP_CBC_CMD(msg=True))

    # Processa a solução
    if pulp.LpStatus[prob.status] == 'Optimal':
        grade = {t: {d: {a: None for a in range(AULAS_POR_DIA)} for d in DIAS} for t in TURNOS}
        professores_dict = {p['id']: p for p in professores}

        for (pid, d, a, t), var in variaveis.items():
            if var.varValue > 0.5:
                professor = professores_dict[pid]
                # Seleciona a primeira matéria do professor que faz parte da carga horária
                for materia in professor['materias']:
                    if materia in CARGA_HORARIA:
                        grade[t][d][a] = {
                            'materia': materia,
                            'professor': professor['nome']
                        }
                        break

        return {
            'status': 'success',
            'grade': grade,
            'folga': folga.varValue
        }
    else:
        return {
            'status': 'infeasible',
            'message': 'Não foi possível encontrar uma solução viável com as restrições atuais.'
        }

def formatar_grade(grade):
    if grade['status'] != 'success':
        return grade['message']

    resultado = []
    for t in TURNOS:
        resultado.append(f"\nTurno: {t.capitalize()}")
        for dia, aulas in grade['grade'][t].items():
            resultado.append(f"  {dia}:")
            for num_aula, aula in aulas.items():
                if aula:
                    resultado.append(f"    Aula {num_aula + 1}: {aula['materia']} - Prof. {aula['professor']}")
                else:
                    resultado.append(f"    Aula {num_aula + 1}: Vaga")

    resultado.append(f"\nFolga total: {grade['folga']}")
    return "\n".join(resultado)

if __name__ == '__main__':
    grade = gerar_grade_horaria()
    print(formatar_grade(grade))
