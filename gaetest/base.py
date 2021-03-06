import unittest
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub

class AppEngineTestCase(unittest.TestCase):

  def setUp(self):
    # Preserve the current apiproxy for tearDown().
    self.original_apiproxy = apiproxy_stub_map.apiproxy

    # Create a new apiproxy and temporary datastore that will be used for this test.
    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
    temp_stub = datastore_file_stub.DatastoreFileStub('AppEngineTestCaseDataStore', None, None)
    apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', temp_stub)

    # For convenience, the subclass can implement 'set_up' rather than overriding setUp()
    # and calling this base method.
    if hasattr(self, 'set_up'):
      self.set_up()

  def tearDown(self):
    # The subclass can optionally choose to implement 'tear_down'.
    if hasattr(self, 'tear_down'):
      self.tear_down()

    # Restore stubs for development.
    # apiproxy_stub_map.apiproxy = self.original_apiproxy