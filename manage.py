from flask.ext.script import Manager
from queryfield import app, db
from queryfield import Status, StatusForm
from queryfield import ProviderType, ProviderTypeForm
from queryfield import Provider, ProviderForm
from queryfield import ProviderAccount, ProviderAccountForm
from queryfield import Server, ServerForm

manager = Manager(app)

@manager.command
def seed():
    for status in ['Active', 'Cancelled', 'Pending']:
        s = Status(name=status)
        db.session.add(s)
        db.session.commit()

    for provider_type in ['Server', 'Domain', 'Email']:
        t = ProviderType(name=provider_type)
        db.session.add(t)
        db.session.commit()

    for provider in ['Amazon', 'DigitalOcean', 'GoDaddy', 'Google']:
        p = Provider(name=provider)
        db.session.add(p)
        db.session.commit()

    a = Provider.query.filter_by(name='Amazon').first()
    d = Provider.query.filter_by(name='DigitalOcean').first()
    pt = ProviderType.query.filter_by(name='Server').first()
    s = Status.query.filter_by(name='Active').first()
    a.provider_type = pt
    a.status = s
    d.provider_type = pt
    d.status = s
    db.session.add_all([a, d])
    db.session.commit()


@manager.command
def reset():
    db.drop_all()
    db.create_all()

if __name__ == "__main__":
    manager.run()
