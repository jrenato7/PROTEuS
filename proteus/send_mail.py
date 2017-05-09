#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask_mail import Message
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


FROM = 'proteus.lbs@gmail.com'


def send_mail_process_start(mail, to, name, pid, pdbid, cuttoff, url):
    print to, name, pid, pdbid, cuttoff, url
    subject = "Process of %s Started in PROTEuS" % (pdbid)
    subject = subject.encode("utf-8")
    snd = ('PROTEuS Team'.encode("utf-8"), FROM.encode("utf-8"))
    msg = Message(subject, sender=snd, recipients=[to.decode("utf-8")])
    html = '''<p>Dear <strong>{0}</strong>,</p>
<p>Your project has been successfully submitted.</p>
<p>The paramms of your submission were: PDB ID {3} with cutoff of {4}.</p>
<p>To follow the job processing, access the following link:
<a href="{1}/result/{2}">{1}result/{2}</a>.</p>
<p><strong>You receive this e-mail because it was used as contact
in PROTEuS tool.</strong></p>
<p>Best regards, PROTEuS Team.</p>
<img src='{1}static/img/proteus_footer.png' class="rounded mx-auto d-block" >
'''.format(name.decode("utf-8"), url, pid, pdbid, cuttoff)
    msg.html = html.encode("utf-8")
    mail.send(msg)
