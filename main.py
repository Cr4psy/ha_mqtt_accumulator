import argparse
import json
import paho.mqtt.client as mqtt
import logging.config
import yaml
from confp import render  # type: ignore
from typing import Any, Optional


_LOG = logging.getLogger("my_addon.main")

class UtilityMeter:
    def __init__(self, name, base, topic, client, scale) -> None:
        self.name = name
        self.topic = topic
        self.base = base
        self.client = client
        self.first_msg = True
        self.scale = scale
        self.value = 0

        if self.scale == 0:
            self.scale = 1
    
    def topic_backup(self):
        return self.base + "/accumulator/" + self.name
    
    def add(self):
        self.value += self.scale
        self.client.publish(self.topic_backup(), self.value, 0, True)
    
    #  todo(acl): how to get stable unique id
    def advertise(self):
        data = dict(
            availability_topic=self.base+"/status",
            payload_available="running",
            payload_not_available="dead",
            state_topic=self.topic_backup(),
            unique_id="crapsy-68092106-9ad3-4023-87f5-b8dce1f61e2c-"+self.name,
            device_class="water",
            unit_of_measurement="L",
            object_id="crapsy-68092106-9ad3-4023-87f5-b8dce1f61e2c-"+self.name,
            device=dict(
                manufacturer="Crapsy",
                name="Crapsy",
                model="v1.0.0",
                identifiers=["crapsy", "crapsy-68092106-9ad3-4023-87f5-b8dce1f61e2c"],
            ),
        )   
        self.client.publish("homeassistant/sensor/crapsy-68092106-9ad3-4023-87f5-b8dce1f61e2c/"+self.name+"/config", json.dumps(data), 0, True)
    def init(self, value):
        if value > self.value:
            self.value = value

    def value(self):
        return self.value

def load_config(config: str, render_config: str) -> Any:
    """
    Loads the config, and uses confp to render it if necessary.
    """
    with open(config, "r", encoding="utf8") as stream:
        if render_config:
            rendered = render(render_config, stream.read())
            raw_config = yaml.safe_load(rendered)
        else:
            raw_config = yaml.safe_load(stream)
    return raw_config

def on_connect_fn(um):
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        for u in um:
            print("Subscribed to "+u.topic)
            client.subscribe(u.topic)
            client.subscribe(u.topic_backup())
    return on_connect



def on_message_fn(ums: list[UtilityMeter]):
    def on_message(client, userdata, msg):
        payload = msg.payload.decode("utf-8") 
        print("Received on topic: "+msg.topic+" message: "+ payload)
        for u in ums:
            if u.topic == msg.topic:
                if u.first_msg:
                    u.first_msg = False
                    continue
                if payload != "ON":
                    return
                u.add()
            elif u.topic_backup() == msg.topic:
               u.init(int(payload)) 
            else:
                continue
    return on_message


def main() -> None:
    """
    Main entrypoint function.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument(
        "--render",
        help="""
    A config file for confp for preprocessing the config file.
    Doesn't need to contain a template section.
    """,
    )
    args = parser.parse_args()

    print("started python code")

     # Load, validate and normalise config, or quit.
    try:
        config = load_config(args.config, args.render)
    except:
        print("failed to read config")

    try:
        host=config["mqtt"]["host"]
        user=config["mqtt"]["user"]
        password=config["mqtt"]["password"]
        base=config["mqtt"]["topic_prefix"]
    except:
        print("failed to get mqtt parameters")
        exit()

    utilities = ""
    try:
        utilities = config["utility_meters"]
    except:
        print("failed to get utility meter config")
        exit()

    client = mqtt.Client()

    ums = []
    for u in utilities:
        ums.append(UtilityMeter(u["name"], base, u["topic"], client, u["scale"]))

   
    client.on_connect = on_connect_fn(ums)
    client.on_message = on_message_fn(ums)
    client.username_pw_set(user, password)
    client.connect(host, 1883, 60)
    
    for u in ums:
        u.advertise()

    client.loop_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("")