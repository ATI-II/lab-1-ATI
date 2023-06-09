from attr import attr
from django import forms

from lab_ati.empresa.models import Empleado, Empresa, SocialMedia

COUNTRY_CHOICES = (
    ("", "Selecciona..."),
    ("ve", "Venezuela"),
    ("ec", "Ecuador"),
    ("es", "España"),
)

# creating a form
class CreateBusinessForm(forms.ModelForm):
    """
    Formulario del modelo empresa
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        # Set custom widget attr
        if(self.instance):
            self.fields['cliente_empresa'].queryset = Empresa.objects.exclude(id = self.instance.id)
        
        for field in self.fields.values():
            if isinstance(field, forms.fields.CharField):
                if isinstance(field.widget, forms.widgets.Textarea):
                    if(not field.label in ["Dirección", "Servicio que le ofrecimos", "Servicio que proporciona"]):    
                        field.widget = forms.TextInput(attrs={
                            "required": True,
                        })
                    
                field.widget.attrs.update({
                    "class": "form-control",
                })

            if isinstance(field.widget, forms.widgets.Select):
                field.widget.attrs.update({
                    "class": "form-select",
                })   
        
        self.fields['telefono'].widget.attrs.update({
            "pattern" : "\+?\d{1,3}(-\d{2,4}){2,4}|\+?\d{7,15}",
        }) 
        
        self.fields['whatsapp'].widget.attrs.update({
            "pattern" : "\+?\d{1,3}(-\d{2,4}){2,4}|\+?\d{7,15}",
        }) 
        
        self.fields['email'].widget.attrs.update({
            "pattern" : "[^\s@]+@[^\s@\.]+\.{1}[^\s@\.]+",
        })  

    
    class Meta:
        model = Empresa
        fields = "__all__"
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 2}),
            'servicio_ofrecido': forms.Textarea(attrs={'rows': 2}),
            'servicio_proporciona': forms.Textarea(attrs={'rows': 2}),
            'curso_interes': forms.Textarea(attrs={'rows': 2}),
        }

class CreateEmployeeForm(forms.ModelForm):
    """
    Formulario del modelo empleado
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        # Set custom widget attr
        for field in  self.fields.values():
            if isinstance(field, forms.fields.CharField):
                if isinstance(field.widget, forms.widgets.Textarea):
                    field.widget = forms.TextInput(attrs={
                        "required": True,
                    })

                field.widget.attrs.update({
                    "class": "form-control",
                })

            if isinstance(field.widget, forms.widgets.Select):
                field.widget.attrs.update({
                    "class": "form-select",
                    "id":"modalidad",
                })   

        self.fields['tlf_celular'].widget.attrs.update({
            "pattern" : "\+?\d{1,3}(-\d{2,4}){3,4}|\+?\d{7,15}",
        }) 
            
        self.fields['tlf_local'].widget.attrs.update({
            "pattern" : "\+?\d{1,3}(-\d{2,4}){3,4}|\+?\d{7,15}",
        }) 

        self.fields['email_emp'].widget.attrs.update({
            "pattern" : "[^\s@]+@[^\s@\.]+\.{1}[^\s@\.]+",
        })  
        
        self.fields['email_p'].widget.attrs.update({
            "pattern" : "[^\s@]+@[^\s@\.]+\.{1}[^\s@\.]+",
        })  
        
    class Meta:
        model = Empleado
        fields = "__all__"

custom_text_input = forms.TextInput(attrs={
    "class": "form-control",
})

SocialMediaFormset = forms.modelformset_factory(
    SocialMedia,
    fields=("nombre","valor"),
    extra=1,
    widgets={
        "nombre": custom_text_input,
        "valor": custom_text_input
    },
    can_delete=True,
)