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