import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from sla_db import SLA


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


class SlaPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=False)
    
    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        
    def before_map(self, map):
        map.connect('sla_main','/admin/sla', action='list', controller='ckanext.sla.sla:SlaController')
        map.connect('sla_management','/admin/sla/manage', action='manage', controller='ckanext.sla.sla:SlaController')
        map.connect('sla_edit','/admin/sla/edit', action='edit', controller='ckanext.sla.sla:SlaController')
        map.connect('sla_new','/admin/sla/new', action='add', controller='ckanext.sla.sla:SlaController')
        map.connect('sla_assign','/admin/sla/assign', action='map_user_sla', controller='ckanext.sla.sla:SlaController')
        map.connect('sla_delete','/admin/sla/delete', action='delete', controller='ckanext.sla.sla:SlaController')
        return map
    
    def get_helpers(self):
        return {'sla_statistics' : sla_statistics}