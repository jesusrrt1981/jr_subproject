# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)



class ProjectInherit(models.Model):
    _inherit = "project.project"

    bol_p=fields.Boolean(compute="_get_bol",store=True)

    def _get_bol(self):
        for line in self:

            if len(line.sub_project_ids)>0:
                line.bol_p=True
            else:
                line.bol_p=False

    def open_child_projects(self):
        self.ensure_one()
        if self.bol_p:
            child_project_ids = self.sub_project_ids.mapped('p_project_id.id')
            action = self.env.ref('jr_subproject.action_view_child_projects').read()[0]  # Reemplaza 'tu_modulo' con el nombre de tu módulo.
            action['context'] = {'child_projects_ids': child_project_ids}
            return action
        return True
    
    def button_view_tasks_in_kanban(self):
        self.ensure_one()
        action = self.env.ref('project.action_view_task').read()[0]
        action['domain'] = [('project_id', '=', self.id)]
      
        action['views'] = [(self.env.ref('project.view_task_kanban').id, 'kanban')]
        return action


class ProjectInherit1(models.Model):
    _inherit = "project.task"
    @api.model
    def create(self, vals):
        # Si estamos en "modo de copia", simplemente llamamos al create original
        if self._context.get('in_copy_mode'):
            return super(ProjectInherit1, self).create(vals)

        res = super(ProjectInherit1, self).create(vals)


        obj = self.env["project.project"].search([("sub_project_ids.p_project_id", "=", res.project_id.id)], limit=1)
      
        if obj.id:
            prst=self.env["project.task.type"].search([("id", "=",vals.get("stage_id"))], limit=1)
            
            st = self.env["project.task.type"].search([("name", "=", prst.name),("project_ids","in",obj.ids)], limit=1)
            stage = st.id if st else False
            
            new_task_vals = vals.copy()
            new_task_vals.update({
                "project_id": obj.id,
                "stage_id": stage  # Asumiendo que 'stage_id' es el nombre correcto del campo
            })

            # Crear el nuevo registro con el contexto 'in_copy_mode' para evitar recursión
            self.env["project.task"].with_context(in_copy_mode=True).create(new_task_vals)

        return res





        




   
