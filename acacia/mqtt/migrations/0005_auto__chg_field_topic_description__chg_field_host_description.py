# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Topic.description'
        db.alter_column(u'mqtt_topic', 'description', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Changing field 'Host.description'
        db.alter_column(u'mqtt_host', 'description', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

    def backwards(self, orm):

        # Changing field 'Topic.description'
        db.alter_column(u'mqtt_topic', 'description', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Host.description'
        db.alter_column(u'mqtt_host', 'description', self.gf('django.db.models.fields.TextField')(default=''))

    models = {
        u'mqtt.host': {
            'Meta': {'object_name': 'Host'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
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
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mqtt.Host']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'qos': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'topic': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        }
    }

    complete_apps = ['mqtt']