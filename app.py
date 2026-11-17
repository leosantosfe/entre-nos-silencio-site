from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///abrigo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    autor = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    abracos = db.Column(db.Integer, default=0)
    comentarios = db.relationship("Comentario", backref="post", lazy=True)

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
        
    filtro = request.args.get("categoria")
    if filtro:
        posts = Post.query.filter_by(categoria=filtro).order_by(Post.id.desc()).all()
    else:
        posts = Post.query.order_by(Post.id.desc()).all()
        
    return render_template("index.html", posts=posts, filtro_atual=filtro)

@app.route("/blog", methods=["GET", "POST"])
def blog():
    if request.method == "POST":
        senha = request.form.get("senha")
        # Senha simples para só você poder publicar artigos no blog
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
