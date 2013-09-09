# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Service.service_not_working_min_probes_count'
        db.delete_column(u'services_service', 'service_not_working_min_probes_count')

        # Deleting field 'Service.performance_issues_min_probes_count'
        db.delete_column(u'services_service', 'performance_issues_min_probes_count')

        # Adding field 'Service.service_working_min_probes_count'
        db.add_column(u'services_service', 'service_working_min_probes_count',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=5),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Service.service_not_working_min_probes_count'
        db.add_column(u'services_service', 'service_not_working_min_probes_count',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=8),
                      keep_default=False)

        # Adding field 'Service.performance_issues_min_probes_count'
        db.add_column(u'services_service', 'performance_issues_min_probes_count',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=8),
                      keep_default=False)

        # Deleting field 'Service.service_working_min_probes_count'
        db.delete_column(u'services_service', 'service_working_min_probes_count')


    models = {
        u'services.additionalrequestparam': {
            'Meta': {'object_name': 'AdditionalRequestParam'},
            'get': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'post': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'referer': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['services.Service']"}),
            'useragent': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        },
        u'services.agent': {
            'Meta': {'object_name': 'Agent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'is_main': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'queue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['services.Queue']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'salt': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        u'services.monitoredphrase': {
            'Meta': {'object_name': 'MonitoredPhrase'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'phrase': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['services.Service']"}),
            'shall_not_be': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
            'performance_issues_time': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '15'}),
            'response_code': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '200'}),
            'sensitivity': ('django.db.models.fields.DecimalField', [], {'default': "'0.5'", 'max_digits': '3', 'decimal_places': '2'}),
            'service_working_min_probes_count': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '5'}),
            'time_delta': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '3'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'services.servicehistory': {
            'Meta': {'ordering': "[u'-created']", 'object_name': 'ServiceHistory'},
            'agent_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'connect_time': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_probe': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'namelookup_time': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'num_connects': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pretransfer_time': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'redirect_count': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'redirect_time': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'request_params_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'response_code': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'response_state': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'response_time': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'service_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'size_download': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'speed_download': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'starttransfer_time': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'tick_failed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'services.servicehistoryarchive': {
            'Meta': {'ordering': "[u'-created']", 'object_name': 'ServiceHistoryArchive'},
            'agent_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'connect_time': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'namelookup_time': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'num_connects': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pretransfer_time': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'redirect_count': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'redirect_time': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'response_time': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'service_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'size_download': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'speed_download': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'starttransfer_time': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'})
        },
        u'services.servicehistoryextra': {
            'Meta': {'object_name': 'ServiceHistoryExtra'},
            'effective_url': ('django.db.models.fields.URLField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'error_msg': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service_history_id': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'wordchecks_errors': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['services']