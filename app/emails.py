from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail # Importa a instância 'mail' do __init__.py

def send_async_email(app, msg):
    """
    Função que roda em background para enviar o email.
    Precisa do 'app_context' para acessar as configurações do app.
    """
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    """
    Função principal para enviar emails.
    'to': Destinatário
    'subject': Assunto
    'template': Nome do arquivo de template (ex: 'email/boas_vindas') sem o .html
    'kwargs': Variáveis para passar para o template (ex: user=usuario)
    """
    # Pega a aplicação atual para usar na thread
    app = current_app._get_current_object()
    
    # Cria a mensagem de email
    msg = Message(
        subject=f"[Seu Projeto] {subject}",
        sender=app.config['MAIL_SENDER'], # Configurado em config.py
        recipients=[to]
    )
    
    # Renderiza o corpo do email usando templates HTML e de texto puro
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    
    # Inicia a thread para enviar o email de forma assíncrona
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    
    return thr