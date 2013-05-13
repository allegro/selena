# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Queue'
        db.create_table(u'services_queue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75, db_index=True)),
        ))
        db.send_create_signal(u'services', ['Queue'])

        # Adding model 'Agent'
        db.create_table(u'services_agent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75, db_index=True)),
            ('is_main', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('queue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['services.Queue'], null=True, on_delete=models.PROTECT, blank=True)),
            ('salt', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal(u'services', ['Agent'])

        # Adding model 'Service'
        db.create_table(u'services_service', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('response_code', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=200)),
            ('performance_issues_time', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=15)),
            ('connection_timeout', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=30)),
            ('performance_issues_min_probes_count', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=8)),
            ('service_not_working_min_probes_count', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=8)),
            ('time_delta', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=10)),
            ('base_useragent', self.gf('django.db.models.fields.CharField')(default=u'Mozilla/5.0 (X11; U; Linux x86_64; pl-PL; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3', max_length=250)),
            ('base_referer', self.gf('django.db.models.fields.URLField')(default=u'', max_length=200, null=True, blank=True)),
            ('auth_user', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('auth_pass', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('is_technical_break', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('is_core_service', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('hosting', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('comments', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=100)),
            ('sensitivity', self.gf('django.db.models.fields.DecimalField')(default='0.5', max_digits=3, decimal_places=2)),
            ('auth_method', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1, db_index=True)),
        ))
        db.send_create_signal(u'services', ['Service'])

        # Adding M2M table for field additional_agents on 'Service'
        db.create_table(u'services_service_additional_agents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('service', models.ForeignKey(orm[u'services.service'], null=False)),
            ('agent', models.ForeignKey(orm[u'services.agent'], null=False))
        ))
        db.create_unique(u'services_service_additional_agents', ['service_id', 'agent_id'])

        # Adding model 'MonitoredPhrase'
        db.create_table(u'services_monitoredphrase', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phrase', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('shall_not_be', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['services.Service'])),
        ))
        db.send_create_signal(u'services', ['MonitoredPhrase'])

        # Adding model 'AdditionalRequestParam'
        db.create_table(u'services_additionalrequestparam', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('useragent', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('referer', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('post', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('get', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['services.Service'])),
        ))
        db.send_create_signal(u'services', ['AdditionalRequestParam'])

        # Adding model 'ServiceHistory'
        db.create_table(u'services_servicehistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('service_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('response_state', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1, db_index=True)),
            ('request_params_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('agent_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('response_code', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('response_time', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('namelookup_time', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('connect_time', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('pretransfer_time', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('starttransfer_time', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('redirect_time', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('size_download', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('speed_download', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('redirect_count', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('num_connects', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('main_probe', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True)),
            ('tick_failed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'services', ['ServiceHistory'])

        # Adding model 'ServiceHistoryExtra'
        db.create_table(u'services_servicehistoryextra', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('service_history_id', self.gf('django.db.models.fields.BigIntegerField')(db_index=True)),
            ('effective_url', self.gf('django.db.models.fields.URLField')(max_length=500, null=True, blank=True)),
            ('error_msg', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('wordchecks_errors', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
        ))
        db.send_create_signal(u'services', ['ServiceHistoryExtra'])

        # Adding model 'ServiceHistoryArchive'
        db.create_table(u'services_servicehistoryarchive', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('service_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('agent_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('response_time', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('namelookup_time', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('connect_time', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('pretransfer_time', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('starttransfer_time', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('redirect_time', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('size_download', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('speed_download', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('redirect_count', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('num_connects', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
        ))
        db.send_create_signal(u'services', ['ServiceHistoryArchive'])

        # BIGINT
        db.execute("ALTER TABLE `services_servicehistory` CHANGE COLUMN `id` `id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT")
        db.execute("ALTER TABLE `services_servicehistory` CHANGE `main_probe` `main_probe` BIGINT UNSIGNED NOT NULL")
        db.execute("ALTER TABLE `services_servicehistoryarchive` CHANGE COLUMN `id` `id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT")
        db.execute("ALTER TABLE `services_servicehistoryextra` CHANGE COLUMN `id` `id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT")
        db.execute("ALTER TABLE `services_servicehistoryextra` CHANGE `service_history_id` `service_history_id` BIGINT UNSIGNED NOT NULL")

        # PARTITIONS
        db.execute("ALTER TABLE `services_servicehistory` DROP PRIMARY KEY , ADD PRIMARY KEY (`id`, `created`)")
        db.execute("ALTER TABLE `services_servicehistory` CHANGE COLUMN `response_time` `response_time` DECIMAL(5,2) UNSIGNED NOT NULL  , CHANGE COLUMN `namelookup_time` `namelookup_time` DECIMAL(5,2) UNSIGNED NULL DEFAULT NULL  , CHANGE COLUMN `connect_time` `connect_time` DECIMAL(5,2) UNSIGNED NULL DEFAULT NULL  , CHANGE COLUMN `pretransfer_time` `pretransfer_time` DECIMAL(5,2) UNSIGNED NULL DEFAULT NULL  , CHANGE COLUMN `starttransfer_time` `starttransfer_time` DECIMAL(5,2) UNSIGNED NULL DEFAULT NULL  , CHANGE COLUMN `redirect_time` `redirect_time` DECIMAL(5,2) UNSIGNED NULL DEFAULT NULL  , CHANGE COLUMN `size_download` `size_download` INT(11) UNSIGNED NULL DEFAULT NULL  , CHANGE COLUMN `speed_download` `speed_download` INT(11) UNSIGNED NULL DEFAULT NULL")
        db.execute("ALTER TABLE `services_servicehistoryarchive` CHANGE COLUMN `response_time` `response_time` DECIMAL(5,2) UNSIGNED NOT NULL  , CHANGE COLUMN `namelookup_time` `namelookup_time` DECIMAL(5,2) UNSIGNED NULL DEFAULT NULL  , CHANGE COLUMN `connect_time` `connect_time` DECIMAL(5,2) UNSIGNED NULL DEFAULT NULL  , CHANGE COLUMN `pretransfer_time` `pretransfer_time` DECIMAL(5,2) UNSIGNED NULL DEFAULT NULL  , CHANGE COLUMN `starttransfer_time` `starttransfer_time` DECIMAL(5,2) UNSIGNED NULL DEFAULT NULL  , CHANGE COLUMN `redirect_time` `redirect_time` DECIMAL(5,2) UNSIGNED NULL DEFAULT NULL  , CHANGE COLUMN `size_download` `size_download` INT(11) UNSIGNED NULL DEFAULT NULL  , CHANGE COLUMN `speed_download` `speed_download` INT(11) UNSIGNED NULL DEFAULT NULL")
        db.execute("ALTER TABLE `services_servicehistoryarchive` DROP PRIMARY KEY , ADD PRIMARY KEY (`id`, `created`)")
        db.execute("ALTER TABLE `services_servicehistory` PARTITION BY RANGE (TO_DAYS(created)) (PARTITION p_other VALUES LESS THAN (0))")
        db.execute("ALTER TABLE `services_servicehistoryarchive` PARTITION BY RANGE (TO_DAYS(created)) (PARTITION p_other VALUES LESS THAN (0))")

    def backwards(self, orm):
        # Deleting model 'Queue'
        db.delete_table(u'services_queue')

        # Deleting model 'Agent'
        db.delete_table(u'services_agent')

        # Deleting model 'Service'
        db.delete_table(u'services_service')

        # Removing M2M table for field additional_agents on 'Service'
        db.delete_table('services_service_additional_agents')

        # Deleting model 'MonitoredPhrase'
        db.delete_table(u'services_monitoredphrase')

        # Deleting model 'AdditionalRequestParam'
        db.delete_table(u'services_additionalrequestparam')

        # Deleting model 'ServiceHistory'
        db.delete_table(u'services_servicehistory')

        # Deleting model 'ServiceHistoryExtra'
        db.delete_table(u'services_servicehistoryextra')

        # Deleting model 'ServiceHistoryArchive'
        db.delete_table(u'services_servicehistoryarchive')


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
            'performance_issues_min_probes_count': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '8'}),
            'performance_issues_time': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '15'}),
            'response_code': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '200'}),
            'sensitivity': ('django.db.models.fields.DecimalField', [], {'default': "'0.5'", 'max_digits': '3', 'decimal_places': '2'}),
            'service_not_working_min_probes_count': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '8'}),
            'time_delta': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '10'}),
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