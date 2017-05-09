#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from contacts_filter import *
from sqlalchemy import func
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from search_db_model_base import AtomSearchBase, ResidueContactSearchBase


eng = 'mysql://root:root@127.0.0.1/proeng'
engine = create_engine(eng, convert_unicode=True)
g = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                bind=engine))

CTT_UPDATED = False


def update_short_db():
    dbs_up = get_available_dbs()
    for b in dbs_up:

        for a in RESIDUELIST:
            tp2 = RESIDUEDICT[b.upper()] + RESIDUEDICT[a]
            gf = dbs_up[b]
            cts = gf.query(ResidueContactSearchBase)\
                    .filter(ResidueContactSearchBase.ctt_type == tp2)\
                    .order_by(ResidueContactSearchBase.id_contact)
            for ct in cts:
                atms = get_atoms_search_db(gf, ct.id_contact)
                dist = atms[5] - atms[17]
                gf.query(ResidueContactSearchBase)\
                  .filter(ResidueContactSearchBase.id_contact == ct.id_contact)\
                  .update({ResidueContactSearchBase.dca: round(dist, 3)})
        gf = dbs_up[b]
        mn = gf.query(func.max(ResidueContactSearchBase.dca)).scalar()
        mx = gf.query(func.min(ResidueContactSearchBase.dca)).scalar()
        print b, round(mn, 3), round(mx, 3)


def get_atoms_search_db(gf, ct_id):
    """
    :param ct_id: ID of contact
    :return: lst obj Bio.PDB.Atom.Atom
    """
    atms = gf.query(AtomSearchBase)\
             .filter(AtomSearchBase.id_ctt == ct_id)\
             .order_by(AtomSearchBase.serial_number).all()
    atm_list = []  # lista de átomos com objetos da classe Bio.PDB.Atom.Atom
    for atm in atms:
        atom_parsed = parser_atom(atm)
        if atom_parsed is None:
            continue
        atm_list.append((int(atm.serial_number), atom_parsed))
    atm_list = sorted(atm_list)
    return map(lambda x: x[1], atm_list)


if __name__ == '__main__':

    update_short_db()
