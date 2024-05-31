from django.db import models
from notes.models import Document
from django.contrib.auth.models import User

class Task(Document):

    task_difficulty = models.IntegerField(default=0)
    task_importance = models.IntegerField(default=0)
    task_assigned_to = models.TextField(blank=True, null=True)

    # Tasks should be in a list, but it is possible for them to not be.
    task_list = models.ForeignKey('TaskList', on_delete=models.SET_NULL, blank=True, null=True)

    # Tasks should always be on a board and will be deleted if a board is deleted.
    task_board = models.ForeignKey('TaskBoard', on_delete=models.CASCADE)

    # The next task in a list.
    next_task = models.ForeignKey('Task', on_delete=models.SET_NULL, blank=True, null=True,
                                  related_name='next_task_in_list')

    # The previous task in a list.
    previous_task = models.ForeignKey('Task', on_delete=models.SET_NULL, blank=True, null=True,
                                      related_name='previous_task_in_list')

    # A task that this task depends upon. It can be null and replaced.
    parent_task = models.ForeignKey('Task', on_delete=models.SET_NULL, blank=True, null=True,
                                    related_name='parent_task_of_task')

    # Deadline for a task. It can be null.
    task_deadline = models.DateTimeField(blank=True, null=True)


class TaskBoard(models.Model):
    """
    A board containing different tasks.
    """

    board_name = models.TextField()
    board_created = models.DateTimeField(auto_now_add=True)
    board_modified = models.DateTimeField(auto_now=True)
    board_created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='board_created_by',
                                            blank=True, null=True)
    board_last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                               related_name='board_last_modified_by', blank=True, null=True)

    def get_all_lists_in_board_in_custom_order(self):
        task_list = self.tasklist_set.filter(previous_list=None).first()
        if not task_list:
            return
        task_list_list = [task_list]
        while task_list.next_list:
            task_list_list.append(task_list.next_list)
            task_list = task_list.next_list
        return task_list_list

    def get_first_task_list_in_custom_order(self):
        return self.tasklist_set.filter(previous_list=None).first()

    def get_last_task_list_in_custom_order(self):
        return self.tasklist_set.filter(next_list=None).first()

    def __str__(self):
        return self.board_name


class TaskList(models.Model):
    """
    A list of tasks on a board. A board can have many lists but not vice versa.
    Examples of lists could be: "In Progress", "Backlog" and such.
    """

    list_name = models.TextField()

    # If a board is deleted then the lists associated with that board are deleted as well.
    list_board = models.ForeignKey('TaskBoard', on_delete=models.CASCADE)

    # The next list on the board.
    next_list = models.ForeignKey('TaskList', on_delete=models.SET_NULL, blank=True, null=True,
                                  related_name='next_list_in_board')

    # The previous list on the board.
    previous_list = models.ForeignKey('TaskList', on_delete=models.SET_NULL, blank=True, null=True,
                                      related_name='previous_list_in_board')

    def __str__(self):
        return self.list_name

    def get_all_tasks_in_list(self):
        return [task for task in self.task_set.all()]

    def get_all_tasks_in_list_alphabetically(self):
        return [task for task in self.task_set.all().order_by('document_name')]

    def get_all_tasks_in_list_by_difficulty(self):
        return [task for task in self.task_set.all().order_by('task_difficulty')][::-1]

    def get_all_tasks_in_list_by_importance(self):
        return [task for task in self.task_set.all().order_by('task_importance')][::-1]

    def get_all_tasks_in_list_in_custom_order(self):

        # There should only be one task in the list with previous_task=None, that would be the first task.
        task = self.task_set.filter(previous_task=None).first()
        if not task:
            return
        task_list = [task]
        while task.next_task:
            if task == task.previous_task or task.next_task == task.previous_task:
                print(f'something is wrong: {task} has the next task: {task.next_task}, and previous task: {task.previous_task}')
                return
            task_list.append(task.next_task)
            task = task.next_task
        return task_list

    def get_first_task_in_custom_order(self):
        return self.task_set.filter(previous_task=None).first()

    def get_last_task_in_custom_order(self):
        return self.task_set.filter(next_task=None).first()
