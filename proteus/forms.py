import os

from wtforms import Form, StringField, FileField, FloatField, validators,\
    ValidationError
import re

UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "")

ALLOWED_EXTENSIONS = set(['pdb'])


class UploadForm(Form):
    cutoff = FloatField('Cutoff', [validators.NumberRange(min=0.0, max=2.0)],
                        render_kw={'placeholder': '0.5', 'class': ''})
    name = StringField('Name', [validators.Length(max=128),
                                validators
                                .DataRequired(message='Forgot your name?')])
    email = StringField('Email Address',
                        [validators.Email('Email address is not valid!'),
                         validators
                         .DataRequired(message='Forgot your email address?')])
    '''pdbfile = FileField('PDB File', [validators
                                     .Regexp(u'([0-9A-Za-z0-9])*\.pdb$')])'''
    pdbfile = FileField('PDB File')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload(request):
    form = UploadForm(request.POST)
    if form.pdbfile.data:
        pdbfile = request.FILES[form.pdbfile.name].read()
        fl = open(os.path.join(UPLOAD_FOLDER, form.pdbfile.data), 'w')
        fl.write(pdbfile)
        fl.close()
    else:
        raise ValidationError('The file is not a PDB.')


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash("Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))


def verifie_pdbfile(files):
    if 'pdbfile' not in files:
        msg = 'Please, choose a PDB file!'
    else:
        file = files['pdbfile']
        r = re.compile(u'([0-9A-Za-z0-9])*\.pdb$')
        if r.match(file.filename.lower()):
            msg = None
        else:
            msg = 'Invalid input. It should be in "*.pdb" format'
    return msg
