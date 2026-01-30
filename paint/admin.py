from django.contrib import admin
from .models import Files
# Register your models here.

@admin.register(Files)
class File_Admin(admin.ModelAdmin):
    list_display = ('name', 'image',)
    search_fields = ('name', 'image',)
