"""
This is the requires side of the interface layer, for use in charms that wish
to request integration with vSphere native features.  The integration will be
provided by the vSphere integration charm, which allows the requiring charm
to not require cloud credentials itself and not have a lot of vSphere
specific API code.

The flags that are set by the requires side of this interface are:

* **`endpoint.{endpoint_name}.joined`** This flag is set when the relation
  has been joined, and the charm should then use the methods documented below
  to request specific vSphere features.  This flag is automatically removed
  if the relation is broken.  It should not be removed by the charm.

* **`endpoint.{endpoint_name}.ready`** This flag is set once the requested
  features have been enabled for the vSphere instance on which the charm is
  running.  This flag is automatically removed if new integration features are
  requested.  It should not be removed by the charm.
"""


from charms.reactive import Endpoint
from charms.reactive import when, when_not
from charms.reactive import clear_flag, toggle_flag


class VsphereIntegrationRequires(Endpoint):
    """
    Interface to request integration access.

    Note that due to resource limits and permissions granularity, policies are
    limited to being applied at the charm level.  That means that, if any
    permissions are requested (i.e., any of the enable methods are called),
    what is granted will be the sum of those ever requested by any instance of
    the charm on this cloud.

    Labels, on the other hand, will be instance specific.

    Example usage:

    ```python
    from charms.reactive import when, endpoint_from_flag

    @when('endpoint.vsphere.ready')
    def vsphere_integration_ready():
        vsphere = endpoint_from_flag('endpoint.vsphere.joined')
        update_config_enable_vsphere(vsphere.vsphere_ip,
                                     vsphere.user,
                                     vsphere.password,
                                     vsphere.datacenter,
                                     vsphere.datastore)
    ```
    """

    @property
    def _received(self):
        """
        Helper to streamline access to received data since we expect to only
        ever be connected to a single vSphere integration application with a
        single unit.
        """
        return self.relations[0].joined_units.received

    @property
    def _to_publish(self):
        """
        Helper to streamline access to received data since we expect to only
        ever be connected to a single vSphere integration application with a
        single unit.
        """
        return self.relations[0].to_publish

    @when('endpoint.{endpoint_name}.changed')
    def check_ready(self):
        toggle_flag(self.expand_name('ready'), self.is_ready)
        clear_flag(self.expand_name('changed'))

    @when_not('endpoint.{endpoint_name}.joined')
    def remove_ready(self):
        clear_flag(self.expand_name('ready'))

    @property
    def is_ready(self):
        """
        Whether or not the request for this instance has been completed.
        """
        return all(field is not None for field in [
            self.vsphere_ip,
            self.user,
            self.password,
            self.datacenter,
            self.datastore,
        ])

    @property
    def vsphere_ip(self):
        return self._received['vsphere_ip']

    @property
    def user(self):
        return self._received['user']

    @property
    def password(self):
        return self._received['password']

    @property
    def datacenter(self):
        return self._received['datacenter']

    @property
    def datastore(self):
        return self._received['datastore']
