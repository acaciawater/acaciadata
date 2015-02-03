# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table(u'data_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('theme', self.gf('django.db.models.fields.CharField')(default='dark-blue', max_length=50)),
        ))
        db.send_create_signal(u'data', ['Project'])

        # Adding model 'Webcam'
        db.create_table(u'data_webcam', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.TextField')()),
            ('video', self.gf('django.db.models.fields.TextField')()),
            ('admin', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'data', ['Webcam'])

        # Adding model 'ProjectLocatie'
        db.create_table(u'data_projectlocatie', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Project'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=28992)),
            ('webcam', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Webcam'], null=True, blank=True)),
        ))
        db.send_create_signal(u'data', ['ProjectLocatie'])

        # Adding unique constraint on 'ProjectLocatie', fields ['project', 'name']
        db.create_unique(u'data_projectlocatie', ['project_id', 'name'])

        # Adding model 'MeetLocatie'
        db.create_table(u'data_meetlocatie', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('projectlocatie', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.ProjectLocatie'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=28992)),
            ('webcam', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Webcam'], null=True, blank=True)),
        ))
        db.send_create_signal(u'data', ['MeetLocatie'])

        # Adding unique constraint on 'MeetLocatie', fields ['projectlocatie', 'name']
        db.create_unique(u'data_meetlocatie', ['projectlocatie_id', 'name'])

        # Adding model 'Generator'
        db.create_table(u'data_generator', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('classname', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'data', ['Generator'])

        # Adding model 'Datasource'
        db.create_table(u'data_datasource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('meetlocatie', self.gf('django.db.models.fields.related.ForeignKey')(related_name='datasources', to=orm['data.MeetLocatie'])),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('generator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Generator'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_download', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('autoupdate', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(default=orm['auth.User'], to=orm['auth.User'])),
            ('config', self.gf('django.db.models.fields.TextField')(default='{}', null=True, blank=True)),
            ('username', self.gf('django.db.models.fields.CharField')(default='anonymous', max_length=50, null=True, blank=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('timezone', self.gf('django.db.models.fields.CharField')(default='Europe/Amsterdam', max_length=50, blank=True)),
        ))
        db.send_create_signal(u'data', ['Datasource'])

        # Adding unique constraint on 'Datasource', fields ['name', 'meetlocatie']
        db.create_unique(u'data_datasource', ['name', 'meetlocatie_id'])

        # Adding model 'SourceFile'
        db.create_table(u'data_sourcefile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('datasource', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sourcefiles', to=orm['data.Datasource'])),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=200, null=True, blank=True)),
            ('rows', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('cols', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('stop', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('crc', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(default=orm['auth.User'], to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('uploaded', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'data', ['SourceFile'])

        # Adding unique constraint on 'SourceFile', fields ['name', 'datasource']
        db.create_unique(u'data_sourcefile', ['name', 'datasource_id'])

        # Adding model 'Parameter'
        db.create_table(u'data_parameter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datasource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Datasource'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('unit', self.gf('django.db.models.fields.CharField')(default='m', max_length=10)),
            ('type', self.gf('django.db.models.fields.CharField')(default='line', max_length=20)),
            ('thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'data', ['Parameter'])

        # Adding unique constraint on 'Parameter', fields ['name', 'datasource']
        db.create_unique(u'data_parameter', ['name', 'datasource_id'])

        # Adding model 'Series'
        db.create_table(u'data_series', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='line', max_length=20, blank=True)),
            ('parameter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Parameter'], null=True, blank=True)),
            ('thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=200, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(default=orm['auth.User'], to=orm['auth.User'])),
            ('resample', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('aggregate', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('scale', self.gf('django.db.models.fields.FloatField')(default=1.0)),
            ('offset', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('cumsum', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cumstart', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'data', ['Series'])

        # Adding unique constraint on 'Series', fields ['parameter', 'name']
        db.create_unique(u'data_series', ['parameter_id', 'name'])

        # Adding model 'Variable'
        db.create_table(u'data_variable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('locatie', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.MeetLocatie'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('series', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Series'])),
        ))
        db.send_create_signal(u'data', ['Variable'])

        # Adding unique constraint on 'Variable', fields ['locatie', 'name']
        db.create_unique(u'data_variable', ['locatie_id', 'name'])

        # Adding model 'Formula'
        db.create_table(u'data_formula', (
            (u'series_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['data.Series'], unique=True, primary_key=True)),
            ('locatie', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.MeetLocatie'])),
            ('formula_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('intersect', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'data', ['Formula'])

        # Adding M2M table for field formula_variables on 'Formula'
        m2m_table_name = db.shorten_name(u'data_formula_formula_variables')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('formula', models.ForeignKey(orm[u'data.formula'], null=False)),
            ('variable', models.ForeignKey(orm[u'data.variable'], null=False))
        ))
        db.create_unique(m2m_table_name, ['formula_id', 'variable_id'])

        # Adding model 'DataPoint'
        db.create_table(u'data_datapoint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('series', self.gf('django.db.models.fields.related.ForeignKey')(related_name='datapoints', to=orm['data.Series'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('value', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'data', ['DataPoint'])

        # Adding unique constraint on 'DataPoint', fields ['series', 'date']
        db.create_unique(u'data_datapoint', ['series_id', 'date'])

        # Adding model 'Chart'
        db.create_table(u'data_chart', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(default=orm['auth.User'], to=orm['auth.User'])),
            ('start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('stop', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('percount', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('perunit', self.gf('django.db.models.fields.CharField')(default='months', max_length=10)),
        ))
        db.send_create_signal(u'data', ['Chart'])

        # Adding model 'ChartSeries'
        db.create_table(u'data_chartseries', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('chart', self.gf('django.db.models.fields.related.ForeignKey')(related_name='series', to=orm['data.Chart'])),
            ('series', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Series'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('axis', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('axislr', self.gf('django.db.models.fields.CharField')(default='l', max_length=2)),
            ('color', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='line', max_length=10)),
            ('stack', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('label', self.gf('django.db.models.fields.CharField')(default='', max_length=20, null=True, blank=True)),
            ('y0', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('y1', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('t0', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('t1', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'data', ['ChartSeries'])

        # Adding model 'Dashboard'
        db.create_table(u'data_dashboard', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(default=orm['auth.User'], to=orm['auth.User'])),
        ))
        db.send_create_signal(u'data', ['Dashboard'])

        # Adding M2M table for field charts on 'Dashboard'
        m2m_table_name = db.shorten_name(u'data_dashboard_charts')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dashboard', models.ForeignKey(orm[u'data.dashboard'], null=False)),
            ('chart', models.ForeignKey(orm[u'data.chart'], null=False))
        ))
        db.create_unique(m2m_table_name, ['dashboard_id', 'chart_id'])

        # Adding model 'TabGroup'
        db.create_table(u'data_tabgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.ProjectLocatie'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal(u'data', ['TabGroup'])

        # Adding model 'TabPage'
        db.create_table(u'data_tabpage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tabgroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.TabGroup'])),
            ('name', self.gf('django.db.models.fields.CharField')(default='basis', max_length=40)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('dashboard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data.Dashboard'])),
        ))
        db.send_create_signal(u'data', ['TabPage'])


    def backwards(self, orm):
        # Removing unique constraint on 'DataPoint', fields ['series', 'date']
        db.delete_unique(u'data_datapoint', ['series_id', 'date'])

        # Removing unique constraint on 'Variable', fields ['locatie', 'name']
        db.delete_unique(u'data_variable', ['locatie_id', 'name'])

        # Removing unique constraint on 'Series', fields ['parameter', 'name']
        db.delete_unique(u'data_series', ['parameter_id', 'name'])

        # Removing unique constraint on 'Parameter', fields ['name', 'datasource']
        db.delete_unique(u'data_parameter', ['name', 'datasource_id'])

        # Removing unique constraint on 'SourceFile', fields ['name', 'datasource']
        db.delete_unique(u'data_sourcefile', ['name', 'datasource_id'])

        # Removing unique constraint on 'Datasource', fields ['name', 'meetlocatie']
        db.delete_unique(u'data_datasource', ['name', 'meetlocatie_id'])

        # Removing unique constraint on 'MeetLocatie', fields ['projectlocatie', 'name']
        db.delete_unique(u'data_meetlocatie', ['projectlocatie_id', 'name'])

        # Removing unique constraint on 'ProjectLocatie', fields ['project', 'name']
        db.delete_unique(u'data_projectlocatie', ['project_id', 'name'])

        # Deleting model 'Project'
        db.delete_table(u'data_project')

        # Deleting model 'Webcam'
        db.delete_table(u'data_webcam')

        # Deleting model 'ProjectLocatie'
        db.delete_table(u'data_projectlocatie')

        # Deleting model 'MeetLocatie'
        db.delete_table(u'data_meetlocatie')

        # Deleting model 'Generator'
        db.delete_table(u'data_generator')

        # Deleting model 'Datasource'
        db.delete_table(u'data_datasource')

        # Deleting model 'SourceFile'
        db.delete_table(u'data_sourcefile')

        # Deleting model 'Parameter'
        db.delete_table(u'data_parameter')

        # Deleting model 'Series'
        db.delete_table(u'data_series')

        # Deleting model 'Variable'
        db.delete_table(u'data_variable')

        # Deleting model 'Formula'
        db.delete_table(u'data_formula')

        # Removing M2M table for field formula_variables on 'Formula'
        db.delete_table(db.shorten_name(u'data_formula_formula_variables'))

        # Deleting model 'DataPoint'
        db.delete_table(u'data_datapoint')

        # Deleting model 'Chart'
        db.delete_table(u'data_chart')

        # Deleting model 'ChartSeries'
        db.delete_table(u'data_chartseries')

        # Deleting model 'Dashboard'
        db.delete_table(u'data_dashboard')

        # Removing M2M table for field charts on 'Dashboard'
        db.delete_table(db.shorten_name(u'data_dashboard_charts'))

        # Deleting model 'TabGroup'
        db.delete_table(u'data_tabgroup')

        # Deleting model 'TabPage'
        db.delete_table(u'data_tabpage')


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
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'stop': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': u"orm['auth.User']", 'to': u"orm['auth.User']"})
        },
        u'data.chartseries': {
            'Meta': {'ordering': "['name']", 'object_name': 'ChartSeries'},
            'axis': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'axislr': ('django.db.models.fields.CharField', [], {'default': "'l'", 'max_length': '2'}),
            'chart': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'series'", 'to': u"orm['data.Chart']"}),
            'color': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
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
            'charts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['data.Chart']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': u"orm['auth.User']", 'to': u"orm['auth.User']"})
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'offset': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'parameter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data.Parameter']", 'null': 'True', 'blank': 'True'}),
            'resample': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'scale': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'line'", 'max_length': '20', 'blank': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': u"orm['auth.User']", 'to': u"orm['auth.User']"})
        },
        u'data.sourcefile': {
            'Meta': {'unique_together': "(('name', 'datasource'),)", 'object_name': 'SourceFile'},
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