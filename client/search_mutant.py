#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from contacts_filter import *
from sqlalchemy import func
from sqlalchemy_pagination import paginate
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from search_db_model_base import AtomSearchBase, ResidueContactSearchBase
from proeng_model_base import ProcessingProeng, ContactProeng, AtomProeng, \
    AlignProeng, AtomAlignProeng, UserProeng
from Bio.PDB import Superimposer
from multiprocessing import Pool
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pickle as pk
import traceback
import copy
import smtplib
import sys
import os


reload(sys)
sys.setdefaultencoding('utf-8')

eng = 'mysql://root:root@127.0.0.1/proeng'
engine = create_engine(eng, convert_unicode=True)
g = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                bind=engine))

CTT_UPDATED = False


def get_atoms_type_search_db(gf, tp, page, limit):
    """"
    :return list: with ....
    """
    contacts = None
    try:
        contacts = paginate(gf.query(ResidueContactSearchBase)
                              .filter(ResidueContactSearchBase.ctt_type == tp),
                            page, limit).items
    except:
        trace = traceback.format_exc()
        print trace
    ret = []

    if contacts is None:
        return None
    for ct in contacts:
        atms = get_atoms_search_db(gf, ct.id_contact)
        r1 = ct.r1_name + str(ct.r1_position)
        r2 = ct.r2_name + str(ct.r2_position)
        ret.append((ct.ctt_pdbid, ct.ctt_chain, ct.id_contact, r1, r2, atms))
    return ret


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


def get_atoms_contact_proeng(ct_id):
    atms = g.query(AtomProeng).filter(AtomProeng.id_ctt == ct_id)\
            .filter(AtomProeng.type == 1)\
            .order_by(AtomProeng.serial_number)
    atm_list = []  # lista de átomos com objetos da classe Bio.PDB.Atom.Atom
    for atm in atms:
        atom_parsed = parser_atom(atm)
        if atom_parsed is None:
            continue
        atm_list.append((int(atm.serial_number), atom_parsed))
    atm_list = sorted(atm_list)
    return map(lambda x: x[1], atm_list)


def update_contact(ct_id):
    global CTT_UPDATED
    if not CTT_UPDATED:
        g.query(ContactProeng).filter(ContactProeng.id_ctt == ct_id)\
         .update({ContactProeng.ctt_status: 1})
        CTT_UPDATED = True


def update_process():
    prcs = g.query(ProcessingProeng).filter(ProcessingProeng.status == 0).all()
    for p in prcs:
        total = g.query(func.count(ContactProeng.id_ctt))\
                 .filter(ContactProeng.ctt_status == 0).scalar()
        if total == 0:
            usr = g.query(UserProeng).filter(UserProeng.id_u == p.id_user)\
                   .first()
            try:
                send_mail_process_finish(usr.name, usr.email, p.pdbid, p.url)
            except:
                print "Error send mail user"
            g.query(ProcessingProeng).filter(ProcessingProeng.id_p == p.id_p)\
             .update({ProcessingProeng.status: 1,
                      ProcessingProeng.notification_user: 1})


def send_mail_process_finish(name, mail, prt, pid):
    fromaddr = "PROTEuS Team <proteus.lbs@gmail.com>"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = mail
    msg['Subject'] = "Process of {} Finished!".format(prt)

    html = '''<p>Dear <strong>{0}</strong>,</p>
<p>Searching for compatible contacts is finished.</p>
<p>To see the job result, access the following link:
<a href="http://proteus.dcc.ufmg.br/result/{1}">
http://proteus.dcc.ufmg.br/result/{1}</a>.</p>
<p>Best regards, PROTEuS Team.</p>
<img src='http://proteus.dcc.ufmg.br/static/img/proteus_footer.png'
class="rounded mx-auto d-block" >
'''.format(name.decode("utf-8"), pid)

    msg.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('proteus.lbs@gmail.com', os.environ.get('MAIL_PASSWORD', ''))
    text = msg.as_string()
    server.sendmail(fromaddr, mail, text)
    server.quit()


def process_contacts(lst):
    cutoff = lst[0]
    tp_ins = lst[1]
    ct_id = lst[2]
    f1 = lst[3]
    pd = lst[4]
    ch = lst[5]
    id_ctt = lst[6]
    r1 = lst[7]
    r2 = lst[8]
    # I'll align all ctts in DB with f1.
    f2 = copy.deepcopy(lst[9])
    cont = 0
    if len(f1) == len(f2):
        si = Superimposer()
        si.set_atoms(f1, f2)
        si.apply(f2)
        si.rms
        if si.rms < cutoff:
            eng3 = 'mysql://root:root@127.0.0.1/proeng'
            engine3 = create_engine(eng3, convert_unicode=True)
            g3 = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                             bind=engine3))
            row = g3.query(AlignProeng).filter(AlignProeng.id_ctt == ct_id)\
                    .filter(AlignProeng.al_type == tp_ins).first()
            if row is None:
                r, t = si.rotran
                re = pk.dumps(r).encode('utf-8')
                te = pk.dumps(t).encode('utf-8')
                cont += 1
                new_alg = AlignProeng(ct_id, id_ctt, si.rms, tp_ins,
                                      pd, ch, r1, r2, re, te)
                g3.add(new_alg)
                g3.commit()
                id_align = new_alg.id_alg
                for a_n in f2:
                    coord = "[%.3f; %.3f; %.3f]" % (a_n.coord[0],
                                                    a_n.coord[1],
                                                    a_n.coord[2])
                    atm_new = AtomAlignProeng(id_align, a_n.name,
                                              a_n.level, a_n.bfactor,
                                              a_n.occupancy, a_n.element,
                                              a_n.serial_number,
                                              a_n.fullname, coord)
                    g3.add(atm_new)
                    atm_new = None
                new_alg = None
                g3.commit()
            else:
                cont += 1
            g3.close()
            engine3 = None
            eng3 = None
            update_contact(ct_id)
    return cont


def seach_mutant_aux(elm, num_cores):
    dbs_up = get_available_dbs()
    cutoff = elm[0]
    trp = elm[1].split("-")  # R282-E286
    tp = RESIDUEDICT2[trp[0][0]] + '-' + RESIDUEDICT2[trp[1][0]]
    ct_id = elm[2]
    cont = 0
    for b in dbs_up:
        for a in RESIDUELIST:
            tp_ins = b.upper() + '-' + a
            if tp == tp_ins:
                # deny search for the same contact type.
                # if tp = ser-ser, do not search for ser-ser.
                continue
            # lista has all contacts stored in db of type b-a:: (CYS-CYS)
            tp2 = RESIDUEDICT[b.upper()] + RESIDUEDICT[a]

            gf = dbs_up[b]

            total_align = gf.query(func.count(ResidueContactSearchBase))\
                            .filter(ResidueContactSearchBase.ctt_type == tp2)\
                            .scalar()
            if total_align == 0:
                continue
            num_proc = num_cores * 10
            pages = total_align / num_proc

            for er in range(1, pages + 1):
                lst = None
                f1 = None
                lst = get_atoms_type_search_db(gf, tp2.lower(), er, num_proc)
                if lst is None:
                    break
                lst_proc = []
                for el in lst:
                    f1 = copy.deepcopy(elm[3])
                    lstpro = [cutoff, tp_ins, ct_id, f1] + list(el)
                    lst_proc.append(lstpro)
                pl = Pool(num_cores)
                ret = pl.map(process_contacts, lst_proc)
                pl.close()
                pl.terminate()
                t = 0
                try:
                    t = ret.index(1)
                    cont += t + 1
                except:
                    cont += 0
                if t != 0:
                    break
    if cont == 0:
        a = g.query(ContactProeng).filter(ContactProeng.id_ctt == ct_id)\
             .update({ContactProeng.ctt_status: -1})
    else:
        a = g.query(ContactProeng).filter(ContactProeng.id_ctt == ct_id)\
             .update({ContactProeng.ctt_status: 2})


def search_mutant_db(num_cores):
    ct = g.query(ContactProeng).filter(ContactProeng.ctt_status == 0)\
          .order_by(ContactProeng.ctt_sequence).first()
    if ct:
        g.query(ContactProeng).filter(ContactProeng.id_ctt == ct.id_ctt)\
         .update({ContactProeng.ctt_status: 3})
        prc = g.query(ProcessingProeng)\
               .filter(ProcessingProeng.id_p == ct.id_p).first()
        atms = get_atoms_contact_proeng(ct.id_ctt)
        lst_proc = [prc.cutoff, ct.ctt_type, ct.id_ctt, atms]
        seach_mutant_aux(lst_proc, num_cores)
        return True
    else:
        update_process()
        return False


if __name__ == '__main__':

    search_mutant_db(20)
    g.close()
