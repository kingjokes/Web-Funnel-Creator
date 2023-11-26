from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound, APIException

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

import json, os, shutil
from typing import Union, Type

from appauth.utils import get_category, get_funnel_manager, get_index_page, funnel_label
from misc.utils import default_palette, SycartResponse

from .serializers import UserSerializer, FunnelSerializer, TemplateSerializer, FormSerializer, PageSerializer

from .models import Funnel, FunnelTemplate, Page, Form
from ecommerce.models import Product
from back import settings


# Create your views here.
class UserView(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def auth_user(self, request):
        ser = UserSerializer(request.user)
        return Response(ser.data)

    def delete_item(self, request):
        data = request.data
        item_id = data.get('id')
        item_type = data.get('item_type')
        funnel_type = data.get('funnel_type')

        item = None

        if item_type == 'forms':
            item = Form.objects.get(uid=item_id)

        elif item_type == 'funnels':
            manager = get_funnel_manager(funnel_type)
            item = manager.get(uid=item_id)

        elif item_type == 'pages':
            try:
                funnel_id = data.get('funnel_id')
                fun_manager = get_funnel_manager(funnel_type)
                funnel = fun_manager.get(uid=funnel_id)
                item = Page.objects.filter(funnel_id=funnel.id, funnel_type=funnel_type, slug=item_id)

                if item.exists():
                    item = item.first()

            except (Funnel.DoesNotExist, FunnelTemplate.DoesNotExist):
                raise NotFound('Funnel or template does not exist.')

        if item:
            item.delete()

            return Response(True)
        
        else:
            raise APIException('Invalid model type. This is usually caused by invalid item type.')

    def dashboard(self, request):
        user = request.user
        def user_items(model: Union[Type[Funnel], Type[Page], Type[Product]]):
            return model.objects.filter(owner=user)

        funnels = user_items(Funnel)
        funnel_list = FunnelSerializer(funnels, many=True).data
        data = {
            "funnels": funnels.count(),
            "pages": user_items(Page).count(),
            "products": user_items(Product).count(),
            "orders": 0,
            "funnel_list": funnel_list
        }

        resp = SycartResponse()
        
        resp.set_error(False)
        resp.set_data(data)

        return Response(resp.data)

class FunnelView(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FunnelSerializer

    def create(self, request):
        data = request.data
        name = data.get('name')
        base = data.get('base')
        is_template = data.get('is_template')
        template = data.get('template')
        funnel: Funnel | FunnelTemplate | None = None

        # create funnel/template
        if is_template:
            cat = get_category(data.get('category'))
            pub_pages = data.get('publicize_pages', True)
            funnel = FunnelTemplate.objects.create(
                name=name, 
                base=base, 
                owner=request.user, 
                category=cat,
                publicize_pages=pub_pages
            )

            data = TemplateSerializer(funnel)

        else:
            funnel = Funnel.objects.create(name=name, base=base, owner=request.user)
            data = FunnelSerializer(funnel)

        # save funnel data to file
        if funnel:
            storage = settings.STORAGE_FOLDER
            fpath = funnel.base_folder() # funnel folder
            ppath = funnel.pages_folder() # pages folder

            main_file = fpath / "main.json"
            os.makedirs(fpath, exist_ok=True)
            os.mkdir(ppath)
            
            # default funnel data
            default_header = "Double Deck"
            header_file = open(storage/"defaults/headers.json", "r")
            headers = json.load(header_file)
            header_file.close()
            fdata = {
                "header": {
                    "template": default_header,
                    "data": headers.get(default_header)
                },
                "palette": default_palette()
            }

            # save default funnel data
            funnel_type = "template" if is_template else "public"
            if is_template or template == "from-scratch":
                with open(main_file, "w") as file:
                    json.dump(fdata, file)

                new_page = Page.objects.create(
                    name="Home", 
                    slug="home", 
                    funnel_id=funnel.id,
                    funnel_type=funnel_type, 
                    published=True,
                    owner=request.user,
                    is_index=True
                )

                # create default home
                home_file = storage / "defaults/page.json"
                page_file = new_page.uid.hex+".json"
                shutil.copy(home_file, ppath/page_file)

            else:
                template = FunnelTemplate.objects.get(uid=template.get("id"))
                tpath = template.base_folder()
                shutil.copytree(tpath, fpath, dirs_exist_ok=True)

                # copy page data
                tpages = Page.objects.filter(funnel_id=template.id, funnel_type="template")
                if tpages.exists():
                    for page in tpages:
                        new_page = Page.objects.create(
                            name=page.name, 
                            slug=page.slug, 
                            funnel_id=funnel.id,
                            funnel_type=funnel_type, 
                            published=True,
                            owner=request.user,
                            is_index=page.is_index
                        )

                        # rename template's pages to funnel's pages
                        pp_file = page.uid.hex+".json"
                        np_file = new_page.uid.hex+".json"
                        shutil.move(ppath/pp_file, ppath/np_file)
                        
        return Response(data.data)

    # Gets pages associated to a funnel
    def get_pages(self, request, funnel_type, funnel_id):
        manager = get_funnel_manager(funnel_type)

        try:
            funnel = manager.get(uid=funnel_id)
            funnel_id = funnel.id
            owner = request.user
            pages = Page.objects.filter(funnel_id=funnel_id, funnel_type=funnel_type, owner=owner)

            data = []

            if pages.exists():
                data = PageSerializer(pages, many=True).data

            return Response(data)
            
        except Funnel.DoesNotExist:
            raise NotFound('Funnel does not exist')

    def get_funnel(self, request, funnel_type, funnel_id):
        resp = SycartResponse()
        manager = get_funnel_manager(funnel_type)
        funnel = manager.filter(uid=funnel_id, owner=request.user).first()

        if funnel:
            serializer = FunnelSerializer if funnel_type == "public" else TemplateSerializer
            data = serializer(funnel).data
            resp.set_error(False)
            resp.set_data(data)

        else:
            resp.set_error(True)
            resp.set_data("Item could not be found!")

        return Response(resp.data)

    # get funnels created by a user
    def get_user_funnels(self, request, funnel_type):
        owner = request.user
        manager = get_funnel_manager(funnel_type)
        funnels = manager.filter(owner=owner)

        data = FunnelSerializer(funnels, many=True).data
        return Response(data)

    # publish a funnel/template
    def publish(self, request):
        data = request.data
        uid = data.get('id')
        state = data.get('state')
        item_type = data.get('item_type')
        funnel_type = data.get('funnel_type')

        item = None
        resp = SycartResponse()
        resp.set_data("Item not found")
        label = item_type

        if item_type == "page":
            funnel_id = data.get("funnel_id")
            page = Page.objects.filter(funnel_id=funnel_id, funnel_type=funnel_type, owner=request.user)
            
            if page.exists():
                item = page.first()

        elif item_type == "funnel":
            manager = get_funnel_manager(funnel_type)
            funs = manager.filter(uid=uid, owner=request.user)
            label = funnel_type

            if funs.first():
                item = funs.first()

        if item:
            item.published = state
            item.save()

            resp.set_error(False)
            resp.set_data("Your " +label+ " is successfully updated!")

        return Response(resp.data)

    # gets index page of a funnel/template
    def get_index_page(self, request, funnel_type, funnel_id):
        manager = get_funnel_manager(funnel_type)
        try:
            funnel = manager.filter(uid=funnel_id, owner = request.user)
            if not funnel.exists():
                raise Funnel.DoesNotExist

            else:
                funnel = funnel.first()
                
            funnel_id = funnel.id
            index = get_index_page(funnel_id, funnel_type)

            slug = index.slug if index else None
            return Response(slug)
        
        except Funnel.DoesNotExist:
            raise NotFound('Funnel does not exist')

    def set_index_page(self, request):
        data = request.data
        funnel_id = data.get('funnel_id')
        funnel_type = data.get('funnel_type')
        page_id = data.get('page_slug')
        state = data.get('state')

        resp = SycartResponse()
        # print(data, request.user.email)

        manager = get_funnel_manager(funnel_type)
        funnel = manager.filter(uid=funnel_id, owner=request.user)
        funnel = funnel.first()
        
        if funnel:
            funnel.set_index_page(page_id, state)

            resp.set_error(False)
            resp.set_data("Your "+funnel_type+" is updated successfully!")

        else:
            resp.set_error(True)
            resp.set_data("Cannot find this "+funnel_type+" in your account.")

        return Response(resp.data)

    # loads editor data from file
    def load_editor_data(self, request, funnel_id, funnel_type):
      funnel_manager = get_funnel_manager(funnel_type)
      funnel = funnel_manager.filter(uid=funnel_id, owner=request.user)
      
      resp = SycartResponse()
      if funnel.exists():
        funnel = funnel.first()
        if funnel:
          funnel_data = funnel.load_data()
          index_page = funnel.get_index_page()
          page_data = None

          if index_page:
            page_data = index_page.load_data()
            # page_data["title"] = index_page.name
            # page_data["slug"] = index_page.slug

            resp_data = {
                "funnel": funnel_data,
                "page": page_data
            }

            resp.set_error(False)
            resp.set_data(resp_data)
        else:
            label = funnel_label(funnel_type).capitalize()
            resp.set_data(label+" is not found or is not created by user.")


      return Response(resp.data)

    # save editor data to file
    def save_editor_data(self, request):
        data = request.data

        funnel_id = data.get("id")
        funnel_type = data.get("type")

        resp = SycartResponse()
        
        funnel = get_funnel_manager(funnel_type).filter(uid=funnel_id, owner=request.user)
        label = funnel_label(funnel_type).capitalize()

        if funnel.exists():
            payload = data.get("payload")
            funnel = funnel.first()

            if funnel:
                funnel.save_data(payload.get("funnel"))

                page_id = data.get("page")
                page = funnel.has_page(page_id)

                if page:
                    page_data = payload.get("page")
                    del page_data["title"]
                    del page_data["slug"]
                    page.save_data(page_data)

                else:
                    resp.set_error(True)
                    resp.set_data("Current page's id is not associated with this "+label+".")
                    return Response(resp.data)
                
            resp.set_error(False)
            resp.set_data(label+" saved successfully!")

        else:
            resp.set_data(label+" does not exist!")

        return Response(resp.data)

    def load_page_data(self, request, funnel_id, funnel_type, page_slug):
        manager = get_funnel_manager(funnel_type)
        funnel = manager.filter(uid=funnel_id, owner=request.user).first()
        label = funnel_label(funnel_type)

        resp = SycartResponse()

        if funnel:
            page = funnel.has_page(page_slug)
            if page:
                page_data = page.load_data()
                resp.set_error(False)
                resp.set_data(page_data)

        else:
            resp.set_error(True)
            resp.set_data("Cannot find "+label+" in your account")

        return Response(resp.data)


    def create_page(self, request):
        data = request.data
        funnel_id = data.get('funnel')
        funnel_type = data.get('funnel_type')
        is_index = data.get('is_index')

        manager = get_funnel_manager(funnel_type)
        funnel = manager.filter(uid=funnel_id, owner=request.user).first()
        resp = SycartResponse()
        label = funnel_label(funnel_type).capitalize()

        if funnel:
            page_data = data.get('page')
            title = page_data.get('title')
            slug = page_data.get('slug')

            page = Page.objects.create(
                funnel_id=funnel.id,
                funnel_type=funnel_type,
                is_index=is_index,
                name=title,
                slug=slug,
                owner=request.user,
            )

            del page_data["title"]
            del page_data["slug"]

            base_file = page.base_file()
            with open(base_file, "w") as file:
                json.dump(page_data, file)

            resp.set_error(False)
            resp.set_data("Page created successfully")

        else:
            resp.set_error(True)
            resp.set_data(label+" does not exist in your account!")

        return Response(resp.data)

class FormView(ModelViewSet):
    permission_classes=(IsAuthenticated,)
    serializer_class=Form

    def create(self, request):
        data = request.data
        name = data.get('name')
        ftype = data.get('type')

        form = Form.objects.create(name=name, ftype=ftype, owner=request.user)

        return Response(form.uid)

    def get_user_forms(self, request):
        owner = request.user
        forms = Form.objects.filter(owner=owner)

        data = FormSerializer(forms, many=True).data
        return Response(data)


class PublicView(ModelViewSet):
    permission_classes = (AllowAny,)

    def get_templates(self, request, cat='All'):
        template_data = []
        templates = FunnelTemplate.objects.filter(published=True)

        if cat and cat != 'All':
            templates = templates.filter(category=cat)
        
        if templates.exists():
            template_data = TemplateSerializer(templates, many=True).data

        return Response(template_data)        

    def get_public_item(self, request,):
        status = True
        query = request.query_params
        item_id = query.get("id")
        item_type = query.get("item_type")

        items = Funnel.objects.filter(base=item_id, published=status)
        serializer = FunnelSerializer

        if item_type in ['page', 'index']:
            funnel_id = query.get("funnel")

            if item_type == 'index':
                funnel = Funnel.objects.get(uid=funnel_id)
                items = funnel.get_index_page()

            else:
                items = Page.objects.filter(slug=item_id, published=status)
                
            serializer = PageSerializer

        resp = SycartResponse()
        item = items if item_type == 'index' else items.first()

        if item:
            data = {
                "meta": serializer(item).data,
                "template": item.load_data()
            }

            resp.set_error(False)
            resp.set_data(data)

        else:
            resp.set_error(True)
            resp.set_data("DOES_NOT_EXIST")

        return Response(resp.data)

    def get_index(self, request, funnel_type, funnel_id):
        manager = get_funnel_manager(funnel_type)
        funnel = manager.filter(published=True, uid=funnel_id)

        if funnel.exists():
            funnel = funnel.first()
            index = get_index_page(funnel_id=funnel.id, funnel_type=funnel_type)

            index = index.slug if index else None

            return Response(index)

        else:
            raise NotFound("Funnel does not exist")