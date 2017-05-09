#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import traceback
from flask import Flask
from flask import request, render_template, flash, redirect, url_for, \
    abort, json
from flask_mail import Mail
from werkzeug.utils import secure_filename
from jinja2 import TemplateNotFound
from generate_contacts import GenerateContactsPdbFile
from forms import *
from models import Processing, Contact, get_user, \
    store_contacts, generate_url, AlignProeng, AtomAlignProeng, User, \
    get_pdb_file, get_user_folder, get_user_process_folder
from database import db_session
from send_mail import send_mail_process_start


# BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_url_path='/static')

app.config.update(
    {'DEBUG': True, 'BASE_DIR': os.environ.get("BASE_DIR", ""),
     'UPLOAD_FOLDER': os.environ.get("UPLOAD_FOLDER", ""),
     'USER_PROCESS_FOLDER': os.environ.get("USER_PROCESS_FOLDER", ""),
     'SECRET_KEY': os.environ.get("SECRET_KEY", ""),
     'MAX_CONTENT_LENGTH': 5 * 1024 * 1024, 'MAIL_SERVER': 'smtp.gmail.com',
     'MAIL_PORT': 465, 'MAIL_USERNAME': 'proteus.lbs@gmail.com',
     'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD', ''),
     'MAIL_USE_TLS': False, 'MAIL_USE_SSL': True})

mail = Mail(app)

up_f = app.config['UPLOAD_FOLDER']

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/', methods=['GET', 'POST'])
def index():
    title = "PROTEUS"
    subtitle = "PROTein Engineering Supporter"
    form = UploadForm(request.form)
    if request.method == 'POST':
        vld = verifie_pdbfile(request.files)
        if form.validate() and not vld:
            file = request.files['pdbfile']
            user = get_user(form.name.data, form.email.data)
            user_id = user.id_u
            filename = secure_filename(file.filename)
            fs = os.path.join(up_f, filename)
            file.save(fs)
            cutoff = form.cutoff.data
            pdb_name = filename.split('.')[0]
            url = generate_url(pdb_name + str(cutoff) + str(user_id))
            prc = Processing(user_id, pdb_name, cutoff, url)
            db_session.add(prc)
            db_session.commit()
            gc = GenerateContactsPdbFile(fs)
            store_contacts(gc, prc.id_p)
            send_mail_process_start(mail, user.email, user.name, prc.url,
                                    prc.pdbid, prc.cutoff, request.url)
            return redirect(url_for('result',
                                    url=prc.url))
        else:
            if vld:
                form.pdbfile.errors = [vld, ]
    return render_template('home.html', **locals())


@app.route('/result/<url>', methods=['GET'])
def result(url):
    try:
        prc = Processing.query.filter(Processing.url == "{}".format(url)
                                      ).first()
        title = "PDB ID: "
        title += prc.pdbid
        subtitle = "Cutoff: "
        subtitle += str(prc.cutoff)

    except:
        title = "Process not found!"
        subtitle = "The process requested isn't in our database. Please send "
        subtitle += " an email to jose.renato77@gmail.com with the "
        subtitle += "URL accessed!"
    return render_template('result.html', **locals())


@app.route('/about/', methods=['GET'])
def about():
    return render_template(
        'about.html')


@app.route('/process/<url>', methods=['GET'])
def process(url):
    try:
        prc = Processing.query.filter(Processing.url == "{}".format(url)
                                      ).first()
        ctts = Contact.query.filter(Contact.id_p == prc.id_p,
                                    Contact.ctt_status > 0
                                    ).order_by(Contact.ctt_sequence)
        data = {'ps': prc.status}
        data['contacts'] = []
        for ct in ctts:
            c = {'id': ct.id_ctt, 'title': ct.ctt_type}
            alg = AlignProeng.query\
                             .filter(AlignProeng.id_ctt == ct.id_ctt)\
                             .order_by(AlignProeng.al_score)
            contacts = []
            for al in alg:
                alid = prc.url + '.' + str(ct.id_ctt) + '.' + str(al.id_alg)
                a = {'type': al.al_type, 'pdbid': al.pdbid, 'chain': al.chain,
                     'r1': al.r1, 'r2': al.r2, 'score': al.al_score,
                     'alid': alid}
                contacts.append(a)
            c['contacts'] = contacts
            data['contacts'].append(c)
    except:
        data = {}
    return json.dumps(data)


@app.route('/showalign/<url>', methods=['GET'])
def showalign(url):
    try:
        usp_f = app.config['USER_PROCESS_FOLDER']
        e = url.split('.')
        purl = e[0]
        cid = int(e[1])
        aid = int(e[2])
        prc = Processing.query.filter(Processing.url == "{}".format(purl)
                                      ).first()
        ctt = Contact.query.filter(Contact.id_ctt == "{}".format(cid))\
                           .first()
        if prc.id_p != ctt.id_p:
            raise ValueError('Contact is not of requested Process!!')

        aln = AlignProeng.query\
                         .filter(AlignProeng.id_alg == "{}".format(aid))\
                         .first()

        if aln.id_ctt != ctt.id_ctt:
            raise ValueError('Align is not of requested Contact!!')

        usr = User.query.filter(User.id_u == prc.id_user).first()
        usr_f = get_user_folder(usr, usp_f)
        prf = get_user_process_folder(usr_f, prc.url)

        f1 = get_pdb_file(prf, ctt.id_ctt, ctt.ctt_type + '.pdb')
        pdb_m = str(aln.id_ctt) + aln.r1 + aln.r2 + '.pdb'
        n_ats = AtomAlignProeng.query\
                               .filter(AtomAlignProeng.id_align == aln.id_alg)\
                               .order_by(AtomAlignProeng.serial_number)
        print "F2: ", prf, aln.id_ctt_search_db, pdb_m
        f2 = get_pdb_file(prf, aln.id_ctt_search_db, pdb_m, 'm', atms=n_ats)

        data = {'e': 0, 'f1': f1, 'f2': f2}
    except:
        trace = traceback.format_exc()
        print trace
        data = {'e': 1}
    return json.dumps(data)


@app.route('/updatedb/', methods=['GET'])
def updatedb():
    ctts = Contact.query.filter(Contact.id_ctt > 0)
    for ct in ctts:
        seq = int(ct.ctt_type.split("-")[0][1:])
        db_session.query(Contact)\
                  .filter(Contact.id_ctt == ct.id_ctt)\
                  .update({Contact.ctt_sequence: seq})
    flash("DataBase ok!")
    return redirect(url_for('index'))
