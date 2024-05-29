from django.views.decorators.http import require_safe
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse

from notes.models import Document
from taskmaster.models import TaskBoard, TaskList, Task
from taskmaster.forms import AddBoardForm, CreateTaskListForm, CreateTaskForm, CreateTaskMiniForm
from taskmaster import services

@require_safe
@login_required
def index(request):

    tasks = Document.objects.filter(tagmap__tag__tag_name='taskmaster_task').all()
    backlog = tasks.filter(tagmap__tag__tag_name='taskmaster_backlog').all()
    in_progress = tasks.filter(tagmap__tag__tag_name='taskmaster_in_progress').all()

    boards = TaskBoard.objects.all()

    return render(request, 'taskmaster/index.html',
                  {'tasks': tasks,
                          'backlog': backlog,
                          'in_progress': in_progress,
                   'boards': boards})


@login_required
def create_board(request):
    if request.method == 'GET':
        return render(request, 'taskmaster/create-task-board.html',
                      {'create_board_form': AddBoardForm()}
        )
    if request.method == 'POST':
        form = AddBoardForm(request.POST)
        if form.is_valid():
            board_name = form.cleaned_data.get('board_name')
            if not TaskBoard.objects.filter(board_name=board_name).exists():
                new_board = TaskBoard(board_name=board_name, board_created_by=request.user,
                                      board_last_modified_by=request.user)
                new_board.save()
                return redirect(reverse('taskmaster:display_board', args=(board_name, )))
            else:
                #TODO: decide how to handle when name is already taken?
                pass

    return redirect(reverse('taskmaster:index'))


@login_required
def display_board(request, board_id):
    board = TaskBoard.objects.get(id=board_id)
    board_lists = list(board.tasklist_set.all())
    if request.method == 'GET':

        return render(request, 'taskmaster/display-task-board.html', {'board': board,
                                                                       'board_lists': board_lists,
                                                                       'create_board_list_form': CreateTaskListForm(),
                                                                      'create_task_form': CreateTaskMiniForm()})

    if request.method == 'POST':
        list_form = CreateTaskListForm(request.POST)
        task_form = CreateTaskMiniForm(request.POST)
        if list_form.is_valid():
            list_name = list_form.cleaned_data.get('list_name')
            if not TaskList.objects.filter(list_name=list_name, list_board=board).exists():
                last_list = board.tasklist_set.all().last()

                new_list = TaskList(list_name=list_name, list_board=board)
                if last_list:
                    last_list.next_list = new_list
                    new_list.previous_list = last_list
                    new_list.save()
                    last_list.save()
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

            new_task = Task(document_name=task_name, document_text=task_text, task_difficulty=task_difficulty,
                            task_importance=task_importance, task_assigned_to=task_assigned_to,
                            task_list=current_list, task_board=board,
                            document_created_by=request.user, document_last_modified_by=request.user)

            task_list = current_list.get_all_tasks_in_list_by_custom_order()
            new_task.save()  # Save the task immediately so that it exists in the database for last_task.

            if task_list:
                last_task = task_list[-1]
                last_task.next_task = new_task
                last_task.save()
                new_task.previous_task = last_task
                new_task.save()

        if 'move_task_up' in request.POST:
            task_to_move_id = request.POST['task_to_move']
            task_to_move = Task.objects.get(id=task_to_move_id)
            moved_task = services.move_task_up(task_to_move)
        if 'move_task_down' in request.POST:
            task_to_move_id = request.POST['task_to_move']
            task_to_move = Task.objects.get(id=task_to_move_id)
            moved_task = services.move_task_down(task_to_move)

        return render(request, 'taskmaster/display-task-board.html', {'board': board,
                                                                      'board_lists': board_lists,
                                                                      'create_board_list_form': CreateTaskListForm(),
                                                                      'create_task_form': CreateTaskMiniForm()})


@login_required
def display_task(request, task_id):
    task = Task.objects.get(id=task_id)
    return render(request, 'taskmaster/display-task.html', {'task': task})

@login_required
def edit_task(request, task_id):
    task = Task.objects.get(id=task_id)
    if request.method == 'POST':

        if 'name_textarea_edit_task_text' in request.POST:
            new_task_text = request.POST['name_textarea_edit_task_text']
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

        if 'name_list_dropdown' in request.POST:
            new_list = request.POST['name_list_dropdown']
            old_task_list = task.task_list  # The old list that the task used to belong to.
            # The new list the task belongs to.
            new_task_list = TaskList.objects.get(list_name=new_list, list_board=task.task_board)
            prev_task = task.previous_task
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

    all_tasks_in_same_list = task.task_list.get_all_tasks_in_list()
    all_tasks_in_same_list.append({'document_name': None})
    return render(request, 'taskmaster/edit-task.html', {'task': task,
                                                         'tasks_in_list': all_tasks_in_same_list})


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
    list_to_delete.delete()
    return redirect(reverse('taskmaster:display_board', args=(list_board_id,)))
