from django import template
from my_messages.models import Message
from profile_mangement.models import ProfileInfo

register = template.Library()


@register.simple_tag
def message_alert(request):
    messages_count = Message.objects.filter(new=True,receiver=request.user).count()
    return messages_count


@register.simple_tag
def profile_picture(request):
    try:
        picture = ProfileInfo.objects.get(user=request.user)
        return picture.profile_image.icon_code[:47] + '64" ' + picture.profile_image.icon_code[51:59] + '64" color="black" ' + picture.profile_image.icon_code[62:]
    except:
        picture = """<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="currentColor" class="bi bi-person-circle" viewBox="0 0 16 16"><path d="M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0z"/><path fill-rule="evenodd" d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm8-7a7 7 0 0 0-5.468 11.37C3.242 11.226 4.805 10 8 10s4.757 1.225 5.468 2.37A7 7 0 0 0 8 1z"/></svg>"""
        return picture

