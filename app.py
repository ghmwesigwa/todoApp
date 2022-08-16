import sys

from flask import (Flask, abort, jsonify, redirect, render_template, request,
                   url_for)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:abc123@localhost:5432/todoapp'
db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey(
        'todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'


class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)

# POST request listener from form element
@app.route('/todos/create', methods=['POST'])
def create_todo():
    # define error flag
    error = False

    body = {}

    # use try-except-finally to handle possible commit failure
    try:
        # gets value of key='description' from returning json
        description = request.get_json()['description']

        list_id = request.get_json()['list_id']

        # create new Todo with form data
        todo = Todo(description=description, list_id=list_id)

        # add new todo object to session and commit
        # this adds new entry to database
        db.session.add(todo)
        db.session.commit()

        # define body with description before session closes
        body['description'] = todo.description
    except:
        # set error to T if error
        error = True

        # roll back session if commit fails
        db.session.rollback()

        # print error information
        print(sys.exc_info())
    finally:
        # always close the session
        db.session.close()
    if error:
        # abort request using code for Internal Server Error
        abort(400)
    else:
        # return json using new description information
        return jsonify(body)


@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))


@app.route('/todos/<todo_id>/delete', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})


@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    # tells the view to render with index.html using latest model
    return render_template('index.html',
                           lists=TodoList.query.all(),
                           active_list=TodoList.query.get(list_id),
                           todos=Todo.query.filter_by(list_id=list_id).order_by('id').all())


@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))