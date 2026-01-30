from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
import psycopg2

from django.shortcuts import render
from .models import Files
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from wsgiref.util import FileWrapper
import json
import io

# generate the file
@csrf_exempt
def paint(request):
    if request.method == 'GET':
        return render(request, 'paint.html')
    elif request.method == 'POST':

        post_data = json.loads(request.body.decode("utf-8"))
        ret = FileResponse(post_data["image"], filename=post_data["filename"], as_attachment=True,)
        #ret['Content-Disposition'] = 'attachment; filename=myfile.tgz'
        return ret
        response = HttpResponse(mimetype='image/png')
        response['Content-Disposition'] = 'attachment; filename=%s.png' % filename

        return HttpResponse(post_data["image"], content_type="image/jpeg", )

        # filename = request.POST['save_fname']
        # data = request.POST['save_cdata']
        # image = request.POST['save_image']
        # file_data = Files(name=filename, image=data, canvas_image=image)
        # response = HttpResponse(FileWrapper(file_data), content_type='application/zip')
        # response['Content-Disposition'] = 'attachment; filename=myfile.zip'
        # return response


@csrf_exempt
def files(request):
    if request.method == 'GET':
        all_data = Files.objects.all()
        return render(request, 'files.html', {'files': all_data})


def search(request):
    if 'filename' in request.GET:
        filename = request.GET['filename']
        datafile = Files.objects.get(name=filename)
        return render(request, 'search.html', {'data': datafile.canvas_image, 'filename': filename})


@csrf_exempt
def download_image(request):
    print (request.body)
    #data = json.loads(request.body.decode("utf-8"))
    #if data:
        #img = data["image"]
        #nom = data["nom"]
        #ret = FileResponse(img, filename=nom, as_attachment=True,)
        #return ret

    binary_io = io.BytesIO(request.body)
    response = FileResponse(binary_io)
    response['Content-Type'] = 'application/x-binary'
    response['Content-Disposition'] = 'attachment; filename="%s.png"' % data["nom"]  # You can set custom filename, which will be visible for clients.
    return response
    response = HttpResponse(FileWrapper(img), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s.png' % nom
    return response
    return HttpResponse()
