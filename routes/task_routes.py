from datetime import datetime

from bson.objectid import ObjectId
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from database import tasks_collection, users_collection
from models.task_model import TaskModel


task_bp = Blueprint('tasks', __name__)


def expire_old_tasks():
    current_time = datetime.utcnow()

    expired_tasks = list(
        tasks_collection.find(
            {
                'status': 'live',
                'deadline': {'$lt': current_time},
            }
        )
    )

    for task in expired_tasks:
        creator_id = task.get('creator_id')
        task_credits = task.get('credits', 0)
        try:
            task_credits = int(task_credits)
        except (TypeError, ValueError):
            task_credits = 0

        if creator_id is not None and task_credits > 0:
            try:
                creator_oid = (
                    ObjectId(creator_id) if isinstance(creator_id, str) else creator_id
                )
                users_collection.update_one(
                    {'_id': creator_oid},
                    {'$inc': {'credits': task_credits}},
                )
            except Exception:
                pass

        tasks_collection.update_one(
            {'_id': task['_id']},
            {'$set': {'status': 'expired'}},
        )


def _get_logged_in_user():
    user_id = session.get('user_id')
    if not user_id:
        return None

    try:
        return users_collection.find_one({'_id': ObjectId(user_id)})
    except Exception:
        return None


def _require_logged_in_user():
    user = _get_logged_in_user()
    if not user:
        session.clear()
        flash('Please log in to continue.', 'warning')
        return None

    try:
        user['credits'] = int(user.get('credits', 0))
    except (TypeError, ValueError):
        user['credits'] = 0

    return user


@task_bp.route('/dashboard')
def dashboard():
    user = _require_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))

    return render_template('dashboard.html', user=user)


@task_bp.route('/post-task', methods=['GET', 'POST'])
@task_bp.route('/tasks/post', methods=['GET', 'POST'])
def post_task():
    user = _require_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('post_task.html', user=user)

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    duration = request.form.get('duration', '').strip()
    deadline_str = request.form.get('deadline', '').strip()

    if not title or not description or not duration or not deadline_str:
        flash('All fields are required.', 'danger')
        return redirect(url_for('tasks.post_task'))

    try:
        task_credits = int(request.form['credits'])
    except (KeyError, TypeError, ValueError):
        flash('Credits must be a valid integer.', 'danger')
        return redirect(url_for('tasks.post_task'))

    if task_credits <= 0:
        flash('Credits must be greater than 0.', 'danger')
        return redirect(url_for('tasks.post_task'))

    if user['credits'] < task_credits:
        flash('You do not have enough credits to post this task.', 'danger')
        return redirect(url_for('tasks.post_task'))

    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        flash('Deadline format is invalid.', 'danger')
        return redirect(url_for('tasks.post_task'))

    task_doc = TaskModel.create_task(
        creator_id=user['_id'],
        title=title,
        description=description,
        credits=task_credits,
        duration=duration,
        deadline=deadline,
    )

    users_collection.update_one(
        {'_id': user['_id']},
        {
            '$inc': {'credits': -task_credits},
            '$push': {'created_tasks': task_doc['_id']},
        },
    )

    flash('Task posted successfully!', 'success')
    return redirect(url_for('tasks.dashboard'))


@task_bp.route('/browse-tasks')
@task_bp.get('/tasks/browse')
def browse_tasks():
    user = _require_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))

    expire_old_tasks()

    tasks = list(
        tasks_collection.find(
            {
                'status': 'live',
                'acceptor_id': None,
                'creator_id': {'$nin': [user['_id'], session['user_id']]},
            }
        )
    )
    for task in tasks:
        try:
            task['credits'] = int(task.get('credits', 0))
        except (TypeError, ValueError):
            task['credits'] = 0

        creator = None
        creator_id = task.get('creator_id')
        if creator_id is not None:
            try:
                creator_lookup_id = (
                    ObjectId(creator_id) if isinstance(creator_id, str) else creator_id
                )
                creator = users_collection.find_one({'_id': creator_lookup_id})
            except Exception:
                creator = users_collection.find_one({'_id': creator_id})

        task['creator_name'] = creator['name'] if creator and creator.get('name') else 'Unknown'

    return render_template('browse_tasks.html', tasks=tasks, user=user)


@task_bp.route('/accept-task/<task_id>')
def accept_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    try:
        task_oid = ObjectId(task_id)
        user_oid = ObjectId(session['user_id'])
    except Exception:
        flash('Invalid task or user id.', 'danger')
        return redirect(url_for('tasks.browse_tasks'))

    task = tasks_collection.find_one({'_id': task_oid})
    if not task:
        flash('Task not found.', 'warning')
        return redirect(url_for('tasks.browse_tasks'))

    if task.get('acceptor_id') is not None:
        flash('Task already accepted', 'warning')
        return redirect(url_for('tasks.browse_tasks'))

    result = tasks_collection.update_one(
        {'_id': task_oid, 'status': 'live'},
        {
            '$set': {
                'acceptor_id': user_oid,
                'status': 'accepted',
            }
        },
    )

    if result.modified_count == 0:
        flash('Task could not be accepted.', 'warning')
    else:
        flash('Task accepted successfully.', 'success')

    return redirect(url_for('tasks.browse_tasks'))


@task_bp.route('/complete-task/<task_id>', methods=['GET', 'POST'])
def complete_task(task_id):
    user = _require_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))

    try:
        task_oid = ObjectId(task_id)
    except Exception:
        flash('Invalid task id.', 'danger')
        return redirect(url_for('tasks.my_tasks'))

    task = tasks_collection.find_one({'_id': task_oid})
    if not task:
        flash('Task not found.', 'warning')
        return redirect(url_for('tasks.my_tasks'))

    creator_id = task.get('creator_id')
    acceptor_id = task.get('acceptor_id')

    if task.get('status') != 'accepted':
        flash('Only accepted tasks can be marked as completed.', 'warning')
        return redirect(url_for('tasks.my_tasks'))

    creator_id_str = str(creator_id)
    if creator_id_str != session.get('user_id'):
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('tasks.my_tasks'))

    if acceptor_id is None:
        flash('Task has no acceptor.', 'warning')
        return redirect(url_for('tasks.my_tasks'))

    try:
        acceptor_oid = (
            ObjectId(acceptor_id) if isinstance(acceptor_id, str) else acceptor_id
        )
    except Exception:
        flash('Invalid user ids on task.', 'danger')
        return redirect(url_for('tasks.my_tasks'))

    try:
        task_credits = int(task.get('credits', 0))
    except (TypeError, ValueError):
        task_credits = 0

    result = tasks_collection.update_one(
        {'_id': task_oid, 'status': 'accepted'},
        {'$set': {'status': 'completed'}},
    )
    if result.modified_count == 0:
        flash('Task could not be marked as completed.', 'warning')
        return redirect(url_for('tasks.my_tasks'))

    users_collection.update_one(
        {'_id': acceptor_oid},
        {'$inc': {'credits': task_credits}},
    )

    flash('Task completed and credits transferred.', 'success')
    return redirect(url_for('tasks.my_tasks'))


@task_bp.route('/delete-task/<task_id>')
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    try:
        task_oid = ObjectId(task_id)
    except Exception:
        flash('Invalid task id.', 'danger')
        return redirect(url_for('tasks.my_tasks'))

    task = tasks_collection.find_one({'_id': task_oid})
    if not task:
        flash('Task not found', 'warning')
        return redirect(url_for('tasks.my_tasks'))

    if str(task.get('creator_id')) != session['user_id']:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('tasks.my_tasks'))

    if task.get('status') != 'live':
        flash('Only live tasks can be deleted', 'warning')
        return redirect(url_for('tasks.my_tasks'))

    tasks_collection.delete_one({'_id': task_oid})
    flash('Task deleted successfully', 'success')
    return redirect(url_for('tasks.my_tasks'))


@task_bp.get('/tasks/mine')
def my_tasks():
    user = _require_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))

    session_user_id = session['user_id']
    try:
        user_oid = ObjectId(session_user_id)
    except Exception:
        session.clear()
        flash('Invalid user session.', 'danger')
        return redirect(url_for('auth.login'))

    creator_tasks = tasks_collection.find(
        {
            'creator_id': {'$in': [user_oid, session_user_id]},
        }
    )
    accepted_tasks = tasks_collection.find(
        {
            'acceptor_id': {'$in': [user_oid, session_user_id]},
        }
    )

    created_tasks = list(creator_tasks)
    accepted_tasks = list(accepted_tasks)

    for task in created_tasks + accepted_tasks:
        try:
            task['credits'] = int(task.get('credits', 0))
        except (TypeError, ValueError):
            task['credits'] = 0

    return render_template(
        'my_tasks.html',
        created_tasks=created_tasks,
        accepted_tasks=accepted_tasks,
        user=user,
    )

