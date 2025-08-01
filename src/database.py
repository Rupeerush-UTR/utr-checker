from models import db, UTR

def add_utr(utr, note=""):
    if UTR.query.filter_by(utr=utr).first():
        return False
    new_utr = UTR(utr=utr, note=note)
    db.session.add(new_utr)
    db.session.commit()
    return True

def query_utr(utr):
    return UTR.query.filter_by(utr=utr).first()
