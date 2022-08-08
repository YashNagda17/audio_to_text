from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from chat import models
from chat import tasks

@require_http_methods(['GET', 'POST'])
def home(request):
    try:
        if request.method == 'GET':
            samples = models.AudioDataModel.objects.all()
            pending_jobs = models.AudioDataModel.objects.filter(status='PEN').count()
            show_timer = False
            if pending_jobs > 0:
                show_timer = True
            return render(request, 'base.html', {'samples': samples, 'show_timer': show_timer})
        uploaded_file = request.FILES['uploaded_file']
        audio_data = models.AudioDataModel.objects.create(uploaded_file=uploaded_file)
        tasks.process_uploaded_file.delay(audio_data.id)
        return HttpResponseRedirect('/')
    except Exception as e:
        audio_data.status = 'ERR'
        audio_data.error_occurred = True
        audio_data.error_message = str(e)
        audio_data.save()
        return HttpResponse(f'Error: {str(e)}')


