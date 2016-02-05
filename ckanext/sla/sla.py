import logging
from sla_db import SLA, SLA_Mapping, sla_mapping_table, sla_table
import ckan.lib.base as base
import ckan.plugins.toolkit as tk
import ckan.model as model
from hurry.filesize import size
import ckan.logic as logic
from ckan.common import _, c, request
import ckan.lib.helpers as h
import ckan.lib.dictization as dictization
from ckan.model.meta import Session
from sqlalchemy import exc

log = logging.getLogger(__name__)

class SlaController(base.BaseController):
    def _check_access(self, user):
        context = {'user' : user}
        try:
            logic.check_access('sla_management', context)
        except tk.NotAuthorized, e:
            log.info(e.extra_msg)
            tk.abort(401, e.extra_msg)
    
    def sla_detail(self, id):
        search = {'id' : id}
        sla = SLA.get(**search)
        if len(sla)==1:
            sla_instance = sla[0]
            data_detail =  dictization.table_dictize(sla_instance, context = {'model' : model})
            search = {'sla_id' : id}
            relationships = SLA_Mapping.getAllDetails(**search)
            data_users = []
            if len(relationships)!=0:
                for rel in relationships:
                    user = rel[0]
                    data_dict = {'id' : user.id,
                                 'name' : user.name}
                    data_users.append(data_dict)
            
            return base.render('sla/sla_detail.html', extra_vars = {'data_detail' : data_detail,
                                                                    'data_users' : data_users})
            
    def delete(self):
        self._check_access(c.user)
        data = request.GET
        if 'id' in data.keys():
            search = {'id' : data['id']}
            log.info(search)
            res = SLA.getCountUserPerSLA(**search)
            log.info('res: %s', res)
            if len(res)==1:
                if res[0][1]==0:
                    sla_table.delete(SLA.id==data['id']).execute()
                    message = _('SLA {0} was deleted!')
                    message = message.format(res[0][0].name)
                    h.flash_success(message)
                    return self.manage()
                else:
                    message = _('You can not delete SLA {0}, because of assigned users to it!')
                    message = message.format(res[0][0].name)
                    h.flash_error(message)
                    return self.manage()
                
    def delete_relationship(self):
        self._check_access(c.user)
        data = request.GET
        if 'id' in data.keys():
            search = {'id' : data['id']}
            res = SLA_Mapping.get(**search)
            if len(res)==1:
                user_detail = tk.get_action('user_show')(data_dict={'id' : res[0].user_id})
                sla_mapping_table.delete(SLA_Mapping.id==data['id']).execute()
                message = _('The SLA of user {0} was removed.')
                message = message.format(user_detail['name'])
                h.flash_success(message)
                return self.list()
                

    def list(self):
        self._check_access(c.user)
        table_results = []
        entries = SLA_Mapping.getAllDetails()
        for entry in entries:
            user = entry[0]
            sla = entry[1]
            n = "{} ({})".format(user.fullname, user.name)
            data_dict = {'user_id' : user.id,
                         'user_name' : n,
                         'sla_id' : sla.id,
                         'sla_name' : sla.name}
            table_results.append(data_dict)
        return base.render('sla/index.html', extra_vars = {'results' : table_results})
     
    def manage(self):
        self._check_access(c.user)
        data = request.POST
        log.info('request post data : %s', data.keys())
        registered_sla = SLA.getAll()
        log.info('registered sla: %s', registered_sla)
        return base.render('sla/edit.html', extra_vars={'data' : data, 'registered_sla' : registered_sla})

    def map_user_sla(self):
        self._check_access(c.user)
        data = request.POST
        if 'save' in data.keys():
            log.info('received data: %s', data)
            user_id = data['user']
            sla_id = data['sla']
            errors = self._validate_mapping_data(data)
            if errors:
                if errors.get('duplicate', None):
                    h.flash_notice(_('This relationship already exists. Nothing has been changed.'))
                    return self.list()
                users = tk.get_action('user_list')(data_dict={})
                not_defined = {'value' : 'not_defined', 'text' : _('Not defined')}
                users_var = []
                users_var.append(not_defined)
                for user in users:
                    n = "{} ({})".format(user['fullname'], user['name'])
                    users_var.append({'value' : user['id'], 'text' : n})
                registered_sla = SLA.getAll()
                sla_var = []
                sla_var.append(not_defined)
                for sla in registered_sla:
                    sla_var.append({'value' : sla.id, 'text' : sla.name})
                return base.render('sla/assign_sla.html', extra_vars={'users' : users_var,
                                                                      'sla' : sla_var,
                                                                      'errors' : errors,
                                                                      'data' : data})
            else:
                user_detail = tk.get_action('user_show')(data_dict={'id' : user_id})
                if data.get('rel_id', None):
                    self._edit_mapping(data['rel_id'], user_detail['name'], sla_id)
                else:
                    self._add_mapping(user_id, user_detail['name'], sla_id)
                return self.list()
        users_var = None
        not_defined = {'value' : 'not_defined', 'text' : _('Not defined')}
        if not data.get('rel_id', None):
            users = tk.get_action('user_list')(data_dict={})
            users_var = []
            users_var.append(not_defined)
            for user in users:
                n = "{} ({})".format(user['fullname'], user['name'])
                users_var.append({'value' : user['id'], 'text' : n})
        registered_sla = SLA.getAll()
        sla_var = []
        sla_var.append(not_defined)
        for sla in registered_sla:
            sla_var.append({'value' : sla.id, 'text' : sla.name})
        data_get = request.GET
        data = {}
        if 'user_id' in data_get.keys():
            data['user'] = data_get['user_id']
        if 'sla_id' in data_get.keys():
            data['sla'] = data_get['sla_id']
        if data.get('user', None) and data.get('sla', None):
            search = {'user_id' : data['user'],
                      'sla_id' : data['sla']}
            res = SLA_Mapping.get(**search)
            if len(res)==1:
                data['rel_id'] = res[0].id
                data['user_name'] = tk.get_action('user_show')(data_dict={'id' : data['user']}).get('name', None)
        return base.render('sla/assign_sla.html', extra_vars={'users' : users_var,
                                                              'sla' : sla_var,
                                                              'errors' : None,
                                                              'data' : data})
        
    def _validate_mapping_data(self, data_dict):
        errors = {}
        if data_dict['user']=='not_defined':
            errors['user'] = (_('Please select a user.'),)
        if data_dict['sla']=='not_defined':
            errors['sla'] = (_('Please select a SLA for user.'),)
        if not errors:
            if data_dict.get('rel_id', None):
                search = {'user_id' : data_dict['user'],
                          'id' : data_dict['rel_id']}
                res = SLA_Mapping.get(**search)
                if not res:
                    errors['user'] = (_('You can not change user. You are allowed to change SLA of user!'),)
            else:
                search = {'user_id' : data_dict['user']}
                res = SLA_Mapping.get(**search)
                if res:
                    if res[0].sla_id!=data_dict['sla']:
                        errors['user'] = (_('This user has already asigned SLA!'),)
                    else:
                        errors['duplicate'] = 'Dont allow to create duplicates'
        return errors
            
        
    def _add_mapping(self, user_id, user_name, sla_id):
        log.info('assigning SLA')
        new_map = SLA_Mapping(user_id, sla_id)
        new_map.save()
        message = _("New SLA was assigned to the user {0}")
        h.flash_success(message.format(user_name))
        
    def _edit_mapping(self, rel_id, user_name, sla_id):
        log.info('editing SLA')
        search = {'id' : rel_id}
        existing_map = SLA_Mapping.get(**search)
        if len(existing_map)==1:
            existing_map[0].sla_id = sla_id
            existing_map[0].save()
            message = _("The SLA of the user {0} was changed.")
            h.flash_success(message.format(user_name))
        
    def add(self):
        self._check_access(c.user)
        data = request.POST
        log.info('received data sla: %s', data)
        if 'save' in data.keys():
            errors = self._validate_sla_data(data)
            if errors:
                return base.render('sla/add_sla.html', extra_vars={'data' : data,
                                                               'errors' : errors})
            log.info("creating new sla")
            try:
                self._add_sla(data['name'],
                              data['level'],
                              data['rate_rq_s'],
                              data['speed_bytes_s'],
                              data['timeout_s'],
                              data['default_for_anonymous_users'],
                              data['default_for_authenticated_users'])
            except exc.IntegrityError as e:
                log.exception(e)
                Session.rollback()
                h.flash_error(_("Integrity error. PLease try again!"))
                return base.render('sla/add_sla.html', extra_vars={'data' : data,
                                                               'errors' : None})
                
            registered_sla = SLA.getAll()
            log.info('registered sla: %s', registered_sla)
            return base.render('sla/edit.html', extra_vars={'registered_sla' : registered_sla})
        return base.render('sla/add_sla.html', extra_vars={'data' : None, 'errors' : None})
        
    
    def edit(self):
        self._check_access(c.user)
        data_post = request.POST
        if 'save' in data_post.keys():
            errors = self._validate_sla_data(data_post)
            if errors:
                search = {'id' : data_post['id']}
                result = SLA.get(**search)
                if len(result)==1:
                    sla_instance = result[0]
                    data  = dictization.table_dictize(sla_instance, context = {'model' : model})
                    return base.render('sla/edit_sla.html', extra_vars={'data' : data, 'errors' : errors })
            try:
                self._edit_sla(data_post['id'],
                               data_post['name'],
                               data_post['level'],
                               data_post['rate_rq_s'],
                               data_post['speed_bytes_s'],
                               data_post['timeout_s'],
                               data_post['default_for_anonymous_users'],
                               data_post['default_for_authenticated_users'])
            except exc.IntegrityError as e:
                log.exception(e)
                Session.rollback()
                h.flash_error(_("Integrity error. PLease try again!"))
                return base.render('sla/edit_sla.html', extra_vars={'data' : data_post,
                                                               'errors' : None})
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
                data = dictization.table_dictize(sla_instance, context = {'model' : model})     
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
            val = int(data_dict['level'])
        except ValueError:
            errors['level'] = ('This attribute has to be an integer. Please enter a valid value.',)
         
        search = {'level' : data_dict['level']}
        result = SLA.get(**search)
        if result and (not data_dict.get('id',None) or (data_dict.get('id',None) and result[0].id!=data_dict['id'])):
            errors['level'] = ('SLA with this level already exists. Please change the value.',)
        
        try:
            val = int(data_dict['rate_rq_s'])
        except ValueError:
            errors['rate_rq_s'] = ('This attribute has to be an integer. Please enter a valid value.',)
        
        try:
            val = float(data_dict['speed_bytes_s'])
        except ValueError:
            errors['speed_bytes_s'] = ('This attribute has to be a number. Please enter a valid value.',)
        
        try:
            val = int(data_dict['timeout_s'])
        except ValueError:
            errors['timeout_s'] = ('This attribute has to be an integer. Please enter a valid value.',)
        
        try:
            log.info('validation anon user')
            val = bool(data_dict.get('default_for_anonymous_users', False))
            data_dict['default_for_anonymous_users'] = val
            search = {'default_for_anonymous_users' : True}
            result = SLA.get(**search)
            log.info('search result: %s', result)
            if result and ((not data_dict.get('id',None) and val) or (data_dict.get('id',None) and result[0].id!=data_dict['id'] and val)):
                errors['default_for_anonymous_users'] = ('There is already default SLA for anonymous users. It is not possible to have more than 1 default SLA.',)
        except ValueError:
            errors['default_for_anonymous_users'] = ('This attribute has to be an boolean. Please enter a valid value.',)
        
        try:
            log.info('validation auth user')
            val = bool(data_dict.get('default_for_authenticated_users', False))
            data_dict['default_for_authenticated_users'] = val
            search = {'default_for_authenticated_users' : True}
            result = SLA.get(**search)
            log.info('search result: %s', result)
            if result and ((not data_dict.get('id',None) and val) or (data_dict.get('id',None) and result[0].id!=data_dict['id'] and val)):
                errors['default_for_authenticated_users'] = ('There is already default SLA for authenticated users. It is not possible to have more than 1 default SLA.',)
        except ValueError:
            errors['default_for_authenticated_users'] = ('This attribute has to be an boolean. Please enter a valid value.',)
        
        return errors

            
    def _add_sla(self, name, number, rqs, mbs, priority, default_anon_user, default_auth_user):
        new_sla = SLA(name, number, rqs, mbs, priority, default_anon_user, default_auth_user)
        new_sla.save()
        h.flash_success(_("New SLA was registered"))
    
    def _edit_sla(self, id, new_name, new_level, new_rqs, new_bytes, new_timeout, new_default_anon_user, new_default_auth_user):
        search = {'id' : id}
        result = SLA.get(**search)
        if len(result)==1:
            updated_sla = result[0]
            updated_sla.name = new_name
            updated_sla.level = new_level
            updated_sla.rate_rq_s = new_rqs
            updated_sla.speed_bytes_s = new_bytes
            updated_sla.timeout_s = new_timeout
            updated_sla.default_for_anonymous_users = new_default_anon_user
            updated_sla.default_for_authenticated_users = new_default_auth_user
            updated_sla.save()
            h.flash_success(_("SLA was updated"))
        else:
            h.flash_error(_("Unable to edit the given SLA. Couldn't retrieve object from database."))
        
