from django.test.testcases import TestCase
from taskmaster.models import Task, TaskList, TaskBoard


class TaskCreationTests(TestCase):

    def test_create_task_board(self):
        TaskBoard.objects.create(board_name='my test taskboard')
        my_board = TaskBoard.objects.get(board_name='my test taskboard')
        self.assertEqual(my_board.board_name, 'my test taskboard')

    def test_create_task_board_and_list(self):
        TaskBoard.objects.create(board_name='my test taskboard')
        my_board = TaskBoard.objects.get(board_name='my test taskboard')

        TaskList.objects.create(list_name='my test task list', list_board=my_board)

        my_list = TaskList.objects.get(list_name='my test task list')

        self.assertEqual(my_list.list_name, 'my test task list')
        self.assertIsNone(my_list.next_list)
        self.assertIsNone(my_list.previous_list)

    def test_create_task_board_and_list_and_task(self):
        TaskBoard.objects.create(board_name='my test taskboard')
        my_board = TaskBoard.objects.get(board_name='my test taskboard')

        TaskList.objects.create(list_name='my test task list', list_board=my_board)

        my_list = TaskList.objects.get(list_name='my test task list')

        my_task = Task.objects.create(document_name='my test task', document_text='my test task text',
                                      task_board=my_board)

        self.assertEqual(my_task.document_name, 'my test task')
        self.assertIsNone(my_task.task_list)
        my_task.task_list = my_list
        my_task.save()
        self.assertIsNotNone(my_task.task_list)
