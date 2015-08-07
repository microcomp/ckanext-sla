from ckan.lib.cli import CkanCommand
import sys
import logging
from ckanext.sla.sla_db import sla_table, sla_mapping_table, create_sla_table
log = logging.getLogger('ckanext')
log.setLevel(logging.DEBUG)

class SlaCmd(CkanCommand):
    """Database initialization command
        Usage:
        sla-cmd initdb
        - initializes required db tables
    """
    
    summary = __doc__.split('\n')[0]
    usage = __doc__
    #max_args = 3
    #min_args = 0
    
    def __init__(self, name):
        super(SlaCmd, self).__init__(name)
    def command(self):
        self._load_config()
        
        if len(self.args) == 0:
            self.parser.print_usage()
            sys.exit(1)
        cmd = self.args[0]
        if cmd == 'initdb':
            log.info('Starting db initialization')
            if not sla_table.exists():
                log.info("creating sla table")
                create_sla_table()
                log.info("sla table created successfully")
            else:
                log.info("sla table already exists")
            if not sla_mapping_table.exists():
                log.info("creating sla_mapping table")
                sla_mapping_table.create()
                log.info("sla_mapping created successfully")
            else:
                log.info("sla_mapping already exists")
            log.info('End of db initialization')
        if cmd == 'uninstall':
            log.info('Starting uninstall command')
            if sla_table.exists():
                log.info("dropping sla table")
                sla_table.drop()
                log.info("dropped sla table successfully")
            if sla_mapping_table.exists():
                log.info("dropping sla mapping table")
                sla_mapping_table.drop()
                log.info("dropped sla mapping table successfully")
            else:
                log.info("Table sla doesn't exist")
            log.info('End of uninstall command')