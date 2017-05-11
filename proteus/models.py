#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from database import db_session, Base
from sqlalchemy import Column, Integer, String, Float, Text
from contacts_filter import *
import hashlib
import datetime
import os
import copy


class User(Base):

    __tablename__ = 'user'

    id_u = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    # Identification Data: email & password
    email = Column(String(128), nullable=False, unique=True)
    # password = Column(String(192), nullable=False)
    # Authorisation Data: role & status
    # role = Column(SmallInteger, nullable=False)
    # status = Column(SmallInteger, nullable=False)

    # New instance instantiation procedure
    def __init__(self, name, email):  # , password):

        self.name = name
        self.email = email
        # self.password = password

    def __repr__(self):
        return '<User %r>' % (self.name)


class Processing(Base):

    __tablename__ = 'processing'

    id_p = Column(Integer, primary_key=True)
    id_user = Column(Integer)
    status = Column(Integer)
    pdbid = Column(String)
    cutoff = Column(Float(precision=2))
    url = Column(String(64))

    def __init__(self, id_u, pdbid, cutoff, url, status=0):
        self.id_user = id_u
        self.pdbid = pdbid
        self.cutoff = cutoff
        self.url = url
        self.status = status


class Contact(Base):

    __tablename__ = 'contact'

    id_ctt = Column(Integer, primary_key=True)
    id_p = Column(Integer)
    ctt_type = Column(String(30))
    ctt_status = Column(Integer)
    ctt_chain = Column(String(4))
    ctt_sequence = Column(Integer)

    def __init__(self, id_p, tp, status, chain, seq):
        self.id_p = id_p
        self.ctt_type = tp
        self.ctt_status = status
        self.ctt_chain = chain
        self.ctt_sequence = seq


class AtomProeng(Base):

    __tablename__ = 'atom'

    id_atom = Column(Integer, primary_key=True)
    id_ctt = Column(Integer)
    sequence = Column(Integer)
    name = Column(String(5))
    level = Column(String(5))
    bfactor = Column(Float)
    occupancy = Column(Float)
    element = Column(String(10))
    serial_number = Column(Integer)
    fullname = Column(String(10))
    coord = Column(String(30))
    type = Column(Integer)

    def __init__(self, id_c, seq, nm, lv, bf, oc, el, sn, fn, co, tp=1):
        self.id_ctt = id_c
        self.sequence = seq
        self.name = nm
        self.level = lv
        self.bfactor = bf
        self.occupancy = oc
        self.element = el
        self.serial_number = sn
        self.fullname = fn
        self.coord = co
        self.type = tp


class AlignProeng(Base):

    __tablename__ = 'align'

    id_alg = Column(Integer, primary_key=True)
    id_ctt = Column(Integer)
    id_ctt_search_db = Column(Integer)
    al_score = Column(Float)
    al_type = Column(String(7))
    pdbid = Column(String(4))
    chain = Column(String(4))
    r1 = Column(String(7))
    r2 = Column(String(7))
    rotation = Column(Text)
    translation = Column(Text)

    def __init__(self, id_ctt, id_rc, score, type, pdbid, chain, r1, r2,
                 r='', t=''):
        self.id_ctt = id_ctt
        self.id_ctt_search_db = id_rc
        self.al_score = score
        self.al_type = type
        self.pdbid = pdbid
        self.chain = chain
        self.r1 = r1
        self.r2 = r2
        self.rotation = r
        self.translation = t


class AtomAlignProeng(Base):

    __tablename__ = 'atom_align'

    id_atom = Column(Integer, primary_key=True)
    id_align = Column(Integer)
    name = Column(String(5))
    level = Column(String(5))
    bfactor = Column(Float)
    occupancy = Column(Float)
    element = Column(String(10))
    serial_number = Column(Integer)
    fullname = Column(String(10))
    coord = Column(String(25))

    def __init__(self, id_c, nm, lv, bf, oc, el, sn, fn, co):
        self.id_align = id_c
        self.name = nm
        self.level = lv
        self.bfactor = bf
        self.occupancy = oc
        self.element = el
        self.serial_number = sn
        self.fullname = fn
        self.coord = co


def get_user(nm, eml):
    user = User.query.filter(User.email == "{}".format(eml)).first()
    if user:
        return user
    else:
        user = User(nm.encode('utf-8'), eml.encode('utf-8'))
        db_session.add(user)
        db_session.commit()
        return user


def store_contacts(gc, id_p):
    lst_ctt_prot = prepare_res_align(gc)
    for ctt in gc.contacts:
        rn1_ct = gc.residues[ctt[0]][0]
        rn2_ct = gc.residues[ctt[1]][0]
        ct_name = RESIDUEDICT[rn1_ct] + str(ctt[0]) + '-'
        ct_name += RESIDUEDICT[rn2_ct] + str(ctt[1])
        c = Contact(id_p, ct_name, 0, str(gc.chain.id), ctt[0])
        db_session.add(c)
        db_session.commit()

        f1 = []  # receive the contacts from pdb uploaded
        #     first triple           second triple
        lp = lst_ctt_prot[ctt[0]] + lst_ctt_prot[ctt[1]]
        for c1 in lp:
            f1 += copy.deepcopy(c1)
        for i, f in enumerate(f1):
            tpa = 1 if f['name'] in MAINCHAIN else 0
            a = AtomProeng(c.id_ctt, i, f['name'], f['level'], f['bfactor'],
                           f['occupancy'], f['element'], f['serial_number'],
                           f['fullname'], f['coord'], tpa)
            db_session.add(a)
        db_session.commit()


def generate_url(url):
    dt = str(datetime.datetime.now())
    url += dt
    e = hashlib.sha256()
    e.update(url)
    return e.hexdigest()


def get_user_folder(usr, usp_f):
    uf = usr.email.split("@")[0] + "_" + str(usr.id_u)
    fus = os.path.join(usp_f, uf)
    if not os.path.exists(fus):
        os.mkdir(fus)
    return fus


def get_user_process_folder(uf, prc):
    uf = os.path.abspath(uf)
    prc = os.path.join(uf, prc)
    if not os.path.exists(prc):
        os.mkdir(prc)
    return prc


def get_pdb_file(prf, ctt_id, pdb, pdb_type='w', mc=0, atms=None):
    prf = os.path.abspath(prf)
    cttf = os.path.join(prf, pdb)
    elm = prf.split('/')
    fr = '/static/user_aligns/%s/%s/%s' % (elm[-2], elm[-1], pdb)
    if not os.path.exists(cttf):
        if pdb_type == 'w':
            create_pdb_wild(cttf, ctt_id, mc)
        else:
            create_mutate_pdb(ctt_id, cttf, mc, atms)
    return fr


def create_pdb_wild(out_file, ct_id, sc=0):
    if sc == 0:
        ats = AtomProeng.query.filter(AtomProeng.id_ctt == ct_id)\
                              .filter(AtomProeng.type == 1)\
                              .order_by(AtomProeng.serial_number)
    else:
        ats = AtomProeng.query.filter(AtomProeng.id_ctt == ct_id)\
                              .order_by(AtomProeng.serial_number)
    ch = Chain('A')
    atms = [a for a in ats]
    if len(atms) == 0:
        return None
    r_ret = None  # residue return
    r_num = 0     # residue number
    for a in atms:
        patm = parser_atom(a)
        if a.name == 'N':
            if r_num > 0:
                ch.add(r_ret)
            r_num += 1
            r_ret = Residue((' ', r_num, ' '), 'NNN', r_num)
        r_ret.add(patm)
    ch.add(r_ret)
    w = PDBIO()
    w.set_structure(ch)
    w.save(out_file)
