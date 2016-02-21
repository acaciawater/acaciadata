# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Host'
        db.create_table(u'mqtt_host', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('host', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('port', self.gf('django.db.models.fields.IntegerField')(default=1833)),
            ('keepalive', self.gf('django.db.models.fields.IntegerField')(default=60)),
        ))
        db.send_create_signal(u'mqtt', ['Host'])

        # Adding model 'Topic'
        db.create_table(u'mqtt_topic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mqtt.Host'])),
            ('topic', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'mqtt', ['Topic'])

        # Adding unique constraint on 'Topic', fields ['host', 'topic']
        db.create_unique(u'mqtt_topic', ['host_id', 'topic'])

        # Adding model 'Message'
        db.create_table(u'mqtt_message', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mqtt.Topic'])),
            ('payload', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal(u'mqtt', ['Message'])

        # Adding unique constraint on 'Message', fields ['date', 'topic']
        db.create_unique(u'mqtt_message', ['date', 'topic_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Message', fields ['date', 'topic']
        db.delete_unique(u'mqtt_message', ['date', 'topic_id'])

        # Removing unique constraint on 'Topic', fields ['host', 'topic']
        db.delete_unique(u'mqtt_topic', ['host_id', 'topic'])

        # Deleting model 'Host'
        db.delete_table(u'mqtt_host')

        # Deleting model 'Topic'
        db.delete_table(u'mqtt_topic')

        # Deleting model 'Message'
        db.delete_table(u'mqtt_message')


    models = {
        u'mqtt.host': {
            'Meta': {'object_name': 'Host'},
            'host': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keepalive': ('django.db.models.fields.IntegerField', [], {'default': '60'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '1833'})
        },
        u'mqtt.message': {
            'Meta': {'unique_together': "(('date', 'topic'),)", 'object_name': 'Message'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payload': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mqtt.Topic']"})
        },
        u'mqtt.topic': {
            'Meta': {'unique_together': "(('host', 'topic'),)", 'object_name': 'Topic'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mqtt.Host']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'topic': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        }
    }

    complete_apps = ['mqtt']