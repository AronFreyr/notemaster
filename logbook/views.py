from django.shortcuts import render, redirect, reverse

from .forms import CreateDiaryEntryForm
from .models import DiaryEntry

# Create your views here.


def index(request):

    all_entries = DiaryEntry.objects.all()

    return render(request, 'logbook/index.html',
                  {'all_entries': all_entries})


def display_entry(request, entry_id):
    entry = DiaryEntry.objects.get(id=entry_id)

    return render(request, 'logbook/display-diary-entry.html',
                  {'entry': entry})


def create_entry(request):
    if request.method == 'POST':
        create_diary_entry_form = CreateDiaryEntryForm(request.POST)
        if create_diary_entry_form.is_valid():
            new_diary_entry = create_diary_entry_form.save(commit=False)
            new_diary_entry.document_created_by = request.user
            new_diary_entry.save()
            return redirect(reverse('logbook:index'))

    return render(request, 'logbook/create-diary-entry.html',
                  {'create_diary_entry_form': CreateDiaryEntryForm()})

