from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse

from .forms import CreateDiaryEntryForm
from .models import DiaryEntry
from notes.services.object_handling import handle_new_tag


@login_required
def index(request):

    all_entries = DiaryEntry.objects.all().order_by('-entry_date')

    return render(request, 'logbook/index.html',
                  {'all_entries': all_entries})


@login_required
def display_entry(request, entry_id):
    entry = DiaryEntry.objects.get(id=entry_id)

    return render(request, 'logbook/display-diary-entry.html',
                  {'entry': entry})


@login_required
def display_all_entries(request):
    all_entries = DiaryEntry.objects.all().order_by('-entry_date')

    return render(request, 'logbook/display-all-entries.html',
                  {'all_entries': all_entries})


@login_required
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


@login_required
def edit_entry(request, entry_id):

    entry_to_edit = DiaryEntry.objects.get(id=entry_id)
    old_tags = entry_to_edit.get_all_tags_sorted()
    if request.method == 'POST':
        edit_diary_entry_form = CreateDiaryEntryForm(request.POST, instance=entry_to_edit)
        if edit_diary_entry_form.is_valid():
            if DiaryEntry.objects.filter(entry_date=edit_diary_entry_form.cleaned_data['entry_date']).exists():
                if DiaryEntry.objects.filter(entry_date=edit_diary_entry_form.cleaned_data['entry_date']) \
                .first().id != entry_id:
                    return render(request, 'logbook/edit-diary-entry.html',
                                  {'edit_diary_entry_form': edit_diary_entry_form,
                                   'entry': entry_to_edit,
                                   'error_message': 'An entry for this date already exists. Please choose another date.'})

            diary_tags = edit_diary_entry_form.cleaned_data['new_tag']
            # TODO: all tags that are in the old tags but not in the new tags should be removed.
            if diary_tags:
                handle_new_tag(new_tags=diary_tags, new_doc=entry_to_edit, tag_creator=request.user)
            edit_diary_entry_form.save()
            return redirect(reverse('logbook:display_entry', args=[entry_id]))

    return render(request, 'logbook/edit-diary-entry.html',
                  {'edit_diary_entry_form': CreateDiaryEntryForm(instance=entry_to_edit),
                   'entry': entry_to_edit})


@login_required
def delete_entry(request, entry_id):
    entry_to_delete = DiaryEntry.objects.get(id=entry_id)
    entry_to_delete.delete()
    return redirect(reverse('logbook:index'))