# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Series.mlocatie'
        db.add_column(u'data_series', 'mlocatie',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.MeetLocatie'], null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Series.mlocatie'
        db.delete_column(u'data_series', 'mlocatie_id')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'data.chart': {
            'Meta': {'ordering': "['name']", 'object_name': 'Chart'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'percount': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'perunit': ('django.db.models.fields.CharField', [], {'default': "'months'", 'max_length': '10'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_data.chart_set+'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'stop': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': u"orm['auth.User']", 'to': u"orm['auth.User']"})
        },
        u'data.chartseries': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'ChartSeries'},
            'axis': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'axislr': ('django.db.models.fields.CharField', [], {'default': "'l'", 'max_length': '2'}),
            'chart': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'series'", 'to': u"orm['data.Chart']"}),
            'color': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Series']"}),
            'stack': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            't0': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            't1': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'line'", 'max_length': '10'}),
            'y0': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y1': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'data.dashboard': {
            'Meta': {'ordering': "['name']", 'object_name': 'Dashboard'},
            'charts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['data.Chart']", 'through': u"orm['data.DashboardChart']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': u"orm['auth.User']", 'to': u"orm['auth.User']"})
        },
        u'data.dashboardchart': {
            'Meta': {'ordering': "['order']", 'object_name': 'DashboardChart'},
            'chart': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Chart']"}),
            'dashboard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Dashboard']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'data.datapoint': {
            'Meta': {'unique_together': "(('series', 'date'),)", 'object_name': 'DataPoint'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'datapoints'", 'to': u"orm['data.Series']"}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'data.datasource': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('name', 'meetlocatie'),)", 'object_name': 'Datasource'},
            'autoupdate': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'config': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'generator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Generator']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_download': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'meetlocatie': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'datasources'", 'to': u"orm['data.MeetLocatie']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'Europe/Amsterdam'", 'max_length': '50', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': u"orm['auth.User']", 'to': u"orm['auth.User']"}),
            'username': ('django.db.models.fields.CharField', [], {'default': "'anonymous'", 'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        u'data.formula': {
            'Meta': {'ordering': "['name']", 'object_name': 'Formula', '_ormbases': [u'data.Series']},
            'formula_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'formula_variables': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['data.Variable']", 'symmetrical': 'False'}),
            'intersect': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'locatie': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.MeetLocatie']"}),
            u'series_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data.Series']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'data.generator': {
            'Meta': {'ordering': "['name']", 'object_name': 'Generator'},
            'classname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'data.grid': {
            'Meta': {'ordering': "['name']", 'object_name': 'Grid', '_ormbases': [u'data.Chart']},
            u'chart_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data.Chart']", 'unique': 'True', 'primary_key': 'True'}),
            'colwidth': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'entity': ('django.db.models.fields.CharField', [], {'default': "'Weerstand'", 'max_length': '50'}),
            'rowheight': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'scale': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'unit': ('django.db.models.fields.CharField', [], {'default': "'\\xce\\xa9m'", 'max_length': '20', 'blank': 'True'}),
            'ymin': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'zmax': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'zmin': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'data.manualseries': {
            'Meta': {'ordering': "['name']", 'object_name': 'ManualSeries', '_ormbases': [u'data.Series']},
            'locatie': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.MeetLocatie']"}),
            u'series_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data.Series']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'data.meetlocatie': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('projectlocatie', 'name'),)", 'object_name': 'MeetLocatie'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '28992'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'projectlocatie': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.ProjectLocatie']"}),
            'webcam': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Webcam']", 'null': 'True', 'blank': 'True'})
        },
        u'data.notification': {
            'Meta': {'object_name': 'Notification'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'datasource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Datasource']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'default': "'ERROR'", 'max_length': '10'}),
            'subject': ('django.db.models.fields.TextField', [], {'default': "'acaciadata.com update rapport'", 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'data.parameter': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('name', 'datasource'),)", 'object_name': 'Parameter'},
            'datasource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Datasource']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'line'", 'max_length': '20'}),
            'unit': ('django.db.models.fields.CharField', [], {'default': "'m'", 'max_length': '10'})
        },
        u'data.project': {
            'Meta': {'object_name': 'Project'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'theme': ('django.db.models.fields.CharField', [], {'default': "'dark-blue'", 'max_length': '50'})
        },
        u'data.projectlocatie': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('project', 'name'),)", 'object_name': 'ProjectLocatie'},
            'dashboard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.TabGroup']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '28992'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Project']"}),
            'webcam': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Webcam']", 'null': 'True', 'blank': 'True'})
        },
        u'data.series': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('parameter', 'name'),)", 'object_name': 'Series'},
            'aggregate': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'cumstart': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'cumsum': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'from_limit': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit_time': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mlocatie': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.MeetLocatie']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'offset': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'offset_series': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'offset_set'", 'null': 'True', 'to': u"orm['data.Series']"}),
            'parameter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Parameter']", 'null': 'True', 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_data.series_set+'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'resample': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'scale': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'scale_series': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'scaling_set'", 'null': 'True', 'to': u"orm['data.Series']"}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'to_limit': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'line'", 'max_length': '20', 'blank': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': u"orm['auth.User']", 'to': u"orm['auth.User']"})
        },
        u'data.seriesproperties': {
            'Meta': {'object_name': 'SeriesProperties'},
            'aantal': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'beforelast': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'beforelast'", 'null': 'True', 'to': u"orm['data.DataPoint']"}),
            'eerste': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'first'", 'null': 'True', 'to': u"orm['data.DataPoint']"}),
            'gemiddelde': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'laatste': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'last'", 'null': 'True', 'to': u"orm['data.DataPoint']"}),
            'max': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True'}),
            'min': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True'}),
            'series': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'properties'", 'unique': 'True', 'to': u"orm['data.Series']"}),
            'tot': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'van': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        u'data.sourcefile': {
            'Meta': {'object_name': 'SourceFile'},
            'cols': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'crc': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'datasource': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sourcefiles'", 'to': u"orm['data.Datasource']"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'rows': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'stop': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'uploaded': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': u"orm['auth.User']", 'to': u"orm['auth.User']"})
        },
        u'data.tabgroup': {
            'Meta': {'object_name': 'TabGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.ProjectLocatie']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'data.tabpage': {
            'Meta': {'object_name': 'TabPage'},
            'dashboard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Dashboard']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'basis'", 'max_length': '40'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'tabgroup': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.TabGroup']"})
        },
        u'data.variable': {
            'Meta': {'unique_together': "(('locatie', 'name'),)", 'object_name': 'Variable'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locatie': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.MeetLocatie']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Series']"})
        },
        u'data.webcam': {
            'Meta': {'object_name': 'Webcam'},
            'admin': ('django.db.models.fields.TextField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'video': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['data']