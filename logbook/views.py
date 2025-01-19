from django.shortcuts import render, redirect, reverse

from .forms import CreateDiaryEntryForm
from .models import DiaryEntry
from notes.services.object_handling import handle_new_tag

# Create your views here.


def index(request):

    all_entries = DiaryEntry.objects.all().order_by('-entry_date')

    return render(request, 'logbook/index.html',
                  {'all_entries': all_entries})


def display_entry(request, entry_id):
    entry = DiaryEntry.objects.get(id=entry_id)

    return render(request, 'logbook/display-diary-entry.html',
                  {'entry': entry})


def display_all_entries(request):
    all_entries = DiaryEntry.objects.all().order_by('-entry_date')

    return render(request, 'logbook/display-all-entries.html',
                  {'all_entries': all_entries})


def create_entry(request):
    if request.method == 'POST':
        create_diary_entry_form = CreateDiaryEntryForm(request.POST)
        if create_diary_entry_form.is_valid():
            entry_date = create_diary_entry_form.cleaned_data['entry_date']
            if DiaryEntry.objects.filter(entry_date=entry_date).exists():
                return render(request, 'logbook/create-diary-entry.html',
                              {'create_diary_entry_form': create_diary_entry_form,
                               'error_message': 'An entry for this date already exists. Please choose another date.'})
            new_diary_entry = create_diary_entry_form.save(commit=False)
            new_diary_entry.document_name = (f'Diary Entry {new_diary_entry.entry_date}'
                                             f'-{request.user}-{request.user.id}')
            new_diary_entry.document_created_by = request.user
            new_diary_entry.save()
            diary_tags = create_diary_entry_form.cleaned_data['new_tag']
            if diary_tags:
                handle_new_tag(new_tags=diary_tags, new_doc=new_diary_entry, tag_creator=request.user)
            return redirect(reverse('logbook:index'))

    return render(request, 'logbook/create-diary-entry.html',
                  {'create_diary_entry_form': CreateDiaryEntryForm()})

