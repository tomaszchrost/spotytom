from app import db
from app.models import User


def main():
    u = User.query.filter_by(username='NAMEHERE').first()
    u.set_password("PASSHERE")

    db.session.add(u)
    db.session.commit()


if __name__ == "__main__":
    main()
