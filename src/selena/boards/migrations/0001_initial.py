# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Board'
        db.create_table('boards_board', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('boards', ['Board'])

        # Adding M2M table for field services on 'Board'
        db.create_table('boards_board_services', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('board', models.ForeignKey(orm['boards.board'], null=False)),
            ('service', models.ForeignKey(orm['services.service'], null=False))
        ))
        db.create_unique('boards_board_services', ['board_id', 'service_id'])


    def backwards(self, orm):
        # Deleting model 'Board'
        db.delete_table('boards_board')

        # Removing M2M table for field services on 'Board'
        db.delete_table('boards_board_services')


    models = {
        'boards.board': {
            'Meta': {'object_name': 'Board'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['services.Service']", 'symmetrical': 'False'})
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

    complete_apps = ['boards']