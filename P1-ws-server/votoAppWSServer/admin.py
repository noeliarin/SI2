from django.contrib import admin

# Register your models here.
from . models import Censo , Voto

@admin . register ( Censo )
class CensoAdmin ( admin . ModelAdmin ) :
    pass

@admin . register ( Voto )
class VotoAdmin ( admin . ModelAdmin ) :
    pass