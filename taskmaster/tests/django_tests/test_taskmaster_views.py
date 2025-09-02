from django.test.testcases import TestCase
from taskmaster.models import TaskBoard, TaskList, Task
from django.urls import reverse
from django.contrib.auth.models import User


class EditTaskViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_pass')
        self.board = TaskBoard.objects.create(board_name='Test Board', board_created_by=self.user,
                                              board_last_modified_by=self.user)
        self.task = Task.objects.create(document_name='Test Task', task_board=self.board, task_assigned_to='test_user')
        self.list1 = TaskList.objects.create(list_name='List 1', list_board=self.board)
        self.edit_task_url = reverse('taskmaster:edit_task_2', kwargs={'task_id': self.task.id})
        self.client.login(username='test_user', password='test_pass')

    def test_edit_task_get(self):
        response = self.client.get(self.edit_task_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'taskmaster/edit-task.html')

    def test_edit_task_post_success(self):
        data = {
            'document_name': 'Updated Task',
            'document_text': 'Updated text',
            'task_difficulty': 3,
            'task_importance': 4
        }
        response = self.client.post(self.edit_task_url, data)
        self.task.refresh_from_db()
        self.assertEqual(self.task.document_name, 'Updated Task')
        self.assertEqual(self.task.document_text, 'Updated text')
        self.assertEqual(self.task.task_difficulty, 3)
        self.assertEqual(self.task.task_importance, 4)
        self.assertRedirects(response, reverse('taskmaster:display_task', kwargs={'task_id': self.task.id}))

    def test_edit_task_by_moving_to_new_list(self):
        list2 = TaskList.objects.create(list_name='List 2', list_board=self.board, previous_list=self.list1)
        self.list1.next_list = list2
        self.list1.save()

        task2 = Task.objects.create(document_name='Task 2', task_board=self.board, task_list=self.list1,
                                    previous_task=None, next_task=None)
        task3 = Task.objects.create(document_name='Task 3', task_board=self.board, task_list=list2,
                                    previous_task=None, next_task=None)

        # We move task3 to from list2 to list1.
        # This should make task3 the next task of task2 and task2 the previous task of task3.
        data = {
            'document_name': 'Task 3',
            'document_text': '',
            'task_list': self.list1.id,
            'task_difficulty': 3,
            'task_importance': 4,
        }

        edit_task3_url = reverse('taskmaster:edit_task_2', kwargs={'task_id': task3.id})
        response = self.client.post(edit_task3_url, data)
        task3.refresh_from_db()
        task2.refresh_from_db()
        self.assertEqual(task3.task_list, self.list1)
        self.assertEqual(task3.previous_task, task2)
        self.assertIsNone(task3.next_task)
        self.assertIsNone(task2.previous_task)
        self.assertEqual(task2.next_task, task3)
