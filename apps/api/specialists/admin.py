from django.contrib import admin
from .models import SpecialistCategory, Specialist, SpecialistFeedback, Appointment, CommonConsultation, Transaction, \
    Prescription, Hospital


@admin.register(SpecialistCategory)
class SpecialistCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_specialists')
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'gender', 'contact_phone', 'contact_email', 'category', 'status')
    search_fields = ('full_name', 'contact_phone', 'contact_email')
    list_filter = ('gender', 'category', 'status')

admin.site.register(CommonConsultation)
admin.site.register(Hospital)
admin.site.register(Appointment)
admin.site.register(Prescription)
admin.site.register(Transaction)
admin.site.register(SpecialistFeedback)


