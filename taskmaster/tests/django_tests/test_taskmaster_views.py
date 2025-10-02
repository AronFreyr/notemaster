from django.test.testcases import TestCase
from taskmaster.models import TaskBoard, TaskList, Task
from notes.models import Tag
from django.urls import reverse
from django.contrib.auth.models import User


class EditTaskViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_pass')
        self.board = TaskBoard.objects.create(board_name='Test Board', board_created_by=self.user,
                                              board_last_modified_by=self.user)
        self.task = Task.objects.create(document_name='Test Task', task_board=self.board, task_assigned_to='test_user')
        self.list1 = TaskList.objects.create(list_name='List 1', list_board=self.board)
        self.edit_task_url = reverse('taskmaster:edit_task', kwargs={'task_id': self.task.id})
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

        edit_task3_url = reverse('taskmaster:edit_task', kwargs={'task_id': task3.id})
        response = self.client.post(edit_task3_url, data)
        task3.refresh_from_db()
        task2.refresh_from_db()
        self.assertEqual(task3.task_list, self.list1)
        self.assertEqual(task3.previous_task, task2)
        self.assertIsNone(task3.next_task)
        self.assertIsNone(task2.previous_task)
        self.assertEqual(task2.next_task, task3)

    def test_add_tag_to_task(self):
        data = {
            'document_name': 'Test Task',
            'document_text': 'Test text',
            'task_difficulty': 2,
            'task_importance': 3,
            'tag_name': 'urgent'
        }
        response = self.client.post(self.edit_task_url, data)
        self.task.refresh_from_db()
        self.assertIn('urgent', [tag.tag_name for tag in self.task.get_all_tags()])
        new_tag = Tag.objects.get(tag_name='urgent')
        self.assertIsNotNone(new_tag)
        self.assertEqual(new_tag.tag_type, Tag.TagTypes.NORMAL)
        self.assertRedirects(response, reverse('taskmaster:display_task', kwargs={'task_id': self.task.id}))

    def test_add_parent_task(self):
        parent_task = Task.objects.create(document_name='Parent Task', task_board=self.board)
        data = {
            'document_name': 'Test Task',
            'document_text': 'Test text',
            'task_difficulty': 2,
            'task_importance': 3,
            'parent_task': parent_task.id
        }
        response = self.client.post(self.edit_task_url, data)
        self.task.refresh_from_db()
        self.assertEqual(self.task.parent_task, parent_task)
        self.assertRedirects(response, reverse('taskmaster:display_task', kwargs={'task_id': self.task.id}))

    def test_remove_parent_task(self):
        parent_task = Task.objects.create(document_name='Parent Task', task_board=self.board)
        self.task.parent_task = parent_task
        self.task.save()
        data = {
            'document_name': 'Test Task',
            'document_text': 'Test text',
            'task_difficulty': 2,
            'task_importance': 3,
            'parent_task': ''
        }
        response = self.client.post(self.edit_task_url, data)
        self.task.refresh_from_db()
        self.assertIsNone(self.task.parent_task)
        self.assertRedirects(response, reverse('taskmaster:display_task', kwargs={'task_id': self.task.id}))

    def test_add_improper_parent_task(self):
        # Parent task from another board should not be allowed.
        other_board = TaskBoard.objects.create(board_name='Other Board', board_created_by=self.user,
                                               board_last_modified_by=self.user)
        parent_task = Task.objects.create(document_name='Parent Task', task_board=other_board)
        data = {
            'document_name': 'Test Task',
            'document_text': 'Test text',
            'task_difficulty': 2,
            'task_importance': 3,
            'parent_task': parent_task.id
        }
        response = self.client.post(self.edit_task_url, data)
        self.task.refresh_from_db()
        self.assertIsNone(self.task.parent_task)
        self.assertNotEqual(response.status_code, 302)
        self.assertTemplateUsed(response, 'taskmaster/edit-task.html')

        # Parent task that is the same as the task being edited should not be allowed.
        data['parent_task'] = self.task.id
        response = self.client.post(self.edit_task_url, data)
        self.task.refresh_from_db()
        self.assertIsNone(self.task.parent_task)
        self.assertNotEqual(response.status_code, 302)
        self.assertTemplateUsed(response, 'taskmaster/edit-task.html')

    def test_add_circular_parent_task(self):
        data = {
            'document_name': 'Test Task',
            'document_text': 'Test text',
            'task_difficulty': 2,
            'task_importance': 3
        }

        # Parent task that is a child of the task being edited should not be allowed.
        child_task = Task.objects.create(document_name='Child Task', task_board=self.board, parent_task=self.task)

        # We set that our task has a parent task that is its own child. This should be rejected.
        data['parent_task'] = child_task.id
        self.assertIsNone(self.task.parent_task)
        response = self.client.post(self.edit_task_url, data)
        self.task.refresh_from_db()
        manipulated_task = Task.objects.get(id=self.task.id)
        self.assertIsNone(manipulated_task.parent_task)
        self.assertRedirects(response, reverse('taskmaster:display_task', kwargs={'task_id': self.task.id}))

    def test_add_next_task(self):
        next_task = Task.objects.create(document_name='Next Task', task_board=self.board, task_list=None)
        data = {
            'document_name': 'Test Task',
            'document_text': 'Test text',
            'task_difficulty': 2,
            'task_importance': 3,
            'next_task': next_task.id
        }
        response = self.client.post(self.edit_task_url, data)
        self.task.refresh_from_db()
        self.assertEqual(self.task.next_task, next_task)
        self.assertRedirects(response, reverse('taskmaster:display_task', kwargs={'task_id': self.task.id}))

    def test_remove_next_task(self):
        next_task = Task.objects.create(document_name='Next Task', task_board=self.board, task_list=None)
        self.task.next_task = next_task
        self.task.save()
        data = {
            'document_name': 'Test Task',
            'document_text': 'Test text',
            'task_difficulty': 2,
            'task_importance': 3,
            'next_task': ''
        }
        response = self.client.post(self.edit_task_url, data)
        self.task.refresh_from_db()
        self.assertIsNone(self.task.next_task)
        self.assertRedirects(response, reverse('taskmaster:display_task', kwargs={'task_id': self.task.id}))

    def test_fail_at_making_next_task_the_same_as_previous_task(self):
        next_task = Task.objects.create(document_name='Next Task', task_board=self.board, task_list=None)
        self.task.previous_task = next_task
        self.task.save()
        data = {
            'document_name': 'Test Task',
            'document_text': 'Test text',
            'task_difficulty': 2,
            'task_importance': 3,
            'next_task': next_task.id
        }
        response = self.client.post(self.edit_task_url, data)
        self.task.refresh_from_db()
        self.assertIsNone(self.task.next_task)

