from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
#dans le terminal : 
#1)export de la variable d'env FLASK_APP=APP
#2) flask db init : pour créer dossier de migration
#3) ensuite commande > flask db migrate -m "Premiere migration"  (pour créer notre base)
#4) Mise a jour de la base : flask db upgrade

from donnees import donnees
from markupsafe import escape
import os 
from db_articles import liste_articles
from db_projets import liste_projets

N_PROJETS=3
N_ARTICLES=3
DOSSIER_UPLOAD = "static\\images"

app = Flask(__name__)

#configuration de db // prerequis = pip install -U Flask-SQLAlchemy=2.5.1
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app,db)  #pour la migration de notre modele

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(150))
    slug = db.Column(db.String(150))
    contenu = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Article[{self.id}] {self.titre}>"

class Projet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(150))
    slug = db.Column(db.String(150))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))

    def __repr__(self):
        return f"<Projet[{self.id}] {self.titre}>"

#URLs
@app.route("/")
def accueil():
    return render_template("index.html", projets=liste_projets[:N_PROJETS], articles=liste_articles[:N_ARTICLES])

@app.route("/projets/creer", methods=["GET", "POST"])
def creer_projet():
    if request.method== 'POST':
        titre = request.form['titre']
        slug = request.form['slug']
        description = request.form['description']
        fichier = request.files['fichier']
        # print(titre, slug, description, fichier.filename)

        image_url = f'static\\images\\thumb_small.png'
        if fichier.filename !='':
            # print(os.getcwd())
            image_url = f'static\\images\\{fichier.filename}'
            fichier.save(os.path.join(DOSSIER_UPLOAD, fichier.filename))
        #verifier que l'utilisateur est connecté
        projet = Projet(titre=titre, slug=slug, description=description, image_url=image_url)
        db.session.add(projet)
        db.session.commit()
        return redirect(url_for('projets'))
    return render_template("creer_projet.html")

@app.route("/projets/")
@app.route("/projets/<string:slug>")
def projets(slug=""):
    if slug:
        projet = Projet.query.filter_by(slug=slug).first_or_404()
        return render_template('projet.html', projet=projet)
    projets= Projet.query.all()
    return render_template("projets.html",projets=projets)

@app.route("/articles/creer", methods=["GET", "POST"])
def creer_article():
    if request.method== 'POST':
        titre = request.form['titre']
        slug = request.form['slug']
        contenu = request.form['contenu']
        # print(titre, slug, contenu)
        #verifier que l'utilisateur est connecté

        article = Article(titre=titre, slug=slug, contenu=contenu)
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('articles'))
    return render_template("creer_article.html")

@app.route("/articles/")
@app.route("/articles/<string:slug>")
def articles(slug=""):
    if slug:
        article = Article.query.filter_by(slug=slug).first_or_404()
        return render_template('article.html', article=article)
    articles= Article.query.order_by(Article.date.desc()).all()
    return render_template("articles.html",articles=articles)

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # print(username, password)
        return "<h1> Utilisateur connecté </h1>"
    return render_template("login.html")

@app.errorhandler(404)
def page_404(error):
    return render_template('404.html'), 404

@app.route("/jinja")
def jinja():
    return render_template("jinja.html", prenom = "Benois", afficher=False, utilisateurs=['Alex', 'Romaric', 'Benois'])