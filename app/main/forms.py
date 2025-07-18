from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, EmailField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, Email
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed

class CadastroInstituicaoForm(FlaskForm):
    instituicao = StringField('Instituição', validators=[DataRequired(), Length(max=100)])
    cnpj = StringField('CNPJ', validators=[DataRequired(), Length(max=18)])
    endereco = StringField('Endereço', validators=[DataRequired()])
    numero = StringField('Número', validators=[DataRequired()])
    bairro = StringField('Bairro', validators=[DataRequired()])
    cidade = StringField('Cidade', validators=[DataRequired()])
    uf = SelectField('UF', choices=[
        ('', 'UF...'), ('AC', 'AC'), ('AL', 'AL'), ('AP', 'AP'), ('AM', 'AM'),
        ('BA', 'BA'), ('CE', 'CE'), ('DF', 'DF'), ('ES', 'ES'), ('GO', 'GO'),
        ('MA', 'MA'), ('MT', 'MT'), ('MS', 'MS'), ('MG', 'MG'), ('PA', 'PA'),
        ('PB', 'PB'), ('PR', 'PR'), ('PE', 'PE'), ('PI', 'PI'), ('RJ', 'RJ'),
        ('RN', 'RN'), ('RS', 'RS'), ('RO', 'RO'), ('RR', 'RR'), ('SC', 'SC'),
        ('SP', 'SP'), ('SE', 'SE'), ('TO', 'TO')
    ])
    cep = StringField('CEP', validators=[DataRequired()])
    telefone = StringField('Telefone', validators=[DataRequired()])
    email = EmailField('E-mail', validators=[DataRequired(), Email()])
    rede_ensino = StringField('Rede de Ensino', validators=[DataRequired()])
    categoria = SelectField('Categoria', choices=[('Pública', 'Pública'), ('Privada', 'Privada')])

    diretor_nome = StringField('Nome do Diretor', validators=[DataRequired()])
    diretor_cpf = StringField('CPF', validators=[DataRequired(), Length(min=11, max=14)])
    diretor_rg = StringField('RG', validators=[DataRequired()])
    diretor_sexo = RadioField('Sexo', choices=[('Masculino', 'Masculino'), ('Feminino', 'Feminino')], validators=[DataRequired()])
    diretor_telefone = StringField('Telefone', validators=[DataRequired()])
    diretor_endereco = StringField('Endereço', validators=[DataRequired()])

    prof_nome = StringField("Nome")
    prof_cpf = StringField("CPF")
    prof_rg = StringField("RG")
    prof_funcao = SelectField("Função", choices=[("professor", "Professor"), ("coordenador", "Coordenador")])
    prof_disciplina = StringField("Disciplina ou Área")
    prof_telefone = StringField("Telefone")

    submit = SubmitField('Cadastrar-se')
    
class MateriaForm(FlaskForm):
    nome = StringField('Nome da Matéria', validators=[DataRequired()])
    area = SelectField('Área',
        choices=[
            ('exatas', 'Ciências Exatas'),
            ('humanas', 'Ciências Humanas'),
            ('biologicas', 'Ciências Biológicas'),
            ('tecnicas', 'Matérias Técnicas')
        ],
        validators=[DataRequired()]
    )
    arquivo = FileField('Arquivo', validators=[FileAllowed(['pdf', 'doc', 'docx'])])
    submit = SubmitField('Adicionar')