from django.db import models
from django.core.exceptions import ValidationError
import paho.mqtt.client as mqtt
import logging
logger = logging.getLogger(__name__)

def on_connect(client, userdata, flags, rc):
    logger.debug('{client} connected to {host}. Result = {rc}'.format(client=client._client_id,host=client._host, rc=rc))
    
def on_disconnect(client, userdata, rc):
    logger.debug('{client} disconnected from {host}. Result = {rc}'.format(client=client._client_id,host=client._host, rc=rc))
    
def on_subscribe(client, userdata, mid, qos):
    logger.debug('{client} subscribed to #{mid} with QoS={qos}'.format(mid=mid,qos=qos,client=client._client_id))

def on_unsubscribe(client, userdata, mid):
    logger.debug('{client} unsubscribed from #{mid}'.format(mid=mid,client=client._client_id))

def on_message(client, userdata, msg):
    logger.debug('Message received, topic={topic}'.format(topic=msg.topic))
    try:
        host = Host.objects.get(host=client._host)
        topic, created = host.topic_set.get_or_create(topic=msg.topic)
        if created:
            logger.debug('Topic {} created'.format(msg.topic))
        exist = topic.message_set.filter(payload=msg.payload)
        if not exist:
            msg = topic.message_set.create(payload=msg.payload)
            logger.debug('Message saved')
        else:
            logger.debug('Message already exist')
    except Host.DoesNotExist:
        logger.error('Host not registered: %s' % host)

clients = {}

class Host(models.Model):
    host = models.CharField(max_length=256)
    description = models.CharField(max_length=128,null=True,blank=True)
    port = models.IntegerField(default=1883)
    keepalive = models.IntegerField(default = 60)
    _client = None

    def connect(self):
        if not self.host in clients:
            # make a new client
            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_disconnect = on_disconnect
            client.on_message = on_message
            client.on_subscribe = on_subscribe
            client.on_unsubscribe = on_unsubscribe
            client.connect(str(self.host), int(self.port), int(self.keepalive))
            clients[self.host] = client
        self._client = clients[self.host]
    
    def client(self):
        if self._client is None:
            self.connect()
        return self._client

    def topics(self):
        return self.topic_set.count()
        
    def __unicode__(self):
        return self.host    
    
def QoSValidator(value):
    if not value in [0,1,2]:
        raise ValidationError('Quality of Service must be 0, 1 or 2')
    
class Topic(models.Model):
    host = models.ForeignKey(Host)
    topic = models.CharField(max_length=512)
    description = models.CharField(max_length=128,null=True,blank=True)
    qos = models.IntegerField(default=0, validators=[QoSValidator], verbose_name = 'Quality of Service')
    
    def client(self):
        return self.host.client()
    
    def subscribe(self):
        self.client().subscribe(str(self.topic),self.qos)

    def unsubscribe(self):
        self.client().unsubscribe(str(self.topic))
        
    def __unicode__(self):
        return self.topic    

    def messages(self):
        return self.message_set.count()

from django.db.models.signals import pre_delete, pre_save
from django.dispatch.dispatcher import receiver

@receiver(pre_delete, sender=Topic)
def topic_delete(sender, instance, **kwargs):
    instance.unsubscribe()

@receiver(pre_save, sender=Topic)
def topic_save(sender, instance, **kwargs):
    instance.subscribe()

class Message(models.Model):
    date = models.DateTimeField(auto_now_add = True)
    topic = models.ForeignKey(Topic)
    payload = models.CharField(max_length=512)

    def __unicode__(self):
        return '%s %s' % (self.topic, self.date)

def subscribe_all():
    for topic in Topic.objects.all():
        topic.subscribe()

def start():
    subscribe_all()
    for host in Host.objects.all():
        host.client().loop_start()
