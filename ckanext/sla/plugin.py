import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

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
        return map
    
    def get_helpers(self):
        return {}