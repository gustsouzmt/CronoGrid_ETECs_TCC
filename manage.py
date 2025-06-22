from app import create_app, db
from app.main import models

app = create_app('default')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Cargo': models.Cargos, 'Usuário': models.Usuarios}

if __name__ == '__main__':
    app.run(debug=True)
