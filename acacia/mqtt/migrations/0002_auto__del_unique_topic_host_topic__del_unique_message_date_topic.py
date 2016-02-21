# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Message', fields ['date', 'topic']
        db.delete_unique(u'mqtt_message', ['date', 'topic_id'])

        # Removing unique constraint on 'Topic', fields ['host', 'topic']
        db.delete_unique(u'mqtt_topic', ['host_id', 'topic'])


    def backwards(self, orm):
        # Adding unique constraint on 'Topic', fields ['host', 'topic']
        db.create_unique(u'mqtt_topic', ['host_id', 'topic'])

        # Adding unique constraint on 'Message', fields ['date', 'topic']
        db.create_unique(u'mqtt_message', ['date', 'topic_id'])


    models = {
        u'mqtt.host': {
            'Meta': {'object_name': 'Host'},
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
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mqtt.Host']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'topic': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        }
    }

    complete_apps = ['mqtt']