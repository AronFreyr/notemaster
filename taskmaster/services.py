from taskmaster.models import TaskBoard, TaskList, Task


def move_task_up(task_to_move: Task) -> Task:
    if task_to_move.previous_task:  # If it is not the top (oldest) task.
        prev_task = task_to_move.previous_task
        prev_prev_task = prev_task.previous_task
        if prev_prev_task:
            prev_prev_task.next_task = task_to_move
            prev_prev_task.save()
        next_next_task = task_to_move.next_task
        if next_next_task:
            next_next_task.previous_task = prev_task
            next_next_task.save()
        prev_task.next_task = task_to_move.next_task
        task_to_move.next_task = prev_task
        task_to_move.previous_task = prev_task.previous_task
        prev_task.previous_task = task_to_move
        prev_task.save()
        task_to_move.save()

    return task_to_move


def move_task_down(task_to_move: Task) -> Task:

    if task_to_move.next_task:  # If it is not the bottom (newest) task.
        prev_task = task_to_move
        task_to_move = task_to_move.next_task
        prev_prev_task = prev_task.previous_task
        if prev_prev_task:
            prev_prev_task.next_task = task_to_move
            prev_prev_task.save()
        next_next_task = task_to_move.next_task
        if next_next_task:
            next_next_task.previous_task = prev_task
            next_next_task.save()
        prev_task.next_task = task_to_move.next_task
        task_to_move.next_task = prev_task
        task_to_move.previous_task = prev_task.previous_task
        prev_task.previous_task = task_to_move
        prev_task.save()
        task_to_move.save()

    return task_to_move


def move_list_left(list_to_move: TaskList) -> TaskList:
    if list_to_move.previous_list:  # If it is not the top (oldest) list.
        prev_list = list_to_move.previous_list
        prev_prev_list = prev_list.previous_list
        if prev_prev_list:
            prev_prev_list.next_list = list_to_move
            prev_prev_list.save()
        next_next_list = list_to_move.next_list
        if next_next_list:
            next_next_list.previous_list = prev_list
            next_next_list.save()
        prev_list.next_list = list_to_move.next_list
        list_to_move.next_list = prev_list
        list_to_move.previous_list = prev_list.previous_list
        prev_list.previous_list = list_to_move
        prev_list.save()
        list_to_move.save()

    return list_to_move

def move_list_right(list_to_move: TaskList) -> TaskList:
    if list_to_move.next_list:  # If it is not the bottom (newest) list.
        prev_list = list_to_move
        list_to_move = list_to_move.next_list
        prev_prev_list = prev_list.previous_list
        if prev_prev_list:
            prev_prev_list.next_list = list_to_move
            prev_prev_list.save()
        next_next_list = list_to_move.next_list
        if next_next_list:
            next_next_list.previous_list = prev_list
            next_next_list.save()
        prev_list.next_list = list_to_move.next_list
        list_to_move.next_list = prev_list
        list_to_move.previous_list = prev_list.previous_list
        prev_list.previous_list = list_to_move
        prev_list.save()
        list_to_move.save()

    return list_to_move