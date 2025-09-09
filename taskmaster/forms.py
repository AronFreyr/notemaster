from django import forms
from taskmaster.models import Task, TaskList

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