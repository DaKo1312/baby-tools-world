from django.conf import settings


def author_processor(request):
    return {"author": settings.AUTHOR}
