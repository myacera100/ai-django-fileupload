import json

from django.http import HttpResponse

from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from django.views.generic import CreateView, DeleteView, ListView

# MOD: import authentication scheme from DRF instead
from rest_framework.permissions import IsAuthenticated, AllowAny
# from fileupload.mixins import CustomAccessMixin

# MOD: import `AttachmentSerializer` instead
from .serializers import AttachmentSerializer

from .models import Attachment
from .response import JSONResponse, response_mimetype

# MOD: import overwritten `serialize` from mod module
from .thumbnail import serialize, cleanup_attachment
# from .serialize import serialize

# MOD: the following CRUD view classes are modified to adapt DRF
class AttachmentCreateView(CreateAPIView):
    # permission_classes = (IsAuthenticated,)
    serializer_class = AttachmentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        files = [serialize(self.object)]
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        # response = HttpResponse(json.dumps(data), content_type="application/json")
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    def perform_create(self, serializer):
        self.object = serializer.save()


# class AttachmentCreateView(CustomAccessMixin, CreateView):
#     model = Attachment
#     fields = "__all__"
#
#     def form_valid(self, form):
#         self.object = form.save()
#         files = [serialize(self.object)]
#         data = {'files': files}
#         response = JSONResponse(data, mimetype=response_mimetype(self.request))
#         # response = HttpResponse(json.dumps(data), content_type="application/json")
#         response['Content-Disposition'] = 'inline; filename=files.json'
#         return response
#
#     def form_invalid(self, form):
#         data = json.dumps(form.errors)
#         return HttpResponse(content=data, status=400, content_type='application/json')
#
#
class AttachmentDeleteView(DestroyAPIView):
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    serializer_class = AttachmentSerializer

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        cleanup_attachment(self.object)
        self.object.delete()
        response = JSONResponse(True, mimetype=response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    # def check_object_permissions(self, request, obj):
        # super().check_object_permissions(request, obj)
        # if obj:
        #     if request.user == obj.created_by:
        #         self.permission_denied(request,
        #                                message='only uploader of the attachment can delete it',
        #                                code=403)

    def get_queryset(self):
        return Attachment.objects.all()


# class AttachmentDeleteView(CustomAccessMixin, DeleteView):
#     model = Attachment
#
#     def delete(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         self.object.delete()
#         response = JSONResponse(True, mimetype=response_mimetype(request))
#         response['Content-Disposition'] = 'inline; filename=files.json'
#         return response
#
#
class AttachmentListView(ListAPIView):
    # permission_classes = (IsAuthenticated,)
    serializer_class = AttachmentSerializer

    def get_queryset(self):
        return Attachment.objects.all()

    def list(self, request, *args, **kwargs):
        files = [
            serialize(p) for p in
            self.get_queryset().filter(content_type=self.request.GET['content_type_id'],
                                       object_id=self.request.GET['object_id'])
        ]

        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


# class AttachmentListView(CustomAccessMixin, ListView):
#     model = Attachment
#
#     def render_to_response(self, context, **response_kwargs):
#         files = [serialize(p) for p in self.get_queryset().filter(content_type=self.request.GET['content_type_id'],
#                                                                   object_id=self.request.GET['object_id'])]
#
#         data = {'files': files}
#         response = JSONResponse(data, mimetype=response_mimetype(self.request))
#         response['Content-Disposition'] = 'inline; filename=files.json'
#         return response
