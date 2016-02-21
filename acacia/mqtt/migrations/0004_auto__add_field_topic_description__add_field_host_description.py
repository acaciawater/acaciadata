# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Topic.description'
        db.add_column(u'mqtt_topic', 'description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Host.description'
        db.add_column(u'mqtt_host', 'description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Topic.description'
        db.delete_column(u'mqtt_topic', 'description')

        # Deleting field 'Host.description'
        db.delete_column(u'mqtt_host', 'description')


    models = {
        u'mqtt.host': {
            'Meta': {'object_name': 'Host'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keepalive': ('django.db.models.fields.IntegerField', [], {'default': '60'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '1883'})
        },
        u'mqtt.message': {
            'Meta': {'object_name': 'Message'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payload': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mqtt.Topic']"})
        },
        u'mqtt.topic': {
            'Meta': {'object_name': 'Topic'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mqtt.Host']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'qos': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'topic': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        }
    }

    complete_apps = ['mqtt']