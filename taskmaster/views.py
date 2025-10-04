from django.views.decorators.http import require_safe
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from datetime import datetime

from notes.models import Document
from taskmaster.models import TaskBoard, TaskList, Task
from taskmaster.forms import AddBoardForm, CreateTaskListForm, CreateTaskForm, CreateTaskMiniForm, TaskForm, EditTaskListForm
from taskmaster import services
from notes.forms import AddTagForm
from notes.services.object_handling import handle_new_tag, remove_object

@login_required
def index(request):

    boards = TaskBoard.objects.all()
    if request.method == 'POST':
        form = AddBoardForm(request.POST)
        if form.is_valid():
            board_name = form.cleaned_data.get('board_name')
            if not TaskBoard.objects.filter(board_name=board_name).exists():
                new_board = TaskBoard(board_name=board_name, board_created_by=request.user,
                                      board_last_modified_by=request.user)
                new_board.save()
                return redirect(reverse('taskmaster:display_board', args=(new_board.id,)))
            else:
                # TODO: decide how to handle when name is already taken?
                pass

        return render(request, 'taskmaster/index.html',
                      {'boards': boards,
                              'create_board_form': AddBoardForm()})

    return render(request, 'taskmaster/index.html',
                  {'boards': boards,
                   'create_board_form': AddBoardForm()})


@login_required
def display_board(request, board_id):
    board = TaskBoard.objects.get(id=board_id)
    board_lists = list(board.tasklist_set.all())
    tasks_without_lists = board.task_set.filter(task_board=board, task_list=None)

    if request.method == 'POST':
        list_form = CreateTaskListForm(request.POST)
        task_form = CreateTaskMiniForm(request.POST)
        if list_form.is_valid():
            list_name = list_form.cleaned_data.get('list_name')
            if not TaskList.objects.filter(list_name=list_name, list_board=board).exists():
                last_list = board.get_last_task_list_in_custom_order()

                new_list = TaskList(list_name=list_name, list_board=board)
                new_list.save()
                if last_list:
                    last_list.next_list = new_list
                    last_list.save()
                    new_list.previous_list = last_list
                    new_list.save()
                else:
                    new_list.save()

            else:
                #TODO: decide how to handle when the name of a list is already taken?
                pass

            board_lists = list(board.tasklist_set.all())  # Get an updated object of the board lists.

        if task_form.is_valid():
            current_list_name = request.POST['currently_viewed_task_list']
            current_list = TaskList.objects.get(list_name=current_list_name, list_board=board)
            task_name = task_form.cleaned_data.get('task_name')
            task_text = task_form.cleaned_data.get('task_text')
            task_importance = task_form.cleaned_data.get('task_importance')
            task_difficulty = task_form.cleaned_data.get('task_difficulty')
            task_assigned_to = task_form.cleaned_data.get('task_assigned_to')
            if not task_assigned_to:
                task_assigned_to = request.user.username

            new_task = Task(document_name=task_name, document_text=task_text, task_difficulty=task_difficulty,
                            task_importance=task_importance, task_assigned_to=task_assigned_to,
                            task_list=current_list, task_board=board, document_type='task',
                            document_created_by=request.user, document_last_modified_by=request.user)

            task_list = current_list.get_all_tasks_in_list_in_custom_order()
            new_task.save()  # Save the task immediately so that it exists in the database for last_task.

            if task_list:
                last_task = task_list[-1]
                last_task.next_task = new_task
                last_task.save()
                new_task.previous_task = last_task
                new_task.save()

            handle_new_tag('Task', new_doc=new_task, tag_creator=request.user, tag_type=('meta', 'task'))

        if 'move_task_up' in request.POST:
            task_to_move_id = request.POST['task_to_move']
            task_to_move = Task.objects.get(id=task_to_move_id)
            moved_task = services.move_task_up(task_to_move)
        if 'move_task_down' in request.POST:
            task_to_move_id = request.POST['task_to_move']
            task_to_move = Task.objects.get(id=task_to_move_id)
            moved_task = services.move_task_down(task_to_move)

        if 'move_list_left' in request.POST:
            list_to_move_id = request.POST['list_to_move']
            list_to_move = TaskList.objects.get(id=list_to_move_id)
            moved_list = services.move_list_left(list_to_move)

        if 'move_list_right' in request.POST:
            list_to_move_id = request.POST['list_to_move']
            list_to_move = TaskList.objects.get(id=list_to_move_id)
            moved_list = services.move_list_right(list_to_move)

        return render(request, 'taskmaster/display-task-board.html', {'board': board,
                                                                      'board_lists': board_lists,
                                                                      'orphan_tasks': tasks_without_lists,
                                                                      'create_board_list_form': CreateTaskListForm(),
                                                                      'create_task_form': CreateTaskMiniForm()})

    return render(request, 'taskmaster/display-task-board.html', {'board': board,
                                                                  'board_lists': board_lists,
                                                                  'orphan_tasks': tasks_without_lists,
                                                                  'create_board_list_form': CreateTaskListForm(),
                                                                  'create_task_form': CreateTaskMiniForm()})

@login_required
def edit_board(request, board_id):
    board = TaskBoard.objects.get(id=board_id)
    if request.method == 'POST':
        if 'name_textarea_edit_board_name' in request.POST:
            new_board_name = request.POST['name_textarea_edit_board_name']
            if new_board_name != '':
                board.board_name = new_board_name
                board.save()

        return redirect(reverse('taskmaster:display_board', args=(board_id, )))
    return render(request, 'taskmaster/edit-task-board.html', {'board': board})

@login_required
def display_task(request, task_id):
    task = Task.objects.get(id=task_id)
    return render(request, 'taskmaster/display-task.html', {'task': task})


@DeprecationWarning
@login_required
def edit_task_old(request, task_id):
    task = Task.objects.get(id=task_id)
    if request.method == 'POST':

        add_tag_form = AddTagForm(request.POST)
        if add_tag_form.is_valid():
            tag = add_tag_form.cleaned_data.get('tag_name')
            if tag != '':
                handle_new_tag(tag, new_doc=task, tag_creator=request.user)

        if 'name_textarea_edit_task_text' in request.POST:
            new_task_text = request.POST['name_textarea_edit_task_text']
            if new_task_text != task.document_text:
                task.document_text = new_task_text

        if 'name_textarea_edit_task_name' in request.POST:
            new_task_name = request.POST['name_textarea_edit_task_name']
            task.document_name = new_task_name

        if 'name_task_difficulty' in request.POST:
            new_difficulty = request.POST['name_task_difficulty']
            task.task_difficulty = new_difficulty

        if 'name_task_importance' in request.POST:
            new_importance = request.POST['name_task_importance']
            task.task_importance = new_importance

        if 'name_task_assigned_to' in request.POST:
            new_assignee = request.POST['name_task_assigned_to']
            task.task_assigned_to = new_assignee

        if 'name_parent_task_dropdown' in request.POST:
            new_parent_task_name = request.POST['name_parent_task_dropdown']
            if new_parent_task_name != 'None':
                new_parent_task = Task.objects.get(document_name=new_parent_task_name, task_board=task.task_board)
                if task.parent_task:
                    if task.parent_task != new_parent_task and task != new_parent_task and new_parent_task.parent_task != task:
                        task.parent_task = new_parent_task
                else:
                    if new_parent_task != task and new_parent_task.parent_task != task:
                        task.parent_task = new_parent_task
            else:
                task.parent_task = None

        if 'name-due-date-picker' in request.POST:
            due_date = request.POST['name-due-date-picker']
            if due_date:
                due_date = datetime.strptime(due_date, '%Y-%m-%d')
                due_date_with_timezone = timezone.make_aware(due_date, timezone.get_current_timezone(), True)
                if due_date_with_timezone != task.task_deadline:
                    task.task_deadline = due_date_with_timezone

        if 'name_list_dropdown' in request.POST:
            new_list = request.POST['name_list_dropdown']
            old_task_list = task.task_list  # The old list that the task used to belong to.
            # The new list the task belongs to.
            new_task_list = TaskList.objects.get(list_name=new_list, list_board=task.task_board)
            prev_task = task.previous_task
            if new_task_list != old_task_list:
                if prev_task:  # If there exists a previous task (i.e. more than one task exists)
                    next_task = task.next_task
                    if next_task:  # If there exists a next task.
                        prev_task.next_task = next_task
                        next_task.previous_task = prev_task
                        next_task.save()
                        prev_task.save()
                    else:
                        prev_task.next_task = None
                        prev_task.save()
                else:
                    # If there is no previous task but there is a next task then that next task must change its
                    # previous task to None.
                    next_task = task.next_task
                    if next_task:
                        next_task.previous_task = None
                        next_task.save()
                task.task_list = new_task_list
                # The task that used to be at the end of the new list.
                old_last_task = new_task_list.task_set.filter(next_task=None, task_list=new_task_list).last()
                if old_last_task:
                    if old_last_task != task:
                        old_last_task.next_task = task
                        task.previous_task = old_last_task
                        task.next_task = None
                        old_last_task.save()
                else:
                    task.next_task = None
                    task.previous_task = None

        if 'name_previous_task_dropdown' in request.POST:
            new_prev_task_name = request.POST['name_previous_task_dropdown']
            if new_prev_task_name != 'None':
                new_prev_task = Task.objects.get(document_name=new_prev_task_name, task_list=task.task_list)
                if new_prev_task != task.previous_task:
                    task.previous_task = new_prev_task
            else:
                task.previous_task = None

        if 'name_next_task_dropdown' in request.POST:
            new_next_task_name = request.POST['name_next_task_dropdown']
            if new_next_task_name != 'None':
                new_next_task = Task.objects.get(document_name=new_next_task_name, task_list=task.task_list)
                if new_next_task != task.next_task:
                    task.next_task = new_next_task
            else:
                task.next_task = None


        task.save()

        return redirect(reverse('taskmaster:display_task', args=(task_id, )))

    if task.task_list:
        all_tasks_in_same_list = task.task_list.get_all_tasks_in_list()
        all_tasks_in_same_list.append({'document_name': None})
    else:
        all_tasks_in_same_list = None

    possible_parent_tasks =  list(task.task_board.task_set.exclude(id=task.id).all())
    possible_parent_tasks.append({'document_name': None})  # Add the possibility that the task does not have a parent.
    return render(request, 'taskmaster/edit-task.html', {'task': task,
                                                         'tasks_in_list': all_tasks_in_same_list,
                                                         'add_tag_form': AddTagForm(),
                                                         'task_form': TaskForm(instance=task),
                                                         'possible_parent_tasks': possible_parent_tasks})

@login_required
def edit_task(request, task_id):
    # TODO: For the love of god make unit tests for this function.
    task = Task.objects.get(id=task_id)

    unchanged_task = Task.objects.get(id=task_id)  # We will use this to compare the changes made to the task.
    if request.method == 'POST':
        if 'remove_tag' in request.POST:
            tag_to_remove = request.POST['remove_tag']
            remove_object(tag_to_remove, 'tag', request)
            return redirect(reverse('taskmaster:edit_task', args=(task_id, )))

        add_tag_form = AddTagForm(request.POST)
        task_form = TaskForm(request.POST, instance=task)
        if add_tag_form.is_valid():
            tag = add_tag_form.cleaned_data.get('tag_name')
            if tag != '':
                handle_new_tag(tag, new_doc=task, tag_creator=request.user)

        if task_form.is_valid():
            # WARNING: checking if the task is valid will apply the changes to the model instance.
            # If you have this: task_form = TaskForm(request.POST, instance=task) then after doing .is_valid()
            # the task instance will have the changes applied to it.
            # This won't save the changes though, but it will affect the instance.

            # Check the new parent task.
            new_parent_task = task_form.cleaned_data.get('parent_task')

            # TODO: check if we can replace task_obj with "task" without issues.
            task_obj = task_form.save(commit=False)

            if new_parent_task and new_parent_task.task_board != unchanged_task.task_board:
                new_parent_task = None

            # We can't allow the new parent task to be a child of the task being edited.
            # This would create a circular reference.
            if new_parent_task and new_parent_task.parent_task == task:
                new_parent_task = None

            if new_parent_task:
                if unchanged_task.parent_task:
                    # The current parent task can't be the same as the new parent task.
                    # The task can't be its own parent task.
                    # The new parent task can't have this task as its own parent task (to avoid circular references).
                    if (unchanged_task.parent_task != new_parent_task
                            and unchanged_task != new_parent_task
                            and new_parent_task.parent_task != unchanged_task):
                        task_obj.parent_task = new_parent_task
                else:
                    # The task can't be its own parent task.
                    # The new parent task can't have this task as its own parent task (to avoid circular references).
                    if new_parent_task != unchanged_task and new_parent_task.parent_task != unchanged_task:
                        task_obj.parent_task = new_parent_task
            else:
                task_obj.parent_task = None

            task_obj.task_assigned_to = str(task_form.cleaned_data.get("task_assigned_to"))

            # Check if we changed the task list.
            new_list = task_form.cleaned_data.get('task_list')
            old_task_list = unchanged_task.task_list  # The old list that the task used to belong to.
            # The new list the task belongs to.
            new_task_list = TaskList.objects.filter(list_name=new_list, list_board=task.task_board).first()
            prev_task = unchanged_task.previous_task
            if new_task_list != old_task_list:
                if prev_task:  # If there exists a previous task (i.e. more than one task exists)
                    next_task = unchanged_task.next_task
                    if next_task:  # If there exists a next task.
                        prev_task.next_task = next_task
                        next_task.previous_task = prev_task
                        next_task.save()
                        prev_task.save()
                    else:
                        prev_task.next_task = None
                        prev_task.save()
                else:
                    # If there is no previous task but there is a next task then that next task must change its
                    # previous task to None.
                    next_task = unchanged_task.next_task
                    if next_task:
                        next_task.previous_task = None
                        next_task.save()
                task_obj.task_list = new_task_list
                # The task that used to be at the end of the new list.
                old_last_task = new_task_list.task_set.filter(next_task=None, task_list=new_task_list).last()
                if old_last_task:
                    if old_last_task != task_obj:
                        old_last_task.next_task = task_obj
                        task_obj.previous_task = old_last_task
                        task_obj.next_task = None
                        old_last_task.save()
                else:
                    task_obj.next_task = None
                    task_obj.previous_task = None

            # check previous task
            new_prev_task_name = task_form.cleaned_data.get('previous_task')
            if new_prev_task_name != unchanged_task.previous_task:
                if new_prev_task_name:
                    new_prev_task = Task.objects.get(document_name=new_prev_task_name, task_list=unchanged_task.task_list)
                    if new_prev_task != unchanged_task.previous_task:
                        task_obj.previous_task = new_prev_task
                else:
                    task_obj.previous_task = None

            # check next task
            new_next_task = task_form.cleaned_data.get('next_task')
            if new_next_task != unchanged_task.next_task:
                if new_next_task:
                    if new_next_task != unchanged_task.next_task:
                        task_obj.next_task = new_next_task
                    if not new_prev_task_name and new_next_task == unchanged_task.previous_task:
                        task_obj.next_task = None
                else:
                    task_obj.next_task = None

            task_obj.save()
            task_id = task_obj.id

            return redirect(reverse('taskmaster:display_task', args=(task_id,)))
        else:
            print('task_form is not valid!!!')
            print(task_form.errors)

    if task.task_list:
        all_tasks_in_same_list = task.task_list.get_all_tasks_in_list()
        all_tasks_in_same_list.append({'document_name': None})
    else:
        all_tasks_in_same_list = None

    possible_parent_tasks = list(task.task_board.task_set.exclude(id=task.id).all())
    possible_parent_tasks.append({'document_name': None})  # Add the possibility that the task does not have a parent.
    return render(request, 'taskmaster/edit-task.html', {'task': task,
                                                         'tasks_in_list': all_tasks_in_same_list,
                                                         'add_tag_form': AddTagForm(),
                                                         'task_form': TaskForm(instance=task),
                                                         'possible_parent_tasks': possible_parent_tasks})



@login_required
def delete_task(request, task_id):
    task_to_delete = Task.objects.get(id=task_id)
    task_board_id = task_to_delete.task_board.id

    next_task = task_to_delete.next_task
    previous_task = task_to_delete.previous_task
    if next_task and previous_task:
        previous_task.next_task = next_task
        next_task.previous_task = previous_task
        next_task.save()
        previous_task.save()

    task_to_delete.delete()
    return redirect(reverse('taskmaster:display_board', args=(task_board_id, )))

@login_required
def delete_list(request, list_id):
    list_to_delete = TaskList.objects.get(id=list_id)
    board= list_to_delete.list_board
    list_board_id = board.id

    next_list = list_to_delete.next_list
    prev_list = list_to_delete.previous_list
    if next_list and prev_list:
        prev_list.next_list = next_list
        next_list.previous_list = prev_list
        next_list.save()
        prev_list.save()

    list_to_delete.delete()
    return redirect(reverse('taskmaster:display_board', args=(list_board_id,)))

@login_required
def delete_board(request, board_id):
    board = TaskBoard.objects.get(id=board_id)
    board.delete()
    return redirect(reverse('taskmaster:index'))

@login_required
def edit_list(request, list_id):
    """
    Edit a task list. Currently, you can edit the name and if the list is for finished tasks or not.
    """
    task_list = TaskList.objects.get(id=list_id)
    if request.method == 'POST':
        form = EditTaskListForm(request.POST)
        if form.is_valid():
            new_list_name: str = form.cleaned_data.get('list_name')
            finished_tasks_list: bool = form.cleaned_data.get('list_for_finished_tasks')

            if new_list_name == '':
                form.add_error('list_name', 'List name cannot be empty.')
            elif TaskList.objects.filter(list_name=new_list_name, list_board=task_list.list_board).exists() and new_list_name != task_list.list_name:
                form.add_error('list_name', 'A list with this name already exists.')

            if form.errors:
                return render(request, 'taskmaster/edit-task-list.html', {'list': task_list, 'form': form})

            task_list.list_name = new_list_name
            task_list.list_for_finished_tasks = finished_tasks_list
            task_list.save()

        return redirect(reverse('taskmaster:display_board', args=(task_list.list_board.id, )))
    return render(request, 'taskmaster/edit-task-list.html', {'list': task_list,
                                                              'form': EditTaskListForm(instance=task_list)})