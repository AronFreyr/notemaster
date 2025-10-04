from django.test.testcases import TestCase
from unittest import skip
from taskmaster.models import TaskBoard, TaskList, Task
from taskmaster.forms import AddBoardForm, CreateTaskListForm, EditTaskListForm, CreateTaskMiniForm, CreateTaskForm, TaskForm
from django.contrib.auth.models import User


class CreateTaskFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_pass')
        self.board = TaskBoard.objects.create(board_name='Test Board', board_created_by=None,
                                              board_last_modified_by=None)
        self.list1 = TaskList.objects.create(list_name='List 1', list_board=self.board)
        self.list2 = TaskList.objects.create(list_name='List 2', list_board=self.board)

        self.task1 = Task.objects.create(document_name='Task 1', task_board=self.board)
        self.task2 = Task.objects.create(document_name='Task 2', task_board=self.board)
        self.task3 = Task.objects.create(document_name='Task 3', task_board=self.board)

    def test_add_board_form_valid(self):
        """ You can create a board with just a name. """
        form_data = {'board_name': 'New Project Board'}
        form = AddBoardForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_add_board_form_invalid(self):
        """ The board needs to have a name. """
        form_data = {'board_name': ''}
        form = AddBoardForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('board_name', form.errors)

    def test_create_task_list_form_valid(self):
        """ You can create a list with just a name. """
        form_data = {'list_name': 'New Task List'}
        form = CreateTaskListForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_create_task_list_form_invalid(self):
        """ The list needs to have a name. """
        form_data = {'list_name': ''}
        form = CreateTaskListForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('list_name', form.errors)

    def test_edit_task_list_form_valid(self):
        """ You can use the form to update a list. """
        form_data = {'list_name': 'Updated List Name', 'list_for_finished_tasks': True}
        form = EditTaskListForm(data=form_data, instance=self.list1)
        self.assertTrue(form.is_valid())

    def test_edit_task_list_form_invalid(self):
        """ You can't change the name of a list to be empty. """
        form_data = {'list_name': '', 'list_for_finished_tasks': True}
        form = EditTaskListForm(data=form_data, instance=self.list1)
        self.assertFalse(form.is_valid())
        self.assertIn('list_name', form.errors)

    def test_create_task_mini_form_valid(self):
        """ You can create a task using the mini form. """
        form_data = {
            'task_name': 'Quick Task',
            'task_text': '',
            'task_difficulty': 2,
            'task_importance': 3,
            'task_assigned_to': ''
        }
        form = CreateTaskMiniForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_get_task_form_with_working_next_task_and_previous_task(self):
        """ Next and previous tasks should show up in the form if they are in the same list as the task being edited."""

        task = Task.objects.create(document_name='Task with next task', task_board=self.board, task_list=self.list1,
                                   next_task=self.task2, task_assigned_to=self.user.id, task_difficulty=4,
                                   task_importance=5, task_deadline=None, previous_task=self.task1)

        # Setting up task2 to be in the same list as task_with_next_task
        self.task2.task_list = self.list1
        self.task2.save()

        # Setting up task1 to be in the same list as task_with_next_task
        self.task1.task_list = self.list1
        self.task1.save()

        form = TaskForm(instance=task)

        next_task_field = form.fields['next_task']

        self.assertIn(self.task2, next_task_field.queryset)
        self.assertIn(self.task1, next_task_field.queryset)
        self.assertNotIn(self.task3, next_task_field.queryset)

        previous_task_field = form.fields['previous_task']
        self.assertIn(self.task1, previous_task_field.queryset)
        self.assertIn(self.task2, previous_task_field.queryset)
        self.assertNotIn(self.task3, previous_task_field.queryset)

        # task2 should be the initial value for next_task, since it is set as such in task_with_next_task
        self.assertEqual(form['next_task'].initial, self.task2.pk)
        # task1 should be the initial value for previous_task, since it is set as such in task_with_next_task
        self.assertEqual(form['previous_task'].initial, self.task1.pk)
