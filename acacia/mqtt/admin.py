from django.contrib import admin
from .models import Host, Topic, Message

class TopicInline(admin.TabularInline):
    model = Topic

class MessageInline(admin.TabularInline):
    model = Message
    fields = ('payload',)
    
class HostAdmin(admin.ModelAdmin):
    model = Host
    inlines = [TopicInline]
    list_display = ('host', 'port', 'topics')
    
class TopicAdmin(admin.ModelAdmin):
    model = Topic
    #inlines = [MessageInline]
    list_display = ('topic', 'host', 'messages')
    list_filter = ('host',)

class MessageAdmin(admin.ModelAdmin):
    model = Message
    list_display = ('topic', 'date', 'payload')
    list_filter = ('topic', 'date')
        
admin.site.register(Host, HostAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Message, MessageAdmin)
