# tlwbe_heartbeat

This is a small python app that uses a rak811
module to send LoRaWAN packets into a network
and validates that the correct uplink is generated
by the backend.

This is mostly intended to help detect situations
where the concentrator board has locked up and
the LoRaWAN network is down.

In the future there might be support for automatically
resetting the concentrator/gateway when a fault is
detected.