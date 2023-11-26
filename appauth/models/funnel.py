from pathlib import Path
from django.db import models
from django.utils import timezone
from typing import Union

from back import settings

import uuid, json

class Page(models.Model):
    class Meta:
        db_table = 'pages'
        constraints = [
            models.UniqueConstraint(fields=('funnel_id', 'funnel_type', 'slug'), name='unique_funnel_type_slug'),
        ]

    FUNNEL_TYPE_CHOICES = (
        ("Public", "public",),
        ("Template", "template",),
    )

    uid = models.UUIDField(unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    funnel_id = models.PositiveIntegerField()
    funnel_type = models.CharField(max_length=10, default="public", choices=FUNNEL_TYPE_CHOICES)
    owner = models.ForeignKey('appauth.User', on_delete=models.CASCADE)
    slug = models.SlugField(unique=False)
    published = models.BooleanField(default=True)
    is_index = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def base_file(self) -> Path:
        model = FunnelTemplate if self.funnel_type == "template" else Funnel
        funnel = model.objects.get(id=self.funnel_id)

        page_path = self.uid.hex+".json"
        page_file = funnel.pages_folder() / page_path

        return page_file

    def make_index(self, value: bool= True):
        self.is_index = value
        self.save()

    def load_data(self) -> dict:
        page_file = self.base_file()

        data = None
        with open(page_file, "r") as file:
            data = json.load(file)
            data["title"] = self.name
            data["slug"] = self.slug

        return data

    def save_data(self, data):
        with open(self.base_file(), "w") as bf:
            json.dump(data, bf)

class FunnelAbstract(models.Model):
    class Meta:
        abstract = True

    uid = models.UUIDField(unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    owner = models.ForeignKey('appauth.User', on_delete=models.CASCADE)
    base = models.SlugField(unique=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    label = 'funnel'

    def funnel_type(self):
        return "public" if self.label == "funnel" else self.label

    def base_folder(self) -> Path:
        root = self.label+"s"
        storage: Path = settings.STORAGE_FOLDER / root
        return storage / self.owner.uid.hex / self.uid.hex

    def base_file(self) -> Path:
        return self.base_folder() / "main.json"

    def pages_folder(self) -> Path:
        return self.base_folder() / "pages"
    
    def load_data(self) -> dict:
        main_file = self.base_file()
        data = open(main_file, "r")
        data = json.load(data)

        return data

    def get_index_page(self) -> Union[Page, None]:
        ftype = self.funnel_type()
        pages = Page.objects.filter(funnel_id=self.id, funnel_type=ftype)
        if pages.exists():
            index = pages.filter(is_index=True)
            
            if index.exists():
                return index.first()

            else:
                return pages.first()

    def set_index_page(self, page_slug:str, state: bool):
        funnel_type = self.funnel_type()

        if state:
            index = Page.objects.filter(
                funnel_id=self.id, 
                funnel_type=funnel_type,
            )

            if index.exists():
                for ind in index:
                    ind.is_index = False
                    ind.save()

        new_index = Page.objects.filter(slug=page_slug, funnel_id=self.id, funnel_type=funnel_type).first()
        
        if new_index:
            new_index.is_index = state
            new_index.save()

    def has_page(self, page_slug) -> Union[Page, None]:
        funnel_type = self.funnel_type()

        page = Page.objects.filter(
            slug=page_slug, 
            funnel_type=funnel_type, 
            funnel_id=self.id, 
            owner=self.owner
        )

        return page.first()


    def save_data(self, data):
        with open(self.base_file(), "w") as base_file:
            json.dump(data, base_file)

    def pages(self):
        return Page.objects.filter(funnel_id=self.id, funnel_type=self.funnel_type())

    def count_pages(self):
        return self.pages().count()


class Funnel(FunnelAbstract):
    class Meta:
        db_table = 'funnels'

    checkout = models.ForeignKey('appauth.Form', null=True, on_delete=models.SET_NULL)

class FunnelTemplate(FunnelAbstract):
    class Meta:
        db_table = 'templates'

    label = 'template'
    category = models.CharField(max_length=50, default='Business')
    publicize_pages = models.BooleanField(default=True)
