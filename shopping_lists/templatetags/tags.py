from django import template
from my_messages.models import Message

register = template.Library()

@register.simple_tag
def message_alert(request):
    messages_count = Message.objects.filter(new=True,receiver=request.user).count()
    return messages_count