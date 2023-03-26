from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text


app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.secret_key = '9Kd2O27rAQKz'

db = SQLAlchemy(app)

class Usuarios(db.Model):
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150))
    password = db.Column(db.String(150))

    def __int__(self, username, password):
        self.username = username
        self.password = password

@app.route('/', methods=['GET', 'POST'])
def index():
    username = ''
    if 'username' in session:
        username = session['username']
        return redirect(url_for('painel'))
    else:
        return render_template('index.html', username=username)


@app.route('/logar', methods=['POST'])
def logar():
    user = request.form['user']
    achar_user = text(f"SELECT username FROM usuarios WHERE username LIKE '{user}'")
    usuario = db.session.execute(achar_user).fetchone()
    if usuario is not None:
        achar_password = text(f"SELECT password FROM usuarios WHERE username LIKE '{user}'")
        usuario = usuario[0]
        senha = db.session.execute(achar_password).fetchone()[0]
        if usuario == request.form['user'] and senha == request.form['senha']:
            session['username'] = request.form['user']
            usuarios_gerais = Usuarios.query.all()
            return render_template('painel.html', username=request.form['user'], usuarios=usuarios_gerais)
        else:
            msg = "Usuario ou senha invalido"
            return render_template('login.html', msg=msg, msg_like='')
    else:
        msg = "Usuário inexistente!"
        return render_template('login.html', msg=msg, msg_like='')


@app.route('/registrar', methods=['POST'])
def registrar():
    user = request.form['user']
    achar_user = text(f"SELECT username FROM usuarios WHERE username LIKE '{user}'")
    usuario = db.session.execute(achar_user).fetchone()
    if usuario is not None:
        msg = "O usuario informado ja está em uso."
        return render_template('register.html', msg=msg)
    else:
        usuario_novo = Usuarios(username=request.form['user'], password=request.form['senha'])
        db.session.add(usuario_novo)
        db.session.commit()
        msg_like = ("Você foi cadastrado com sucesso!", "Realize seu login abaixo!")
        return render_template('login.html', msg_like=msg_like)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg_like=('', '')
    return render_template('login.html', msg_like=msg_like)

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route('/painel')
def painel():
    username = ''
    if 'username' in session:
        username = session['username']
        if username == 'admin':
            usuarios_gerais = Usuarios.query.all()
            return render_template('painel.html', username=username, usuarios=usuarios_gerais)
        else:
            return render_template('painel.html', username=username)
    else:
        return render_template('index.html', username=username)

@app.route('/delete/<int:id>')
def delete(id):
    usuario = Usuarios.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('painel'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    usuario = Usuarios.query.get(id)
    if request.method == 'POST':
        usuario.username = request.form['user']
        usuario.password = request.form['senha']
        db.session.commit()
        return redirect(url_for('painel'))
    return render_template('editar.html', usuario=usuario)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)