import mimetypes
import re
import os
from PIL.Image import Image
from PIL import Image as IM

from django.conf import settings

# MOD: import `ModelSerializer` instead to assume DRF-style
from rest_framework.serializers import ModelSerializer
# from django.forms import ModelForm

from fileupload import constants
from .thumbnail import cleanup_attachment
from .models import Attachment
# from .views import AttachmentCreateView, AttachmentDeleteView


# MOD: serializer instead of form to adapt DRF
class AttachmentSerializer(ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'

    def __init__(self, uploader=None, *args, **kwargs):
        self.uploader = None
        if uploader:
            self.uploader = uploader
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        validated_data.update({
            'created_by': self.uploader,
            'last_modified_by': self.uploader
        })
        return validated_data


# class AttachmentForm(ModelForm):
#     class Meta:
#         model = Attachment
#         fields = '__all__'
#
#     def __init__(self, uploader=None, *args, **kwargs):
#         self.uploader = None
#         if uploader:
#             self.uploader = uploader
#         super(AttachmentForm, self).__init__(*args, **kwargs)
#
#     def clean(self):
#         cleaned_data = super(AttachmentForm, self).clean()
#         cleaned_data.update({
#             'created_by': self.uploader,
#             'last_modified_by': self.uploader
#         })
#         return cleaned_data
#
#
# class AttachmentCreateViewEx(AttachmentCreateView):
#
#     def get_form_class(self):
#         return AttachmentForm
#
#     def get_form_kwargs(self):
#         kwargs = super(AttachmentCreateViewEx, self).get_form_kwargs()
#         kwargs.update({'uploader': self.request.user})
#         return kwargs
#
#
# class AttachmentDeleteViewEx(AttachmentDeleteView):
#
#     def delete(self, request, *args, **kwargs):
#         obj = self.get_object()
#         # Remove thumbnail file before delete the file object
#         cleanup_attachment(obj)
#         return super(AttachmentDeleteViewEx, self).delete(request, *args, **kwargs)
