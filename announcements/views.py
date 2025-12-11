from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Annonce
from .forms import AnnonceForm

def announcement_list(request):
    announcements = Annonce.objects.all()
    form = AnnonceForm() # For the modal creation if we wanted, but we keep create separate or not? 
                     # Ref: Plan says create is standard page, Edit is modal.
    return render(request, 'announcements/announcement_list.html', {
        'announcements': announcements,
        # We can pass an empty form for potential usage or just rely on separate page for creation as planned
        # However, for consistency, let's keep create as a separate page as per original plan unless user argues.
    })

def announcement_detail(request, pk):
    announcement = get_object_or_404(Annonce, pk=pk)
    return render(request, 'announcements/announcement_detail.html', {'announcement': announcement})

@staff_member_required
def announcement_create(request):
    if request.method == 'POST':
        form = AnnonceForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.auteur = request.user
            announcement.save()
            return redirect('announcements:announcement_list')
    else:
        form = AnnonceForm()
    return render(request, 'announcements/announcement_form.html', {'form': form, 'title': 'Nouvelle Annonce'})

@staff_member_required
def announcement_update(request, pk):
    announcement = get_object_or_404(Annonce, pk=pk)
    data = dict()
    
    if request.method == 'POST':
        form = AnnonceForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            data['html_announcement_list'] = render_to_string('announcements/partials/announcement_item.html', {
                'announcement': announcement,
                'request': request # pass request to check perms in partial
            })
            # Also return the updated detail html if we are on detail page? 
            # For now the user asked for list page with action buttons.
        else:
            data['form_is_valid'] = False
    else:
        form = AnnonceForm(instance=announcement)
        
    context = {'form': form, 'announcement': announcement}
    data['html_form'] = render_to_string('announcements/partials/announcement_form_modal.html',
        context,
        request=request
    )
    return JsonResponse(data)

@staff_member_required
def announcement_delete(request, pk):
    announcement = get_object_or_404(Annonce, pk=pk)
    data = dict()
    if request.method == 'POST':
        announcement.delete()
        data['form_is_valid'] = True
    else:
        context = {'announcement': announcement}
        data['html_form'] = render_to_string('announcements/partials/announcement_confirm_delete_modal.html',
            context,
            request=request
        )
    return JsonResponse(data)
