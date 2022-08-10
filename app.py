from flask import (Flask, abort, jsonify, redirect, render_template, request,
                   url_for)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:abc123@localhost:5432/todoapp'
db = SQLAlchemy(app)

class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)

  def __repr__(self):
    return f'<Todo {self.id} {self.description}>'

db.create_all()


@app.route('/todos/create', methods=['POST'])
def create_todo():
  description = request.form.get('description')
  todo = Todo(description=description)
  db.session.add(todo)
  db.session.commit()
  return render_template('index.html', data=Todo.query.all())



@app.route('/')
def index():
  return render_template('index.html', data=Todo.query.all())





#always include this at the bottom of your code
if __name__ == '__main__':
   app.run(host="0.0.0.0", port=3000)