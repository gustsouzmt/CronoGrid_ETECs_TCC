from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, EmailField, SubmitField
from wtforms.validators import DataRequired, Length, Email

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
    diretor_cpf = StringField('CPF', validators=[DataRequired()])
    diretor_rg = StringField('RG', validators=[DataRequired()])
    diretor_sexo = StringField('Sexo', validators=[DataRequired()])
    diretor_telefone = StringField('Telefone', validators=[DataRequired()])
    diretor_endereco = StringField('Endereço', validators=[DataRequired()])

    submit = SubmitField('Cadastrar-se')
