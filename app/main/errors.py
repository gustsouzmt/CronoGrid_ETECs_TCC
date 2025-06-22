'''

from flask import render_template, current_app
from . import main

@main.app_errorhandler(400)
def bad_request(e):
    current_app.logger.error(f'Erro 400: {e}')
    return render_template('400.html'), 400

@main.app_errorhandler(404)
def page_not_found(e):
    current_app.logger.error(f'Erro 404: {e}')
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    current_app.logger.error(f'Erro 500: {e}')
    return render_template('500.html'), 500

'''
