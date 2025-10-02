from django import forms
from taskmaster.models import Task, TaskList
from django.contrib.auth.models import User
from tinymce.widgets import TinyMCE

class AddBoardForm(forms.Form):

    board_name = forms.CharField(label='Input name of new board here:')

    class Meta:
        fields = ['board_name']


class CreateTaskListForm(forms.Form):

    list_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'List Name'}),
                                label='New task list:')

    class Meta:
        fields = ['list_name']

class EditTaskListForm(forms.ModelForm):

    list_name = forms.CharField(label='List name:', required=True)
    list_for_finished_tasks = forms.BooleanField(label='Is this list for finished tasks?', required=False)

    class Meta:
        model = TaskList
        fields = ['list_name', 'list_for_finished_tasks']


class CreateTaskMiniForm(forms.ModelForm):
    """
    Creates tasks, but you only need to input the task name.
    """
    task_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Task Name'}), required=True, label=False)
    task_text = forms.CharField(widget=forms.HiddenInput(), required=False)
    task_difficulty = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    task_importance = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    task_assigned_to = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Task
        fields = [
            'task_name',
            'task_text',
            'task_difficulty',
            'task_importance',
            'task_assigned_to'
        ]


class CreateTaskForm(forms.ModelForm):

    task_name = forms.CharField(label='Task name:', required=True)
    task_text = forms.CharField(label='Task text:', required=False)
    task_assigned_to = forms.CharField(label='assigned to:', required=False)
    class Meta:
        model = Task
        fields = [
            'task_name',
            'task_text',
            'task_difficulty',
            'task_importance',
            'task_assigned_to'
        ]
    #
    # def __init__(self, *args, **kwargs):
    #     super(TaskForm, self).__init__(*args, **kwargs)
    #     # Customizing form fields if necessary
    #     self.fields['task_difficulty'].widget = forms.NumberInput(attrs={'min': 0, 'max': 10})
    #     self.fields['task_importance'].widget = forms.NumberInput(attrs={'min': 0, 'max': 10})
    #     self.fields['task_assigned_to'].widget = forms.TextInput(attrs={'placeholder': 'Assigned to...'})


class TaskForm(forms.ModelForm):
    """
    Form for creating and editing tasks.
    """
    document_name = forms.CharField(label='Task name:', required=True)
    document_text = forms.CharField(label='', required=False,
                                    widget=TinyMCE(mce_attrs={'width': '700px', 'height': '400px'}))
    task_assigned_to = forms.ModelChoiceField(label='Assigned to:', required=False, queryset=User.objects.all(), empty_label=None)
    task_deadline = forms.DateField(label='Task deadline:', required=False,
                                    widget=forms.DateInput(attrs={'type': 'date'}),
                                    initial=None)
    task_board = forms.CharField(label='Task board:', required=False, disabled=True)

    parent_task = forms.ModelChoiceField(label='Parent task:', required=False, queryset=Task.objects.none(),
                                         empty_label='No parent task')

    class Meta:
        model = Task
        fields = [
            'document_name',
            'document_text',
            'task_difficulty',
            'task_importance',
            'task_list',
            #'task_board',
            'next_task',
            'previous_task',
            'parent_task',
            'task_deadline',
        ]

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        curr_instance: Task = kwargs.get('instance')  # The task being edited.
        if curr_instance:
            # We restrict the next_task, previous_task, and parent_task fields to only show tasks
            # that are in the same list and on the same board as the task being edited.
            # Note: parent_task can be from any list on the same board.
            task_list = curr_instance.task_list
            task_board = curr_instance.task_board
            self.fields['next_task'].queryset = Task.objects.filter(
                task_list=task_list,
                task_board=task_board
            ).exclude(pk=curr_instance.pk)
            self.fields['previous_task'].queryset = Task.objects.filter(
                task_list=task_list,
                task_board=task_board
            ).exclude(pk=curr_instance.pk)
            self.fields['parent_task'].queryset = Task.objects.filter(
                task_board=task_board
            ).exclude(pk=curr_instance.pk)
            # This is supposedly a way to make the dropdown show the document_name of the task instead of "Task object (1)".
            self.fields['parent_task'].label_from_instance = lambda obj: obj.document_name

            self.fields['task_board'].initial = str(curr_instance.task_board)

            # We make lists only show lists that are on the same board as the task being edited.
            self.fields['task_list'].queryset = curr_instance.task_board.get_all_lists_in_board_in_custom_order_queryset()
            self.fields['task_list'].empty_label = None

            self.fields['task_assigned_to'].initial = User.objects.filter(username=curr_instance.task_assigned_to).first()
        else:
            self.fields['task_board'].initial = ''
            self.fields['next_task'].queryset = Task.objects.none()
            self.fields['previous_task'].queryset = Task.objects.none()
            self.fields['parent_task'].queryset = Task.objects.none()

        # This gives the parent_task a field that limits it's size as defined in the edit-task.css.
        self.fields['parent_task'].widget.attrs.update({'class': 'select-block'})
        self.fields['next_task'].widget.attrs.update({'class': 'select-block'})
        self.fields['previous_task'].widget.attrs.update({'class': 'select-block'})
        self.fields['task_assigned_to'].widget.attrs.update({'class': 'select-block'})
        self.fields['task_list'].widget.attrs.update({'class': 'select-block'})
        self.fields['task_importance'].widget.attrs.update({'class': 'select-block'})
        self.fields['task_difficulty'].widget.attrs.update({'class': 'select-block'})
        self.fields['document_name'].widget.attrs.update({'class': 'task-name-input'})
