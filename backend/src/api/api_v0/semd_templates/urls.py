from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from api.api_v0.semd_templates.views.document_template_view import DocumentTemplateViewSet
from api.api_v0.semd_templates.views.field_definition_view import FieldDefinitionViewSet
from api.api_v0.semd_templates.views.document_instance import (
    DocumentInstanceViewSet,
    DocumentFieldValueViewSet,
)
from api.api_v0.semd_templates.views.validate_document import DocumentValidatorViewSet

router = DefaultRouter()
router.register(r"field-definitions",        FieldDefinitionViewSet, basename="field-definition")
router.register(r"semd-document-templates", DocumentTemplateViewSet, basename="semd-document-template")
router.register(r"semd-documents",          DocumentInstanceViewSet, basename="semd-document")
router.register(r"validate-document", DocumentValidatorViewSet, basename="semd-document-validator")

# nested: /semd-documents/{id}/fields/…
nested = NestedDefaultRouter(router, r"semd-documents", lookup="document")
nested.register(r"fields", DocumentFieldValueViewSet, basename="semd-document-field")

urlpatterns = router.urls + nested.urls
