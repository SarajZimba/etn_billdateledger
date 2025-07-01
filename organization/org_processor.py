from .models import Organization

def org_renderer(request):
    return {
       'org_global': Organization.objects.first() if Organization.objects.all().exists() else None,
    }

