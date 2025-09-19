from rest_framework import routers

from api.api_v0.semd_templates.views.document_template_view import DocumentTemplateViewSet
from api.api_v0.semd_templates.views.field_definition_view import FieldDefinitionViewSet

router = routers.DefaultRouter()
router.register(r'field-definitions', FieldDefinitionViewSet, basename='field-definitions')
router.register(r'semd-document-templates', DocumentTemplateViewSet, basename='semd-document-templates')

urlpatterns = [] + router.urls