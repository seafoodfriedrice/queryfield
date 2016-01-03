import os

from flask import Flask
from flask import render_template, flash, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from wtforms.fields import FormField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms_alchemy import ModelForm, ModelFormField, model_form_factory


app = Flask(__name__)

with app.app_context():

    uri = "postgresql://p:p@localhost:5433/queryfield"
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = os.urandom(24)

    db = SQLAlchemy(app)


    class Status(db.Model):
        __tablename__ = "status"
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(32))

        def __unicode__(self):
            return self.name

        def __repr__(self):
            return "<Status {!r}>".format(self.name)


    class ProviderType(db.Model):
        __tablename__ = "provider_types"
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(64))

        providers = db.relationship('Provider', backref='provider_type')

        def __repr__(self):
            return "<ProviderType {!r}>".format(self.name)


    class Provider(db.Model):
        __tablename__ = "providers"
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(64))
        provider_type_id = db.Column(db.Integer,
                                     db.ForeignKey('provider_types.id'))

        provider_accounts = db.relationship('ProviderAccount',
                                            backref='provider')

        def __unicode__(self):
            return self.name

        def __repr__(self):
            return "<Provider {!r}>".format(self.name)


    class ProviderAccount(db.Model):
        __tablename__ = "provider_accounts"
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(128))
        password = db.Column(db.String(128))
        provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'))

        servers = db.relationship('Server', backref='provider_account')

        def __repr__(self):
            return "<ProviderAccount {!r}>".format(self.username)


    class Server(db.Model):
        __tablename__ = "servers"
        id = db.Column(db.Integer, primary_key=True)
        ip = db.Column(db.String(24), unique=True)
        status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
        provider_account_id = db.Column(db.Integer,
                                        db.ForeignKey('provider_accounts.id'))

        def __repr__(self):
            return "<Server {!r}>".format(self.ip)


    BaseModelForm = model_form_factory(Form, strip_string_fields=True)

    class ModelForm(BaseModelForm):
        @classmethod
        def get_session(self):
            return db.session


    def status():
        return Status.query

    def providers():
        return Provider.query

    def provider_types():
        return ProviderType.query


    class StatusForm(ModelForm):
        class Meta:
            model = Status


    class ProviderTypeForm(ModelForm):
        class Meta:
            model = ProviderType


    class ProviderForm(ModelForm):
        class Meta:
            model = Provider

        provider_type = QuerySelectField(query_factory=provider_types)


    class ProviderAccountForm(ModelForm):
        class Meta:
            model = ProviderAccount

        provider = QuerySelectField(query_factory=providers)


    class ServerForm(ModelForm):
        class Meta:
            model = Server

        status = QuerySelectField(query_factory=status)
        provider_account = ModelFormField(ProviderAccountForm)


    def flash_errors(form):
        for field, errors in form.errors.items():
            for error in errors:
                flash(u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                ))


    @app.route('/', methods=["GET", "POST"])
    def add_server():
        server = Server()
        form = ServerForm()
        if form.validate_on_submit():
            form.populate_obj(server)
            db.session.add(server)
            db.session.commit()
            flash("Added {}".format(server.ip))
            return redirect(url_for("get_server", id=server.id))
        else:
            flash_errors(form)
        return render_template("add_server.html", form=form)

    @app.route('/<int:id>', methods=["GET", "POST"])
    def get_server(id):
        server = Server.query.get(id)
        form = ServerForm(obj=server)
        if form.validate_on_submit():
            form.populate_obj(server)
            db.session.add(server)
            db.session.commit()
            flash("Success.")
            return redirect(url_for("get_server", id=server.id))
        else:
            flash_errors(form)
        return render_template("get_server.html", form=form, id=server.id)


if __name__ == '__main__':
    app.run()
