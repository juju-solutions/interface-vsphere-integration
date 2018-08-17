"""
This is the provides side of the interface layer, for use only by the
vSphere integration charm itself.

The flags that are set by the provides side of this interface are:

* **`endpoint.{endpoint_name}.requested`** This flag is set when there is
  a new or updated request by a remote unit for vSphere integration
  features.  The vSphere integration charm should then iterate over each
  request, perform whatever actions are necessary to satisfy those requests,
  and then mark them as complete.
"""

from operator import attrgetter

from charms.reactive import Endpoint
from charms.reactive import when
from charms.reactive import toggle_flag, clear_flag


class VsphereIntegrationProvides(Endpoint):
    """
    Example usage:

    ```python
    from charms.reactive import when, endpoint_from_flag
    from charms import layer

    @when('endpoint.vsphere.requests-pending')
    def handle_requests():
        vsphere = endpoint_from_flag('endpoint.vsphere.requests-pending')
        for request in vsphere.requests:
            request.set_credentials(layer.vsphere.get_user_credentials())
        vsphere.mark_completed()
    ```
    """

    @when('endpoint.{endpoint_name}.changed')
    def check_requests(self):
        toggle_flag(self.expand_name('requests-pending'),
                    len(self.requests) > 0)
        clear_flag(self.expand_name('changed'))

    @property
    def requests(self):
        """
        A list of the new or updated #IntegrationRequests that
        have been made.
        """
        if not hasattr(self, '_requests'):
            all_requests = [IntegrationRequest(unit)
                            for unit in self.all_joined_units]
            is_changed = attrgetter('is_changed')
            self._requests = list(filter(is_changed, all_requests))
        return self._requests

    def mark_completed(self):
        """
        Mark all requests as completed and remove the `requests-pending` flag.
        """
        clear_flag(self.expand_name('requests-pending'))
        self._requests = []


class IntegrationRequest:
    """
    A request for integration from a single remote unit.
    """
    def __init__(self, unit):
        self._unit = unit

    @property
    def _to_publish(self):
        return self._unit.relation.to_publish

    @property
    def is_changed(self):
        """
        Whether this request has changed since the last time it was
        marked completed (if ever).
        """
        return not self.has_credentials

    @property
    def unit_name(self):
        return self._unit.unit_name

    def set_credentials(self,
                        vsphere_ip,
                        user,
                        password,
                        datacenter,
                        datastore):
        """
        Set the credentials for this request.
        """
        self._unit.relation.to_publish.update({
            'vsphere_ip': vsphere_ip,
            'user': user,
            'password': password,
            'datacenter': datacenter,
            'datastore': datastore,
        })

    @property
    def has_credentials(self):
        """
        Whether or not credentials have been set via `set_credentials`.
        """
        return 'credentials' in self._unit.relation.to_publish
