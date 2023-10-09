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
    picture = ProfileInfo.objects.get(user=request.user)
    return picture.profile_image