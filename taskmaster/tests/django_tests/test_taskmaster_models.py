from django.utils import timezone
from django.test.testcases import TestCase
from taskmaster.models import Task, TaskBoard, TaskList


class TaskCreationTests(TestCase):


    def setUp(self):
        self.board = TaskBoard.objects.create(board_name="Project Alpha", board_created_by=None, board_last_modified_by=None)
        self.list_todo = TaskList.objects.create(list_name="To Do", list_board=self.board,
                                                 list_for_finished_tasks=False)
        self.list_done = TaskList.objects.create(list_name="Done", list_board=self.board,
                                                 list_for_finished_tasks=True)

    def test_create_task(self):
        current_date_and_time = timezone.now()
        task = Task.objects.create(document_name="Design UI", document_text="Create initial UI designs",
                                   task_list=self.list_todo, task_board=self.board,
                                   document_created_by=None, document_last_modified_by=None)
        self.assertEqual(task.document_name, "Design UI")
        self.assertEqual(task.document_text, "Create initial UI designs")
        self.assertEqual(task.task_finished, False)
        self.assertEqual(task.document_created.date(), current_date_and_time.date())
        self.assertEqual(task.document_modified.date(), current_date_and_time.date())
        self.assertEqual(task.task_list, self.list_todo)

    def test_finish_task_on_save(self):
        """ Task that moves to a list meant for finished tasks should automatically be marked as finished."""
        task = Task.objects.create(document_name="Set up database", document_text="Install and configure PostgreSQL",
                                   task_list=self.list_todo, task_board=self.board,
                                   document_created_by=None, document_last_modified_by=None)
        self.assertFalse(task.task_finished)
        task.task_list = self.list_done
        task.save()
        self.assertTrue(task.task_finished)

    def test_unfinish_task_on_save(self):
        """ Task that moves out of a list meant for finished tasks should automatically be marked as unfinished."""
        task = Task.objects.create(document_name="Write tests", document_text="Create unit tests for models",
                                   task_list=self.list_done, task_board=self.board,
                                   document_created_by=None, document_last_modified_by=None,
                                   task_finished=True)
        self.assertTrue(task.task_finished)
        task.task_list = self.list_todo
        task.document_text = "Create unit and integration tests for models"
        task.save()
        self.assertFalse(task.task_finished)
        self.assertEqual(task.document_text, "Create unit and integration tests for models")