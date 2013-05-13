# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TechnicalBreak'
        db.create_table('planner_technicalbreak', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_desciption', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('date_from', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_to', self.gf('django.db.models.fields.DateTimeField')()),
            ('activated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['services.Service'])),
        ))
        db.send_create_signal('planner', ['TechnicalBreak'])


    def backwards(self, orm):
        # Deleting model 'TechnicalBreak'
        db.delete_table('planner_technicalbreak')


    models = {
        'planner.technicalbreak': {
            'Meta': {'object_name': 'TechnicalBreak'},
            'activated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_from': ('django.db.models.fields.DateTimeField', [], {}),
            'date_to': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['services.Service']"}),
            'short_desciption': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'services.service': {
            'Meta': {'ordering': "['name']", 'object_name': 'Service'},
            'auth_pass': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'auth_user': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'base_referer': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'base_useragent': ('django.db.models.fields.CharField', [], {'default': "'Mozilla/5.0 (X11; U; Linux x86_64; pl-PL; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3'", 'max_length': '250'}),
            'connection_timeout': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '30'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_status': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_technical_break': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            'performance_issues_min_probes_count': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '8'}),
            'performance_issues_time': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '15'}),
            'service_not_working_min_probes_count': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '8'}),
            'time_delta': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '10'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['planner']