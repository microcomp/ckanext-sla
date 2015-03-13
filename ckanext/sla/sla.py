import logging
from sla_db import SLA, SLA_Mapping, sla_mapping_table, sla_table
import ckan.lib.base as base
import ckan.plugins.toolkit as tk
import ckan.model as model
from hurry.filesize import size
import ckan.logic as logic
from ckan.common import _, c, request
import ckan.lib.helpers as h

log = logging.getLogger('ckanext')

class SlaController(base.BaseController):
    def list(self):
        return base.render('sla/index.html')
     
    def manage(self):
        data = request.POST
        log.info('request post data : %s', data.keys())
        registered_sla = SLA.getAll()
        log.info('registered sla: %s', registered_sla)
        return base.render('sla/edit.html', extra_vars={'data' : data,
                                                        'registered_sla' : registered_sla})
    
    def add(self):
        data = request.POST
        if 'save' in data.keys():
            errors = self._validate_sla_data(data)
            if errors:
                return base.render('sla/add_sla.html', extra_vars={'data' : data,
                                                                   'errors' : errors})
            log.info("creating new sla")
            self._add_sla(data['name'], data['number'], data['rqs'], data['speed'], data['priority'])
            registered_sla = SLA.getAll()
            log.info('registered sla: %s', registered_sla)
            return base.render('sla/edit.html', extra_vars={'registered_sla' : registered_sla})
        return base.render('sla/add_sla.html', extra_vars={'data' : None, 'errors' : None})
        
    
    def edit(self):
        data_post = request.POST
        if 'save' in data_post.keys():
            errors = self._validate_sla_data(data_post)
            if errors:
                search = {'id' : data_post['id']}
                result = SLA.get(**search)
                if len(result)==1:
                    sla_instance = result[0]
                    data = {'id' : sla_instance.id,
                           'name' : sla_instance.name,
                           'number' : sla_instance.level,
                           'rqs' : sla_instance.rate_rq_s,
                           'speed' : sla_instance.speed_mb_s,
                           'priority' : sla_instance.priority}
                    return base.render('sla/edit_sla.html', extra_vars={'data' : data, 'errors' : errors })
            self._edit_sla(data_post['id'], data_post['name'], data_post['number'], data_post['rqs'], data_post['speed'], data_post['priority'])
            registered_sla = SLA.getAll()
            return base.render('sla/edit.html', extra_vars={'data' : None,
                                                            'registered_sla' : registered_sla})
        
        data = request.GET
        log.info('data keys: %s', data.keys())
        if 'id' in data.keys():
            search = {'id' : data['id']}
            result = SLA.get(**search)
            if len(result)==1:
                sla_instance = result[0]
                data = {'id' : sla_instance.id,
                       'name' : sla_instance.name,
                       'number' : sla_instance.level,
                       'rqs' : sla_instance.rate_rq_s,
                       'speed' : sla_instance.speed_mb_s,
                       'priority' : sla_instance.priority}
        
            return base.render('sla/edit_sla.html', extra_vars={'data' : data, 'errors' : None })
    
    def _validate_sla_data(self, data_dict):
        name = {'name' : data_dict['name']}
        errors = {}
        if data_dict['name']=='':
            errors['name'] = ('Please enter a name of new SLA.',)
        else:
            result = SLA.get(**name)
            if data_dict.get('id',None):
                if not (len(result)==1 and result[0].id==data_dict['id']) and not len(result)==0:
                    errors['name'] = ('SLA name has to be unique. Please change the name and try again.',)
            else:
                if result:
                    errors['name'] = ('SLA name has to be unique. Please change the name and try again.',)
                
        try:
            val = int(data_dict['number'])
        except ValueError:
            errors['number'] = ('This attribute has to be an integer. Please enter a valid value.',)
            
        try:
            val = int(data_dict['rqs'])
        except ValueError:
            errors['rqs'] = ('This attribute has to be an integer. Please enter a valid value.',)
        
        try:
            val = float(data_dict['speed'])
        except ValueError:
            errors['speed'] = ('This attribute has to be a number. Please enter a valid value.',)
        
        try:
            val = int(data_dict['priority'])
        except ValueError:
            errors['priority'] = ('This attribute has to be an integer. Please enter a valid value.',)
            
        return errors

            
    def _add_sla(self, name, number, rqs, mbs, priority):
        new_sla = SLA(name, number, rqs, mbs, priority)
        new_sla.save()
        h.flash_success(_("New SLA was registered"))
    
    def _edit_sla(self, id, new_name, new_number, new_rqs, new_mbs, new_priority):
        search = {'id' : id}
        result = SLA.get(**search)
        if len(result)==1:
            updated_sla = result[0]
            updated_sla.name = new_name
            updated_sla.level = new_number
            updated_sla.rate_rq_s = new_rqs
            updated_sla.speed_mb_s = new_mbs
            updated_sla.priority = new_priority
            updated_sla.save()
            h.flash_success(_("SLA was updated"))
        
