import logging
import sla_db
import ckan.lib.base as base
import ckan.plugins.toolkit as tk
import ckan.model as model
from hurry.filesize import size
import ckan.logic as logic
from ckan.common import _, c

log = logging.getLogger('ckanext')

class SlaController(base.BaseController):
     def list(self):
         return base.render('sla/index.html')
     def manage(self):
         pass