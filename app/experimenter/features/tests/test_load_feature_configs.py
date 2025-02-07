import json

from django.core.management import call_command
from django.test import TestCase

from experimenter.experiments.models import NimbusExperiment, NimbusFeatureConfig
from experimenter.experiments.tests.factories import NimbusFeatureConfigFactory
from experimenter.features import Features
from experimenter.features.tests import mock_valid_features


@mock_valid_features
class TestLoadFeatureConfigs(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Features.clear_cache()

    def test_loads_new_feature_configs(self):
        self.assertFalse(NimbusFeatureConfig.objects.filter(slug="someFeature").exists())
        call_command("load_feature_configs")

        feature_config = NimbusFeatureConfig.objects.get(slug="someFeature")
        self.assertEqual(feature_config.name, "someFeature")
        self.assertEqual(
            feature_config.description,
            "Some Firefox Feature",
        )
        self.assertEqual(
            json.loads(feature_config.schema),
            {
                "type": "object",
                "properties": {
                    "stringEnumProperty": {
                        "description": "String Property",
                        "type": "string",
                        "enum": ["v1", "v2"],
                    },
                    "boolProperty": {
                        "description": "Boolean Property",
                        "type": "boolean",
                    },
                    "intProperty": {"description": "Integer Property", "type": "integer"},
                    "jsonProperty": {"description": "Arbitrary JSON Property"},
                },
                "additionalProperties": False,
            },
        )

    def test_updates_existing_feature_configs(self):
        NimbusFeatureConfigFactory.create(
            name="someFeature",
            slug="someFeature",
            application=NimbusExperiment.Application.DESKTOP,
            schema="{}",
        )
        call_command("load_feature_configs")

        feature_config = NimbusFeatureConfig.objects.get(slug="someFeature")
        self.assertEqual(feature_config.name, "someFeature")
        self.assertEqual(
            feature_config.description,
            "Some Firefox Feature",
        )
        self.assertEqual(
            json.loads(feature_config.schema),
            {
                "type": "object",
                "properties": {
                    "stringEnumProperty": {
                        "description": "String Property",
                        "type": "string",
                        "enum": ["v1", "v2"],
                    },
                    "boolProperty": {
                        "description": "Boolean Property",
                        "type": "boolean",
                    },
                    "intProperty": {"description": "Integer Property", "type": "integer"},
                    "jsonProperty": {"description": "Arbitrary JSON Property"},
                },
                "additionalProperties": False,
            },
        )

    def test_handles_existing_features_with_same_slug_different_name(self):
        NimbusFeatureConfigFactory.create(
            name="Some Firefox Feature different name",
            slug="someFeature",
            application=NimbusExperiment.Application.DESKTOP,
            schema="{}",
        )
        call_command("load_feature_configs")

        feature_config = NimbusFeatureConfig.objects.get(slug="someFeature")
        self.assertEqual(feature_config.name, "someFeature")
        self.assertEqual(
            feature_config.description,
            "Some Firefox Feature",
        )
