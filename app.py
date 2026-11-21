import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Conecta ao banco permanente na nuvem
database_url = os.environ.get("DATABASE_URL")
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    db_path = os.path.join("/tmp", "abrigo.db") if os.path.exists("/tmp") else "abrigo.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    autor = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    abracos = db.Column(db.Integer, default=0)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    comentarios = db.relationship("Comentario", backref="post", lazy=True, cascade="all, delete-orphan")

class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    autor = db.Column(db.String(100), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)

class Artigo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    indicacao_texto = db.Column(db.String(200), nullable=True)
    indicacao_link = db.Column(db.String(500), nullable=True)

with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        autor = request.form.get("autor") or "Anônimo"
        categoria = request.form.get("categoria")
        texto = request.form.get("texto")
        
        if texto:
            novo_post = Post(autor=autor, categoria=categoria, texto=texto)
            db.session.add(novo_post)
            db.session.commit()
        return redirect(url_for("index"))
        
    limite_48h = datetime.utcnow() - timedelta(hours=48)
    query = Post.query.filter(Post.criado_em >= limite_48h)
    
    filtro = request.args.get("categoria")
    if filtro:
        posts = query.filter_by(categoria=filtro).order_by(Post.id.desc()).all()
    else:
        posts = query.order_by(Post.id.desc()).all()
        
    return render_template("index.html", posts=posts, filtro_atual=filtro)

@app.route("/blog", methods=["GET", "POST"])
def blog():
    if request.method == "POST":
        senha = request.form.get("senha")
        if senha == "abrigo123":
            titulo = request.form.get("titulo")
            conteudo = request.form.get("conteudo")
            indicacao_texto = request.form.get("indicacao_texto")
            indicacao_link = request.form.get("indicacao_link")
            
            if titulo and conteudo:
                novo_artigo = Artigo(
                    titulo=titulo,
                    conteudo=conteudo,
                    indicacao_texto=indicacao_texto,
                    indicacao_link=indicacao_link
                )
                db.session.add(novo_artigo)
                db.session.commit()
        return redirect(url_for("blog"))

    artigos = Artigo.query.order_by(Artigo.id.desc()).all()
    return render_template("blog.html", artigos=artigos)

@app.route("/abracar/<int:post_id>", methods=["POST"])
def abracar(post_id):
    post = Post.query.get_or_404(post_id)
    post.abracos += 1
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/comentar/<int:post_id>", methods=["POST"])
def comentar(post_id):
    autor = request.form.get("autor") or "Anônimo"
    texto = request.form.get("texto")
    if texto:
        novo_comentario = Comentario(autor=autor, texto=texto, post_id=post_id)
        db.session.add(novo_comentario)
        db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
