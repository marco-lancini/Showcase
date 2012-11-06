from django.core.files.storage import FileSystemStorage

class MyFileStorage(FileSystemStorage):
    # http://stackoverflow.com/a/8337264/1183090

    # This method is actually defined in Storage
    def get_available_name(self, name):
      return name # simply returns the name passed



#=========================================================================
# https://www.google.it/search?q=BlobField&oq=BlobField
# http://stackoverflow.com/questions/4915397/django-blob-model-field
# http://djangosnippets.org/snippets/1597/
# http://djangosnippets.org/snippets/1669/
# http://djangosnippets.org/snippets/1305/

# import base64
# from django.db import models

# class Base64Field(models.TextField):
#     def contribute_to_class(self, cls, name):
#         if self.db_column is None:
#             self.db_column = name
#         self.field_name = name + '_base64'
#         super(Base64Field, self).contribute_to_class(cls, self.field_name)
#         setattr(cls, name, property(self.get_data, self.set_data))

#     def get_data(self, obj):
#         return base64.decodestring(getattr(obj, self.field_name))

#     def set_data(self, obj, data):
#         setattr(obj, self.field_name, base64.encodestring(data))
#=========================================================================