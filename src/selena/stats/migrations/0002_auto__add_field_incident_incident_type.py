# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Incident.incident_type'
        db.add_column(u'stats_incident', 'incident_type',
                      self.gf('django.db.models.fields.CharField')(default=u'failure', max_length=15),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Incident.incident_type'
        db.delete_column(u'stats_incident', 'incident_type')


    models = {
        u'services.agent': {
            'Meta': {'object_name': 'Agent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'is_main': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'queue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['services.Queue']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'salt': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        u'services.queue': {
            'Meta': {'object_name': 'Queue'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'})
        },
        u'services.service': {
            'Meta': {'ordering': "[u'name']", 'object_name': 'Service'},
            'additional_agents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['services.Agent']", 'null': 'True', 'blank': 'True'}),
            'auth_method': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'auth_pass': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'auth_user': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'base_referer': ('django.db.models.fields.URLField', [], {'default': "u''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'base_useragent': ('django.db.models.fields.CharField', [], {'default': "u'Mozilla/5.0 (X11; U; Linux x86_64; pl-PL; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3'", 'max_length': '250'}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'connection_timeout': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '30'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hosting': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'is_core_service': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_technical_break': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            'performance_issues_min_probes_count': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '8'}),
            'performance_issues_time': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '15'}),
            'response_code': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '200'}),
            'sensitivity': ('django.db.models.fields.DecimalField', [], {'default': "'0.5'", 'max_digits': '3', 'decimal_places': '2'}),
            'service_not_working_min_probes_count': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '8'}),
            'service_working_min_probes_count': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '5'}),
            'time_delta': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '10'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'stats.incident': {
            'Meta': {'object_name': 'Incident'},
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incident_type': ('django.db.models.fields.CharField', [], {'default': "u'failure'", 'max_length': '15'}),
            'is_closed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['services.Service']"}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['stats']