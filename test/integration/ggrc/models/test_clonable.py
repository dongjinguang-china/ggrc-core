# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Integration test for Clonable mixin"""

from ggrc import db
from ggrc import models
from ggrc.access_control.list import AccessControlList
from ggrc.access_control.role import AccessControlRole
from ggrc.snapshotter.rules import Types

from integration.ggrc import generator
from integration.ggrc.models import factories
from integration.ggrc.snapshotter import SnapshotterBaseTestCase

from mock import patch


class TestClonable(SnapshotterBaseTestCase):

  """Test case for Clonable mixin"""

  # pylint: disable=invalid-name

  def setUp(self):
    # pylint: disable=super-on-old-class
    # pylint seems to get confused, mro chain successfully resolves and returns
    # <type 'object'> as last entry.
    super(TestClonable, self).setUp()

    self.client.get("/login")
    self.generator = generator.Generator()
    self.object_generator = generator.ObjectGenerator()

  def clone_object(self, obj, mapped_objects=None):
    """Perform clone operation on an object"""
    if not mapped_objects:
      mapped_objects = []
    return self.object_generator.generate_object(
        models.Audit,
        {
            "program": self.object_generator.create_stub(obj.program),
            "title": "Audit - copy 1",
            "operation": "clone",
            "status": "Planned",
            "cloneOptions": {
                "sourceObjectId": obj.id,
                "mappedObjects": mapped_objects
            }
        })

  def test_audit_clone(self):
    """Test that assessment templates get copied correctly"""
    audit = factories.AuditFactory()
    assessment_template_1 = factories.AssessmentTemplateFactory(
        title="test_audit_clone assessment_template_1")
    assessment_template_2 = factories.AssessmentTemplateFactory(
        title="test_audit_clone assessment_template_2")

    factories.RelationshipFactory(
        source=audit,
        destination=assessment_template_1)
    factories.RelationshipFactory(
        source=audit,
        destination=assessment_template_2)

    assessment_template_attributes_def = [
        {
            "definition_type": "assessment_template",
            "definition_id": assessment_template_1.id,
            "title": "test text field",
            "attribute_type": "Text",
            "multi_choice_options": ""
        },
        {
            "definition_type": "assessment_template",
            "definition_id": assessment_template_1.id,
            "title": "test RTF",
            "attribute_type": "Rich Text",
            "multi_choice_options": ""
        },
        {
            "definition_type": "assessment_template",
            "definition_id": assessment_template_1.id,
            "title": "test checkbox",
            "attribute_type": "Checkbox",
            "multi_choice_options": "test checkbox label"
        },
        {
            "definition_type": "assessment_template",
            "definition_id": assessment_template_1.id,
            "title": "test date field",
            "attribute_type": "Date",
            "multi_choice_options": ""
        },
        {
            "definition_type": "assessment_template",
            "definition_id": assessment_template_1.id,
            "title": "test dropdown field",
            "attribute_type": "Dropdown",
            "multi_choice_options": "ddv1,ddv2,ddv3"
        },
    ]

    assessment_template_attributes = []
    for attribute in assessment_template_attributes_def:
      attr = factories.CustomAttributeDefinitionFactory(**attribute)
      assessment_template_attributes += [attr]

    self.clone_object(audit, [u"AssessmentTemplate"])

    self.assertEqual(db.session.query(models.Audit).filter(
        models.Audit.title.like("%copy%")).count(), 1)

    audit_copy = db.session.query(models.Audit).filter(
        models.Audit.title.like("%copy%")).first()

    assessment_templates = audit_copy.related_objects({"AssessmentTemplate"})

    self.assertEqual(len(assessment_templates), 2)

    assessment_template_1 = db.session.query(models.AssessmentTemplate).filter(
        models.AssessmentTemplate.title ==
        "test_audit_clone assessment_template_1"
    ).first()

    self.assertEqual(
        db.session.query(models.CustomAttributeDefinition).filter(
            models.CustomAttributeDefinition.definition_type ==
            "assessment_template",
            models.CustomAttributeDefinition.definition_id ==
            assessment_template_1.id
        ).count(), len(assessment_template_attributes_def))

  # pylint: disable=unused-argument
  @patch('ggrc.integrations.issues.Client.update_issue')
  def test_audit_clone_with_issue_tracker(self, mock_update_issue):
    """Test that audit with issue tracker On gets copied without error"""
    from ggrc.models.hooks import issue_tracker
    iti = factories.IssueTrackerIssueFactory()
    asmt = iti.issue_tracked_obj
    asmt_id = asmt.id
    audit = asmt.audit
    audit_id = audit.id
    self.api.modify_object(audit, {
        "issue_tracker": {
            "enabled": True,
            "component_id": "11111",
            "hotlist_id": "222222",
        },
    })
    asmt = db.session.query(models.Assessment).get(asmt_id)
    with patch.object(issue_tracker, '_is_issue_tracker_enabled',
                      return_value=True):
      self.api.modify_object(asmt, {
          "issue_tracker": {
              "enabled": True,
              "component_id": "11111",
              "hotlist_id": "222222",
          },
      })

    audit = db.session.query(models.Audit).get(audit_id)
    self.clone_object(audit)

    self.assertEqual(db.session.query(models.Audit).filter(
        models.Audit.title.like("%copy%")).count(), 1)

  def test_audit_clone_invalid_values(self):
    """Test that audit gets copied successfully if invalid input"""
    audit = factories.AuditFactory()
    assessment_template_1 = factories.AssessmentTemplateFactory(
        title="test_audit_clone assessment_template_1")
    assessment_template_2 = factories.AssessmentTemplateFactory(
        title="test_audit_clone assessment_template_2")

    factories.RelationshipFactory(
        source=audit,
        destination=assessment_template_1)
    factories.RelationshipFactory(
        source=audit,
        destination=assessment_template_2)

    assessment_template_attributes_def = [
        {
            "definition_type": "assessment_template",
            "definition_id": assessment_template_1.id,
            "title": "test text field",
            "attribute_type": "Text",
            "multi_choice_options": ""
        },
        {
            "definition_type": "assessment_template",
            "definition_id": assessment_template_1.id,
            "title": "test RTF",
            "attribute_type": "Rich Text",
            "multi_choice_options": ""
        },
        {
            "definition_type": "assessment_template",
            "definition_id": assessment_template_1.id,
            "title": "test checkbox",
            "attribute_type": "Checkbox",
            "multi_choice_options": "test checkbox label"
        },
        {
            "definition_type": "assessment_template",
            "definition_id": assessment_template_1.id,
            "title": "test date field",
            "attribute_type": "Date",
            "multi_choice_options": ""
        },
        {
            "definition_type": "assessment_template",
            "definition_id": assessment_template_1.id,
            "title": "test dropdown field",
            "attribute_type": "Dropdown",
            "multi_choice_options": "ddv1,ddv2,ddv3"
        },
    ]

    assessment_template_attributes = []
    for attribute in assessment_template_attributes_def:
      attr = factories.CustomAttributeDefinitionFactory(**attribute)
      assessment_template_attributes += [attr]

    self.clone_object(audit, [u"blaaaaaa", 123])

    self.assertEqual(db.session.query(models.Audit).filter(
        models.Audit.title.like("%copy%")).count(), 1)

    audit_copy = db.session.query(models.Audit).filter(
        models.Audit.title.like("%copy%")).first()

    assessment_templates = audit_copy.related_objects({"AssessmentTemplate"})

    self.assertEqual(len(assessment_templates), 0)

  def test_audit_clone_template_not_selected(self):
    """Test that assessment templates don't get copied"""
    audit = factories.AuditFactory()
    assessment_template_1 = factories.AssessmentTemplateFactory(
        title="test_audit_clone assessment_template_1")
    assessment_template_2 = factories.AssessmentTemplateFactory(
        title="test_audit_clone assessment_template_2")

    factories.RelationshipFactory(
        source=audit,
        destination=assessment_template_1)
    factories.RelationshipFactory(
        source=audit,
        destination=assessment_template_2)

    assessment_template_attributes_def = [
        {
            "definition_type": "assessment_template",
            "definition_id": assessment_template_1.id,
            "title": "test text field",
            "attribute_type": "Text",
            "multi_choice_options": ""
        },
        {
            "definition_type": "assessment_template",
            "definition_id": assessment_template_1.id,
            "title": "test RTF",
            "attribute_type": "Rich Text",
            "multi_choice_options": ""
        },
        {
            "definition_type": "assessment_template",
            "definition_id": assessment_template_1.id,
            "title": "test checkbox",
            "attribute_type": "Checkbox",
            "multi_choice_options": "test checkbox label"
        },
        {
            "definition_type": "assessment_template",
            "definition_id": assessment_template_1.id,
            "title": "test date field",
            "attribute_type": "Date",
            "multi_choice_options": ""
        },
        {
            "definition_type": "assessment_template",
            "definition_id": assessment_template_1.id,
            "title": "test dropdown field",
            "attribute_type": "Dropdown",
            "multi_choice_options": "ddv1,ddv2,ddv3"
        },
    ]

    assessment_template_attributes = []
    for attribute in assessment_template_attributes_def:
      attr = factories.CustomAttributeDefinitionFactory(**attribute)
      assessment_template_attributes += [attr]

    self.clone_object(audit, [""])

    self.assertEqual(db.session.query(models.Audit).filter(
        models.Audit.title.like("%copy%")).count(), 1)

    audit_copy = db.session.query(models.Audit).filter(
        models.Audit.title.like("%copy%")).first()

    assessment_templates = audit_copy.related_objects({"AssessmentTemplate"})

    self.assertEqual(len(assessment_templates), 0)

  def test_audit_clone_auditors(self):
    """Test that auditors get cloned correctly"""
    auditor_role = AccessControlRole.query.filter_by(name="Auditors").first()

    audit = factories.AuditFactory()
    audit_context = factories.ContextFactory()
    audit.context = audit_context

    users = [
        "user1@example.com",
        "user2@example.com",
        "user3@example.com"
    ]

    auditors = []
    for user in users:
      person = factories.PersonFactory(email=user)
      auditors += [person]

    for auditor in auditors:
      factories.AccessControlListFactory(
          ac_role=auditor_role,
          object=audit,
          person=auditor
      )

    self.assertEqual(
        AccessControlList.query.filter_by(
            ac_role_id=auditor_role.id,
            object_type="Audit",
            object_id=audit.id).count(), 3, "Auditors not present")

    self.clone_object(audit)

    audit_copy = db.session.query(models.Audit).filter(
        models.Audit.title.like("%copy%")).first()

    self.assertEqual(
        AccessControlList.query.filter_by(
            ac_role_id=auditor_role.id,
            object_type="Audit",
            object_id=audit_copy.id
        ).count(), 3, "Auditors not present on copy")

    # Verify that contexts are different for original and copy audit
    another_user_4 = factories.PersonFactory(email="user4@example.com")

    factories.AccessControlListFactory(
        ac_role=auditor_role,
        object=audit,
        person=another_user_4
    )

    self.assertEqual(
        AccessControlList.query.filter_by(
            ac_role_id=auditor_role.id,
            object_type="Audit",
            object_id=audit.id).count(), 4, "Auditors not present")

    self.assertEqual(
        AccessControlList.query.filter_by(
            ac_role_id=auditor_role.id,
            object_type="Audit",
            object_id=audit_copy.id
        ).count(), 3, "Auditors not present on copy")

  def test_audit_clone_custom_attributes(self):
    """Test if custom attributes were copied correctly"""
    audit = factories.AuditFactory()
    ca_def_text = factories.CustomAttributeDefinitionFactory(
        title="test audit CA def 1",
        definition_type="audit",
        attribute_type="Text"
    )
    factories.CustomAttributeValueFactory(
        custom_attribute=ca_def_text,
        attributable=audit,
        attribute_value="CA 1 value"
    )

    self.clone_object(audit)

    audit_copy = db.session.query(models.Audit).filter(
        models.Audit.title.like("%copy%")).first()

    self.assertEqual(
        models.CustomAttributeValue.query.filter_by(
            attributable_type="Audit",
            attributable_id=audit_copy.id
        ).count(), 1, "Custom Attribute weren't copied.")

  def test_audit_snapshot_scope_cloning(self):
    """Test that exact same copy of original audit scope is created."""

    self._check_csv_response(self._import_file("snapshotter_create.csv"), {})

    program = db.session.query(models.Program).filter(
        models.Program.slug == "Prog-13211"
    ).one()

    self.create_audit(program)

    audit = db.session.query(models.Audit).filter(
        models.Audit.title == "Snapshotable audit").one()

    snapshots = db.session.query(models.Snapshot).filter(
        models.Snapshot.parent_type == "Audit",
        models.Snapshot.parent_id == audit.id,
    )

    self.assertEqual(snapshots.count(), len(Types.all) * 3)

    self._check_csv_response(self._import_file("snapshotter_update.csv"), {})

    # We create another copy of this object to test that it will not be
    # snapshotted
    new_control = self.create_object(models.Control, {
        "title": "Test New Control On Program"
    })
    self.objgen.generate_relationship(program, new_control)

    audit = db.session.query(models.Audit).filter(
        models.Audit.title == "Snapshotable audit").one()

    self.clone_object(audit)

    audit_copy = db.session.query(models.Audit).filter(
        models.Audit.title == "Snapshotable audit - copy 1").one()

    clones_snapshots = db.session.query(models.Snapshot).filter(
        models.Snapshot.parent_type == "Audit",
        models.Snapshot.parent_id == audit_copy.id,
    )

    self.assertEqual(clones_snapshots.count(), len(Types.all) * 3)

    original_revisions = {
        (snapshot.child_type, snapshot.child_id): snapshot.revision_id
        for snapshot in snapshots
    }

    clone_revisions = {
        (snapshot.child_type, snapshot.child_id): snapshot.revision_id
        for snapshot in clones_snapshots
    }

    for child, revision_id in original_revisions.items():
      self.assertEqual(revision_id, clone_revisions[child])

    self.assertEqual(
        db.session.query(models.Snapshot).filter(
            models.Snapshot.child_type == "Control",
            models.Snapshot.child_id == new_control.id
        ).count(),
        0, "No snapshots should exist for new control."
    )
