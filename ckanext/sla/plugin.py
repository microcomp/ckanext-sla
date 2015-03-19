import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from sla_db import SLA
from ckanext.sla.sla_db import SLA_Mapping
import logging
from ckan.model.user import User

log = logging.getLogger('ckanext')


def sla_statistics():
    statistics = SLA.getCountUserPerSLA()
    table_stat = []
    for entry in statistics:
        sla_name = entry[0].name
        count = entry[1]
        data_dict = {'name' : sla_name,
                     'count' : count}
        table_stat.append(data_dict)
    return table_stat

def user_id_to_name(id):
    user_detail = toolkit.get_action('user_show')(data_dict={'id' : id})
    return user_detail.get('name', None)

def user_sla(id):
    search = {'user_id' : id}
    result = SLA_Mapping.getSLA(**search)
    if len(result)==1:
        return result[0].name
    return toolkit._('Default SLA')


class SlaPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=False)
    
    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        
    def before_map(self, map):
        map.connect('sla_main','/admin/sla', action='list', controller='ckanext.sla.sla:SlaController')
        map.connect('sla_detail','/admin/sla/detail/{id}', action='sla_detail', controller='ckanext.sla.sla:SlaController')
        map.connect('sla_management','/admin/sla/manage', action='manage', controller='ckanext.sla.sla:SlaController')
        map.connect('sla_edit','/admin/sla/edit', action='edit', controller='ckanext.sla.sla:SlaController')
        map.connect('sla_new','/admin/sla/new', action='add', controller='ckanext.sla.sla:SlaController')
        map.connect('sla_assign','/admin/sla/assign', action='map_user_sla', controller='ckanext.sla.sla:SlaController')
        map.connect('sla_delete','/admin/sla/delete', action='delete', controller='ckanext.sla.sla:SlaController')
        map.connect('sla__rel_sdelete','/admin/sla/delete_rel', action='delete_relationship', controller='ckanext.sla.sla:SlaController')
        return map
    
    def get_helpers(self):
        return {'sla_statistics' : sla_statistics,
                'user_id_to_name' : user_id_to_name,
                'user_sla' : user_sla}