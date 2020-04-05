from app import app
from flask import render_template, redirect, url_for, request, session, flash

@app.route('/upload')
def upload():
    return render_template('submission.html')

@app.route('/contentall')
def contentAll():
    return render_template('interactive-resources.html')