from django.db.models.signals import post_delete
from django.dispatch import receiver
from appauth.models.funnel import Funnel, FunnelTemplate, Page

import shutil, os

@receiver(post_delete, sender=Funnel)
@receiver(post_delete, sender=FunnelTemplate)
def delete_funnel(sender, instance, **kwargs):
    # delete associated filed
    base = instance.base_folder()
    shutil.rmtree(base, ignore_errors=True, onerror=None)

    # delete associated pages
    ftype = "public" if instance.label == "funnel" else "template"
    pages = Page.objects.filter(funnel_id=instance.id, funnel_type=ftype)
    pages.delete()

@receiver(post_delete, sender=Page)
def delete_page(sender, instance, **kwargs):
    filename = instance.base_file()
    os.remove(filename)