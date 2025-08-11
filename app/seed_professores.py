from app import create_app, db
from app.main.models import Usuarios, Disciplinas, ProfessoresDisciplinas, Cargos
from werkzeug.security import generate_password_hash

app = create_app()
app.app_context().push()

professores = [
    {"nome":"Ana CP", "disciplinas":["MATEMÁTICA"]},
    {"nome":"Bruno SM", "disciplinas":["MATEMÁTICA"]},
    {"nome":"Carla P", "disciplinas":["PORTUGUÊS"]},
    {"nome":"Daniel OT", "disciplinas":["PORTUGUÊS"]},
    {"nome":"Eduardo GV", "disciplinas":["INGLÊS"]},
    {"nome":"Fernando HC", "disciplinas":["INGLÊS"]},
    {"nome":"Gustavo R", "disciplinas":["FÍSICA"]},
    {"nome":"Helena JM", "disciplinas":["FÍSICA"]},
    {"nome":"Igor S", "disciplinas":["QUÍMICA"]},
    {"nome":"Juliana D", "disciplinas":["QUÍMICA"]},
    {"nome":"Kleber S", "disciplinas":["BIOLOGIA"]},
    {"nome":"Larissa S", "disciplinas":["BIOLOGIA"]},
    {"nome":"Marcelo C", "disciplinas":["HISTÓRIA"]},
    {"nome":"Natália F", "disciplinas":["GEOGRAFIA"]},
    {"nome":"Otavio M", "disciplinas":["FILOSOFIA"]},
    {"nome":"Pedro B", "disciplinas":["SOCIOLOGIA"]},
    {"nome":"Quirino A", "disciplinas":["ARTE"]},
    {"nome":"Renata P", "disciplinas":["EDUCAÇÃO FÍSICA"]},
    {"nome":"Sergio N", "disciplinas":["ADM. PROD. SERV"]},
    {"nome":"Tatiana C", "disciplinas":["PROC.LOG.EMP"]},
    {"nome":"Ulisses F", "disciplinas":["DES. AÇÕES MKT"]},
    {"nome":"Vanessa M", "disciplinas":["LEG. EMP"]},
    {"nome":"Wallace B", "disciplinas":["LEG. TRAB. PREV."]},
    {"nome":"Xavier L", "disciplinas":["EST. ADM. PÚBLICA"]},
    {"nome":"Yasmin C", "disciplinas":["ECONOMIA"]},
    {"nome":"Zé C", "disciplinas":["TEORIAS DA ADMINISTRAÇÃO"]},
    {"nome":"Alice M", "disciplinas":["MATEMÁTICA FINANCEIRA"]},
    {"nome":"Bernardo S", "disciplinas":["LIDERANÇA ORGANIZACIONAL"]},
    {"nome":"Caio C", "disciplinas":["PROGRAMAÇÃO WEB"]},
    {"nome":"Diana F", "disciplinas":["BANCO DE DADOS"]},
    {"nome":"Igor P", "disciplinas":["REDES DE COMPUTADORES"]},
    {"nome":"Wagner L", "disciplinas":["PW III"]},
    {"nome":"Ximena D", "disciplinas":["PAM II"]},
    {"nome":"Yuri C", "disciplinas":["QTS"]},
    {"nome":"Zilda A", "disciplinas":["SIST. EMBARCADOS"]},
    {"nome":"Arthur T", "disciplinas":["IPS"]},
    {"nome":"Bianca M", "disciplinas":["T.P.A"]},
    {"nome":"Claudio F", "disciplinas":["BD I"]},
    {"nome":"Denise C", "disciplinas":["DESEN. SISTEMAS"]},
    {"nome":"Elias R", "disciplinas":["PDTCC-DS"]},
    {"nome":"Fernanda T", "disciplinas":["PDTCCA"]},
    {"nome":"Guilherme L", "disciplinas":["ADM. RH"]},
    {"nome":"Hugo V", "disciplinas":["ADM. FIN E ORÇ."]},
    {"nome":"Isabela N", "disciplinas":["TEC. INFO. ADM"]},
    {"nome":"João P", "disciplinas":["CUSTOS CONTÁBEIS"]},
    {"nome":"Kelly A", "disciplinas":["LAB. MED. INT. SOC."]},
    {"nome":"Leonardo R", "disciplinas":["CPOC"]},
    {"nome":"Marta S", "disciplinas":["LEG. TRAB. PREV."]},
    {"nome":"Nicolas F", "disciplinas":["EST. A. LINGUAGENS"]},
    {"nome":"Olga S", "disciplinas":["PRÁTICAS EMP."]},
    {"nome":"Patricia R", "disciplinas":["LAB. PROC. CRIA."]},
    {"nome":"Ricardo L", "disciplinas":["EST. AVA. CH / SA"]},
    {"nome":"Silvia C", "disciplinas":["EST. AVANÇ. MAT."]},
    {"nome":"Tomas O", "disciplinas":["LAB. INV. CIEN."]},
    {"nome":"Veronica M", "disciplinas":["ALMOÇO"]},
    {"nome":"Willian C", "disciplinas":["LEG. EMP."]},
    {"nome":"Xuxa L", "disciplinas":["OP. CONT. COM."]},
    {"nome":"Yago F", "disciplinas":["PORDP"]},
    {"nome":"Zoraide C", "disciplinas":["EST. ECO. MER. E COM."]},
    {"nome":"Alan R", "disciplinas":["EST. ADM. PÚBLICA"]},
    {"nome":"Breno S", "disciplinas":["PORA"]},
    {"nome":"Clara G", "disciplinas":["ARTE"]},
    {"nome":"Douglas P", "disciplinas":["SOCIOLOGIA"]},
    {"nome":"Eliane S", "disciplinas":["ECO"]},
    {"nome":"Fabio M", "disciplinas":["PW II"]},
    {"nome":"Giovana R", "disciplinas":["BD II"]},
    {"nome":"Henrique L", "disciplinas":["BD III"]},
    {"nome":"Lucas T.", "disciplinas":["APLI. INFO."]},
    {"nome":"Marina S.", "disciplinas":["APLI. INFO."]},
    {"nome":"Paulo R.", "disciplinas":["DES. MOD. NEG."]},
    {"nome":"Sofia M.", "disciplinas":["DES. MOD. NEG."]},
    {"nome":"Renan F.", "disciplinas":["ORG. EMP. CONT. II"]},
    {"nome":"Clara D.", "disciplinas":["ORG. EMP. CONT. II"]},
    {"nome":"Gabriel N.", "disciplinas":["PROJ. INT. II"]},
    {"nome":"Beatriz L.", "disciplinas":["PROJ. INT. II"]},
    {"nome":"Carlos B.", "disciplinas":["EST. AVANÇ. MATEM"]},
    {"nome":"Fernanda K.", "disciplinas":["EST. AVANÇ. MATEM"]},
    {"nome":"Juliana A.", "disciplinas":["LEGISLAÇÃO TRABALHISTA"]},
    {"nome":"Ricardo V.", "disciplinas":["LEGISLAÇÃO TRABALHISTA"]},
    {"nome":"Eduardo M.", "disciplinas":["MATEMÁTICA APLICADA"]},
    {"nome":"Ana C.", "disciplinas":["MATEMÁTICA APLICADA"]},
]

# 1. Garante que o cargo Professor existe
cargo_prof = Cargos.query.filter_by(nome_cargo='Professor').first()
if not cargo_prof:
    cargo_prof = Cargos(nome_cargo='Professor')
    db.session.add(cargo_prof)
    db.session.commit()

# 2. Cria disciplinas se não existirem
def get_or_create_disciplina(nome):
    disciplina = Disciplinas.query.filter_by(nome=nome).first()
    if not disciplina:
        disciplina = Disciplinas(nome=nome)
        db.session.add(disciplina)
        db.session.commit()
    return disciplina

# 3. Adiciona professores e associa disciplinas
for prof in professores:
    # Evita duplicidade
    if Usuarios.query.filter_by(nome=prof["nome"], id_cargo=cargo_prof.id).first():
        continue
    novo_prof = Usuarios(
        nome=prof["nome"],
        email=f"{prof['nome'].replace(' ', '').replace('.', '').replace('ç','c').replace('ã','a').replace('é','e').replace('ê','e').replace('á','a').replace('í','i').replace('ó','o').replace('ú','u').replace('ô','o').replace('õ','o').replace('â','a').replace('ê','e').replace(' ','').lower()}@exemplo.com",
        senha=generate_password_hash("senha_padrao123"),
        id_cargo=cargo_prof.id,
        ativo=True
    )
    db.session.add(novo_prof)
    db.session.commit()

    # Associa disciplinas
    for nome_disc in prof["disciplinas"]:
        disciplina = get_or_create_disciplina(nome_disc)
        assoc = ProfessoresDisciplinas(id_professor=novo_prof.id, id_disciplina=disciplina.id)
        db.session.add(assoc)
    db.session.commit()

print("Professores e disciplinas inseridos com sucesso!")