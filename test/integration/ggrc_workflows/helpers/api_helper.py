# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Package contains Workflow related helper functions for REST API calls."""

from ggrc import utils
from ggrc.access_control import role
from ggrc.models import all_models

from integration.ggrc import api_helper
from integration.ggrc.models import factories


def _get_object_subdict(obj):
  return {
      "id": obj.id,
      "href": utils.url_for(obj),
      "type": obj.type,
  }


def _get_acl_subdict(acr_name, person, model):
  """Generate ACL sub-dict representation for using inside JSON.

  Args:
      acr_name: Access Control Role name.
      person: Person instance, who should get `acr_name` in scope of `model`.
      model: Model, in which scope ACR should be assigned to `person`.
  Returns:
      ACL entry sub-dict representation. It is used for inserting into object
      JSON representation under 'access_control_list' key.
  """
  acr = role.get_ac_roles_for(model.__name__)[acr_name]
  return {
      "ac_role_id": acr.id,
      "person": _get_object_subdict(person)
  }


class WorkflowApi(api_helper.Api):
  """Workflow related helper for REST API calls."""

  @classmethod
  def get_task_group_post_dict(cls, workflow, contact):
    """Get TaskGroup JSON representation for POST API call.

    Args:
        workflow: Workflow instance which TaskGroup should belong to.
        contact: Person instance which should become TaskGroup Assignee.
    Returns:
        TaskGroup object dict representation for using in POST request.
    """
    return {
        "task_group": {
            "custom_attributes": {},
            "contact": _get_object_subdict(contact),
            "workflow": _get_object_subdict(workflow),
            "context": _get_object_subdict(workflow.context),
            "modal_title": "Create Task Group",
            "title": factories.random_str(prefix="tg_"),
            "description": factories.random_str(length=64),
            "slug": "",
        }
    }

  @classmethod
  def get_task_group_object_post_dict(cls, task_group, obj_map):
    """Get TaskGroupObject JSON representation for POST API call.

    Args:
        task_group: TaskGroup instance which TaskGroupObject should belong to.
        obj_map: Object which should be mapped to TaskGroup.
    Returns:
        TaskGroupObject object dict representation for using in POST request.
    """
    return {
        "task_group_object": {
            "context": _get_object_subdict(task_group.context),
            "task_group": _get_object_subdict(task_group),
            "object": _get_object_subdict(obj_map),
        }
    }

  @classmethod
  def get_task_post_dict(cls, task_group, people_roles, start_date, end_date):
    """Get TaskGroupTask JSON representation for POST API call.

    Args:
        task_group: TaskGroup instance which TaskGroupTask should belong to.
        people_roles: Mapping like {'ACR name': Person instance}
        start_date: String date representation.
        end_date: String date representation.
    Returns:
        TaskGroupTask object dict representation for using in POST request.
    """
    access_control_list = []
    for acr_name, person in people_roles.iteritems():
      access_control_list.append(
          _get_acl_subdict(acr_name, person, all_models.TaskGroupTask)
      )
    return {
        "task_group_task": {
            "response_options": [],
            "start_date": start_date,
            "end_date": end_date,
            "access_control_list": access_control_list,
            "custom_attributes": {},
            "task_group": _get_object_subdict(task_group),
            "context": _get_object_subdict(task_group.context),
            "modal_title": "Create New Task",
            "title": factories.random_str(prefix="tgt_"),
            "task_type": "text",
            "description": factories.random_str(length=64),
            "slug": ""
        }
    }

  @classmethod
  def get_cycle_post_dict(cls, workflow):
    """Get Cycle JSON representation for POST API call.

    Args:
        workflow: Workflow instance which Cycle should belong to.
    Returns:
        Cycle object dict representation for using in POST request.
    """
    return {
        "cycle": {
            "context": _get_object_subdict(workflow.context),
            "workflow": _get_object_subdict(workflow),
            "autogenerate": True,
            "isOverdue": False
        }
    }

  @classmethod
  def get_cycle_task_entry_post_dict(cls, cycle_task):
    """Get CycleTaskEntry JSON representation for POST API call.

    Args:
        cycle_task: CycleTaskGroupObjectTask instance which CycleTaskEntry
            should belong to.
    Returns:
        CycleTaskEntry object dict representation for using in POST request.
    """
    return {
        "cycle_task_entry": {
            "custom_attributes": {},
            "cycle_task_group_object_task": _get_object_subdict(cycle_task),
            "cycle": _get_object_subdict(cycle_task.cycle),
            "context": _get_object_subdict(cycle_task.context),
            "is_declining_review": "",
            "description": factories.random_str(length=64),
        }
    }
