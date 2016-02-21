# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Topic.active'
        db.delete_column(u'mqtt_topic', 'active')

        # Adding field 'Topic.qos'
        db.add_column(u'mqtt_topic', 'qos',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Topic.active'
        db.add_column(u'mqtt_topic', 'active',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Deleting field 'Topic.qos'
        db.delete_column(u'mqtt_topic', 'qos')


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
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mqtt.Host']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'qos': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'topic': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        }
    }

    complete_apps = ['mqtt']