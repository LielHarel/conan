# coding=utf-8

import os
import unittest

import pytest
from mock import patch

from conans.client.hook_manager import HookManager
from conans.model.recipe_ref import RecipeReference
from conans.paths import CONAN_MANIFEST
from conans.test.utils.tools import TurboTestClient


class PostPackageTestCase(unittest.TestCase):

    @pytest.mark.xfail(reason="cache2.0 revisit test")
    def test_create_command(self):
        """ Test that 'post_package' hook is called before computing the manifest
        """
        t = TurboTestClient()
        filename = "hook_file"

        def post_package_hook(conanfile, **kwargs):
            # There shouldn't be a manifest yet
            post_package_hook.manifest_path = os.path.join(conanfile.package_folder, CONAN_MANIFEST)
            self.assertFalse(os.path.exists(post_package_hook.manifest_path))
            # Add a file
            open(os.path.join(conanfile.package_folder, filename), "w").close()

        def mocked_load_hooks(hook_manager):
            hook_manager.hooks["post_package"] = [("_", post_package_hook)]

        with patch.object(HookManager, "load_hooks", new=mocked_load_hooks):
            pref = t.create(RecipeReference.loads("name/version@user/channel"))

        # Check that we are considering the same file
        pkg_layout = t.get_latest_pkg_layout(pref)
        self.assertEqual(post_package_hook.manifest_path,
                         os.path.join(pkg_layout.package(), CONAN_MANIFEST))
        # Now the file exists and contains info about created file
        self.assertTrue(os.path.exists(post_package_hook.manifest_path))
        with open(post_package_hook.manifest_path) as f:
            content = f.read()
            self.assertIn(filename, content)

    @pytest.mark.xfail(reason="cache2.0 revisit test")
    def test_export_pkg_command(self):
        """ Test that 'post_package' hook is called before computing the manifest
        """
        t = TurboTestClient()
        filename = "hook_file"

        def post_package_hook(conanfile, **kwargs):
            # There shouldn't be a manifest yet
            post_package_hook.manifest_path = os.path.join(conanfile.package_folder, CONAN_MANIFEST)
            self.assertFalse(os.path.exists(post_package_hook.manifest_path))
            # Add a file
            open(os.path.join(conanfile.package_folder, filename), "w").close()

        def mocked_load_hooks(hook_manager):
            hook_manager.hooks["post_package"] = [("_", post_package_hook)]

        with patch.object(HookManager, "load_hooks", new=mocked_load_hooks):
            pref = t.export_pkg(ref=RecipeReference.loads("name/version@user/channel"),
                                args="--package-folder=.")

        # Check that we are considering the same file
        pkg_layout = t.get_latest_pkg_layout(pref)
        self.assertEqual(post_package_hook.manifest_path,
                         os.path.join(pkg_layout.package(), CONAN_MANIFEST))
        # Now the file exists and contains info about created file
        self.assertTrue(os.path.exists(post_package_hook.manifest_path))
        with open(post_package_hook.manifest_path) as f:
            content = f.read()
            self.assertIn(filename, content)
