from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///notesweb.db"
app.config['SECRET_KEY'] = 'thisisanotessavingwebsite'
bootstrap = Bootstrap5(app)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Notes(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    Title: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False)
    note: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


class AddNotes(FlaskForm):
    Title = StringField(label='Title', validators=[DataRequired(), Length(max=100)])
    note = StringField(label='Notes', validators=[DataRequired(), Length(max=250)])
    submit = SubmitField(label='Save')

class EditNotes(FlaskForm):
    note = StringField(label='Notes', validators=[DataRequired(), Length(max=250)])
    submit = SubmitField(label='Save')


@app.route('/')
def home():
    result = db.session.execute(db.select(Notes).order_by(Notes.Title)).scalars().all()
    return render_template('index.html', data=result)


@app.route('/addnotes', methods=['GET', 'POST'])
def add():
    form = AddNotes()
    if form.validate_on_submit():
        date = datetime.datetime.now().strftime(f"{'%d'}/{'%m'}/{'%Y'}")
        new_note = Notes(
            date=str(date),
            Title=form.Title.data,
            note=form.note.data
        )
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_notes.html', form=form)

@app.route("/deletenote")
def delete():
    id = request.args.get('id')
    note = db.get_or_404(Notes, id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/editnote", methods=["GET", 'POST'])
def edit():
    form = EditNotes()
    id = request.args.get('id')
    note = db.get_or_404(Notes, id)
    if form.validate_on_submit():
        note.note = form.note.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html', form=form)

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
