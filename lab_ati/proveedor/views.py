from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .models import Proveedor
from .forms import ProveedorForm
#from ..empresa.models import Empresa, SocialMedia 
from django.template.defaulttags import register
from lab_ati.empresa.models import Empresa, SocialMedia
from lab_ati.empresa.forms import SocialMediaFormset
from lab_ati.utils.social_media import add_social_media
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect, render
from pathlib import Path
import requests



@register.filter
def get_item(objectList, key):
  if objectList == "":
    return ""
  return getattr(objectList,key)

def getCountries():
  countries = requests.get("https://restcountries.com/v3.1/all?fields=name").json()      # Get information about countries via a RESTful API
  names = []
  for i in countries:
      names.append(i["name"]["common"])

  names = sorted(names)
  return names

# Create Supplier 
def createProveedor(request):

  if request.method == 'GET': 
    empresaId = request.GET.get('empresa')                  # get id 

    if(empresaId == None):
      return render(request,'404.html')

    
    try:
      empresa = Empresa.objects.get(id=empresaId)
    except ObjectDoesNotExist:
      return render(request,'404.html')
    
    formularioProveedor = ProveedorForm()
    context = {}
    proveedorSocialMedia = SocialMediaFormset(
        prefix="proveedorSocial",
        queryset=SocialMedia.objects.none()
    )
    socialMediaRepresentanteForm = SocialMediaFormset(
        queryset=SocialMedia.objects.none(),
        prefix="representanteSocial"
    )
    #socialMediaRepresentanteForm = SocialMediaFormset(queryset=SocialMedia.objects.none())
    #print(proveedorSocialMedia)

    context = {
      "data":{
        "empresa":empresa,
        "update":False, 
        "formulario":formularioProveedor,
        "socialMedia" : proveedorSocialMedia,
        "socialMediaRepresentante": socialMediaRepresentanteForm
      },
      "list_link":'/proveedor?empresa='+str(empresaId), 
      "paises": getCountries()
      }
    
    return render(request,'pages/proveedor/create-update.html', context)

  elif request.method == 'POST':
    empresaId = request.GET.get('empresa') 
    if(empresaId == None):
      return render(request,'404.html')  
    empresa = Empresa.objects.get(id=empresaId)
    if(empresa == None):
      return render(request,'404.html')
    formularioProveedor = ProveedorForm(request.POST)
    #print(formularioProveedor)
    social_media_formset = SocialMediaFormset(data=request.POST, prefix="proveedorSocial")
    redes_representante_formset = SocialMediaFormset(data=request.POST, prefix="representanteSocial")
    #print(social_media_formset)
    if formularioProveedor.is_valid() and social_media_formset.is_valid() and redes_representante_formset.is_valid():
      #print('is valid!')
      proveedorSaved = formularioProveedor.save()
      # Añadir las redes sociales del proveedor
      add_social_media(proveedorSaved,social_media_formset, belongs_to="redes_proveedor")
      # Añadir las redes sociales del representante
      add_social_media(proveedorSaved, redes_representante_formset, belongs_to="redes_representante")
      return redirect('/proveedor?empresa='+empresaId)
    return redirect('/proveedor/crear?empresa='+empresaId)

# Update Supplier 
def updateProveedor(request):
  if request.method == 'GET':
    proveedorId = request.GET.get('proveedor')
    
    if(proveedorId == None):
      return render(request,'404.html')
    proveedor = Proveedor.objects.get(id=proveedorId)
    if(proveedor == None):
      return render(request,'404.html') 
    
    formularioProveedor = ProveedorForm(request.POST or request.GET)
    socialMediaForm  = SocialMediaFormset(
        prefix="proveedorSocial",
        queryset=proveedor.redes_proveedor.all()
    )
    socialMediaRepresentanteForm = SocialMediaFormset(
        prefix="representanteSocial",
        queryset=proveedor.redes_representante.all(),
    )

    if formularioProveedor.is_valid():
      messages.success(request, _("Su cambio se ha guardado con éxito"))

    context = {
      "business_id": proveedor.empresa.id,
      "data":{
        "proveedor":proveedor,
        "empresa":{"id":proveedor.empresa.id},
        "update":True,
        "formulario":formularioProveedor,
        "socialMedia":socialMediaForm,
        "socialMediaRepresentante": socialMediaRepresentanteForm
      },
      "editing_social":True,
      "list_link":'/proveedor?empresa='+str(proveedor.empresa.id), 
      "paises": getCountries()
    }
    

    return render(request,'pages/proveedor/create-update.html',context)
  elif request.method == 'POST':
    proveedorId = request.GET.get('proveedor')
    print('proveedor id: ', proveedorId)
    if(proveedorId == None):
      return render(request,'404.html')
    oldProveedor = Proveedor.objects.get(id=proveedorId)
    if(oldProveedor == None):
      return render(request,'404.html')
    print(oldProveedor)
    formularioProveedor = ProveedorForm(request.POST, instance=oldProveedor)
    print(formularioProveedor)
    empresaId = str(oldProveedor.empresa.id)
    if formularioProveedor.is_valid():
      print('is valid!')
      messages.success(request, _("Su cambio se ha guardado con éxito"))
      proveedorSaved = formularioProveedor.save()
      social_media_formset = SocialMediaFormset(
        prefix="proveedorSocial",
        data=request.POST,
        queryset=proveedorSaved.redes_proveedor.all()
      )
      socialMediaRepresentanteForm = SocialMediaFormset(
        queryset=proveedorSaved.redes_representante.all(),
        data=request.POST,
        prefix="representanteSocial"
      )

      if social_media_formset.is_valid():
        add_social_media(proveedorSaved,social_media_formset, belongs_to="redes_proveedor")
      if socialMediaRepresentanteForm.is_valid():
        add_social_media(proveedorSaved,socialMediaRepresentanteForm, belongs_to="redes_representante")
    return redirect('/proveedor?empresa='+empresaId)


#listar proeedores de una emrpresa dada
def listProveedor(request):
  empresaId = request.GET.get('empresa')
  print(empresaId)
  if(empresaId == None):
    return render(request,'404.html')

  empresa = findEmpresa(empresaId)
  print(empresa)
  if(empresa == None): #empresa no existe
    return render(request,'404.html')

  proveedoresList = Proveedor.objects.filter(empresa__id__contains=empresaId)
  print(proveedoresList)
  context = {}

  context["tieneProveedores"] = True
  if(len(proveedoresList)==0):
    context["tieneProveedores"] = False

  context["list"] = proveedoresList
  context["empresa"] = {"empresa":empresa, "id":empresaId}
  context["business_id"] = empresaId
  return render(request,'pages/proveedor/list.html',context)

# Delete Supplier 
def deleteProveedor(request):
  proveedorId = request.GET.get('proveedor')          # get supplier id 

  # Error 
  if(proveedorId == None):
    return render(request,'404.html')

  # get supplier 
  try:
    proveedor = Proveedor.objects.get(id=proveedorId)
  except ObjectDoesNotExist:
    return render(request,'404.html')

  proveedor.delete()                                  # delete 
  empresaId = str(proveedor.empresa.id)
  return redirect('/proveedor?empresa='+empresaId)

def seeProveedor(request):
  proveedorId = request.GET.get('proveedor') 
  if(proveedorId == None):
    return render(request,'404.html')
  proveedor = Proveedor.objects.get(id=proveedorId)
  if(proveedor == None):
    return render(request,'404.html')
  socialMediaForm  = SocialMediaFormset(
    prefix="proveedorSocial",
    queryset=proveedor.redes_proveedor.all()
  )
  socialMediaRepresentanteForm = SocialMediaFormset(
    prefix="representanteSocial",
    queryset=proveedor.redes_representante.all(),
  )
  context = {
    "proveedor" :proveedor,
    "business_id": proveedor.empresa.id,
    "socialMedia":socialMediaForm,
    "socialMediaRepresentante":socialMediaRepresentanteForm,
    "list_link":'/proveedor?empresa='+str(proveedor.empresa.id)
  }
  return render(request,'pages/proveedor/read.html', context)

##otras funciones
def findEmpresa(empresaId):
  empresa = Empresa.objects.get(id=empresaId)
  return empresa

