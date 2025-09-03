from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_safe
from django.shortcuts import render, redirect, reverse, get_object_or_404

from .forms import CreateDiaryEntryForm
from .models import DiaryEntry
from notes.models import Tag
from notes.services.object_handling import handle_new_tag


@login_required
def index(request):

    all_entries = DiaryEntry.objects.filter(document_created_by=request.user).order_by('-entry_date')
    return render(request, 'logbook/index.html',
                  {'all_entries': all_entries})


@login_required
def display_entry(request, entry_id):
    entry = get_object_or_404(DiaryEntry, id=entry_id, document_created_by=request.user)
    return render(request, 'logbook/display-diary-entry.html',
                  {'entry': entry})


@login_required
def display_all_entries(request):
    all_entries = DiaryEntry.objects.filter(document_created_by=request.user).order_by('-entry_date')

    # group entries based on month and year
    grouped_entries = {}
    for entry in all_entries:
        year = entry.entry_date.strftime('%Y')
        if year not in grouped_entries:
            grouped_entries[year] = {}
        month = entry.entry_date.strftime('%B')
        if month not in grouped_entries[year]:
            grouped_entries[year][month] = []
        grouped_entries[year][month].append(entry)

    return render(request, 'logbook/display-all-entries.html',
                  {'grouped_entries': grouped_entries})


@login_required
@require_safe
def display_entries_by_tag(request, tag_id):
    tag = Tag.objects.filter(id=tag_id).first()
    if not tag:
        # TODO: log
        print(f'No tag found with id {tag_id} for user {request.user}. Redirecting to index.')
        return redirect(reverse('logbook:index'))
    entries = DiaryEntry.objects.filter(document_created_by=request.user, tagmap__tag__id=tag.id).order_by('-entry_date')
    return render(request, 'logbook/index.html',
                  {'all_entries': entries, 'filtered_by_tag': tag})


@login_required
def create_entry(request):
    if request.method == 'POST':
        create_diary_entry_form = CreateDiaryEntryForm(request.POST)
        if create_diary_entry_form.is_valid():
            entry_date = create_diary_entry_form.cleaned_data['entry_date']
            if DiaryEntry.objects.filter(entry_date=entry_date, document_created_by=request.user).exists():
                return render(request, 'logbook/create-diary-entry.html',
                              {'create_diary_entry_form': create_diary_entry_form,
                               'error_message': 'An entry for this date already exists. Please choose another date.'})
            new_diary_entry = create_diary_entry_form.save(commit=False)
            new_diary_entry.document_name = (f'Diary Entry {new_diary_entry.entry_date}'
                                             f'-{request.user}-{request.user.id}')
            new_diary_entry.document_created_by = request.user
            new_diary_entry.save()
            diary_tags = create_diary_entry_form.cleaned_data['new_tag']

            # All diary entries should have the "Diary Entry" meta-tag.
            handle_new_tag('Diary Entry', new_doc=new_diary_entry,
                           tag_creator=request.user, tag_type=('meta', 'diary_entry'))
            if diary_tags:
                handle_new_tag(new_tags=diary_tags, new_doc=new_diary_entry, tag_creator=request.user)
            return redirect(reverse('logbook:index'))

    return render(request, 'logbook/create-diary-entry.html',
                  {'create_diary_entry_form': CreateDiaryEntryForm()})


@login_required
def edit_entry(request, entry_id):

    entry_to_edit = get_object_or_404(DiaryEntry, id=entry_id, document_created_by=request.user)
    old_tags = entry_to_edit.get_all_tags_sorted()
    if request.method == 'POST':
        edit_diary_entry_form = CreateDiaryEntryForm(request.POST, instance=entry_to_edit)
        if edit_diary_entry_form.is_valid():
            if DiaryEntry.objects.filter(entry_date=edit_diary_entry_form.cleaned_data['entry_date'],
                                         document_created_by=request.user).exists():
                if DiaryEntry.objects.filter(entry_date=edit_diary_entry_form.cleaned_data['entry_date'],
                                             document_created_by=request.user) \
                .first().id != entry_id:
                    return render(request, 'logbook/edit-diary-entry.html',
                                  {'edit_diary_entry_form': edit_diary_entry_form,
                                   'entry': entry_to_edit,
                                   'error_message': 'An entry for this date already exists. Please choose another date.'})

            diary_tags = edit_diary_entry_form.cleaned_data['new_tag']
            if diary_tags:
                handle_new_tag(new_tags=diary_tags, new_doc=entry_to_edit, tag_creator=request.user)
            edit_diary_entry_form.save()
            return redirect(reverse('logbook:display_entry', args=[entry_id]))

    return render(request, 'logbook/edit-diary-entry.html',
                  {'edit_diary_entry_form': CreateDiaryEntryForm(instance=entry_to_edit),
                   'entry': entry_to_edit})


@login_required
def delete_entry(request, entry_id):
    entry_to_delete = get_object_or_404(DiaryEntry, id=entry_id, document_created_by=request.user)
    entry_to_delete.delete()
    return redirect(reverse('logbook:index'))