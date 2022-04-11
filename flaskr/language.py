from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for, session)

from flask_babel import Babel, gettext

bp = Blueprint('language', __name__)

@bp.route('/', methods=['GET', 'POST'])
def language():
    lang = request.args.get('lang')

    if lang is None:
        lang = 'en'

    session['lang'] = lang

    return render_template('blog/index.html', lang = lang)
