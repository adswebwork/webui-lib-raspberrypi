"""AWS IoT Core: connect, publish readings, subscribe to them.

Replaces the twenty-line AWSIoTMQTTClient setup block that used to be copied
verbatim into seven files, and the hand-built `'{"' + key + '": "' + value`
payload construction that went with it.
"""
import json

from pihome import credentials, identity, log, topics
from pihome.reading import Event, from_json

_logger = log.get_logger("iot")


def connect(device=None, label="pihome"):
    """Connect to AWS IoT Core as `device` (default: this machine).

    Returns a connected AWSIoTMQTTClient.
    """
    from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

    device = device or identity.device_id()
    ca, private_key, certificate = credentials.certs_for(device)

    client = AWSIoTMQTTClient("{}-{}-{}".format(device, label, identity.boot_id()))
    client.configureEndpoint(credentials.endpoint(), credentials.port())
    client.configureCredentials(ca, private_key, certificate)
    client.configureOfflinePublishQueueing(-1)   # queue indefinitely when offline
    client.configureDrainingFrequency(2)         # 2 Hz
    client.configureConnectDisconnectTimeout(10)
    client.configureMQTTOperationTimeout(5)

    _logger.info("connecting to %s as %s", credentials.endpoint(), device)
    client.connect()
    _logger.info("connected")
    return client


def publish(client, item, qos=1):
    """Publish a Reading or an Event on its own topic."""
    topic = item.topic()
    client.publish(topic=topic, QoS=qos, payload=item.to_json())
    _logger.info("-> %s %s", topic,
                 getattr(item, "value", getattr(item, "message", "")))


def publish_event(client, kind, message="", level="info", **tags):
    """Shorthand for publishing an Event."""
    publish(client, Event(kind=kind, level=level, message=message, tags=tags))


def _subscribe(client, topic, callback, qos):
    """Subscribe, parsing each payload before it reaches `callback`.

    Payloads that will not parse are logged and dropped - one malformed
    message from one node must not take down a subscriber.
    """
    def _handler(_client, _userdata, message):
        try:
            item = from_json(message.payload)
        except ValueError as exc:
            _logger.warning("dropping unparseable payload on %s: %s",
                            message.topic, exc)
            return
        callback(item)

    client.subscribe(topic, qos, _handler)
    _logger.info("subscribed to %s", topic)
    return topic


def subscribe_readings(client, callback, device="+", metric="#", qos=1):
    """Call `callback(reading)` for each Reading on the matching topic."""
    return _subscribe(client, topics.telemetry(device, metric), callback, qos)


def subscribe_events(client, callback, device="+", qos=1):
    """Call `callback(event)` for each Event from the matching devices."""
    return _subscribe(client, topics.events(device), callback, qos)


class MockClient:
    """Stand-in for AWSIoTMQTTClient. Records what was published.

    Lets tests and desktop runs exercise the whole publish path with no AWS
    account, no certificate and no Pi.
    """

    def __init__(self):
        self.published = []
        self.subscriptions = []
        self.connected = False

    def configureEndpoint(self, *a):                pass
    def configureCredentials(self, *a):             pass
    def configureOfflinePublishQueueing(self, *a):  pass
    def configureDrainingFrequency(self, *a):       pass
    def configureConnectDisconnectTimeout(self, *a): pass
    def configureMQTTOperationTimeout(self, *a):    pass

    def connect(self):
        self.connected = True
        return True

    def disconnect(self):
        self.connected = False
        return True

    def publish(self, topic, QoS, payload):
        json.loads(payload)          # fail loudly on a malformed payload
        self.published.append((topic, payload))
        return True

    def subscribe(self, topic, qos, callback):
        self.subscriptions.append((topic, callback))
        return True

    def deliver(self, topic, payload):
        """Simulate an inbound message to any matching subscription."""
        class _Message:
            pass
        for pattern, callback in self.subscriptions:
            if _topic_matches(pattern, topic):
                message = _Message()
                message.topic = topic
                message.payload = payload
                callback(self, None, message)


def _topic_matches(pattern, topic):
    """MQTT wildcard match: + is one level, # is the rest."""
    p, t = pattern.split("/"), topic.split("/")
    for index, part in enumerate(p):
        if part == "#":
            return True
        if index >= len(t):
            return False
        if part != "+" and part != t[index]:
            return False
    return len(p) == len(t)
