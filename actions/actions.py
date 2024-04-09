# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
####################################################################################

# actions.py

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.events import SlotSet

# Map the detected day ask_day_entities to their corresponding names
day_name_mapping = {
    "จัน": "monday",
    "อังคาร": "tuesday",
    "อังคาน": "tuesday",
    "พุด": "wednesday",
    "พุท": "wednesday",
    "พุธ": "wednesday",
    "พฤหัส": "thursday",
    "ศุก": "friday",
    "สุก": "friday",
    "สุข": "friday",
    "เสา": "saturday",
    "อาทิต": "sunday",
    "อาทิด": "sunday",
 # Add mappings for other days as needed
}

open_mappings = {
    "เปิด": "open"
}

close_mappings = {
    "ปิด": "close"
}
class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Check if the latest message exists and if it has text
        latest_message = tracker.latest_message
        if latest_message and latest_message.get("text"):
            user_input = latest_message["text"].strip()
            if not user_input:
                # If the user input is blank, send an appropriate message
                dispatcher.utter_message(response="utter_blank")
            else:
                # If the user input is not blank, send a generic fallback message
                dispatcher.utter_message(response="utter_fallback")
        else:
            # If there's no text in the latest message, send a generic fallback message
            dispatcher.utter_message(response="utter_fallback")

        # Revert user message which led to fallback.
        return [UserUtteranceReverted()]


class ActionHandleDayOpen(Action):
    def name(self) -> Text:
        return "action_handle_date"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # Extract ask_day_entities related to the ask_day_open slot from the user's message
        ask_day_entities = tracker.latest_message.get("entities", [])
        extract_entities = [entity["value"] for entity in ask_day_entities if entity["entity"]]
        print("Detected day ask_day_entities:", extract_entities)

        # Create a set of keys from day_name_mapping for faster lookup
        day_name_mapping_keys = set(day_name_mapping.keys())
        open_mappings_keys = set(open_mappings.keys())
        close_mappings_keys = set(close_mappings.keys())

        # Get the detected day entity
        detected_day_entity = None
        for day_entity in extract_entities:
            if day_entity in day_name_mapping_keys:
                detected_day_entity = day_name_mapping[day_entity]
                break
        
        # Get the detected open entity
        detected_open_entity = None
        for open_entity in extract_entities:
            if open_entity in open_mappings_keys:
                detected_open_entity = open_mappings[open_entity]
                break
            
        # Get the detected open entity
        detected_close_entity = None
        for close_entity in extract_entities:
            if close_entity in close_mappings_keys:
                detected_close_entity = close_mappings[close_entity]
                break
            
        print("Detected entity:", detected_day_entity , detected_open_entity, detected_close_entity)

        # Perform actions based on the detected day entity
        if detected_day_entity == "sunday":
            dispatcher.utter_message(response=f"utter_{detected_day_entity}")
        elif detected_day_entity and detected_open_entity:
            dispatcher.utter_message(response=f"utter_open_{detected_day_entity}")
        elif (detected_day_entity != "sunday") and detected_close_entity:
            dispatcher.utter_message(response=f"utter_open_{detected_day_entity}")
        else:
            dispatcher.utter_message("ขอโทษครับ ไม่มีข้อมูลสำหรับวันนั้น")

        # Reset the ask_day_open slot value
        return [SlotSet("ask_day_open", None),SlotSet("ask_day_close", None)]


class ActionHandleTimeOpen(Action):
    def name(self) -> Text:
        return "action_handle_time"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Access the value of the detected entity
        detected_entity_value = tracker.get_slot("ask_time_open")
        print(detected_entity_value)
        # Map the detected entity value to its corresponding name
        entity_name_mapping = {
            "จัน": "monday",
            "อังคาร": "tuesday",
            "อังคาน": "tuesday",
            "พุด": "wednesday",
            "พุท": "wednesday",
            "พุธ": "wednesday",
            "พฤหัส": "thursday",
            "ศุก": "friday",
            "สุก": "friday",
            "สุข": "friday",
            "เสา": "saturday",
            "อาทิต": "sunday",
            "อาทิด": "sunday"
        }
    
        # Get the entity name from the mapping
        detected_entity_name = entity_name_mapping.get(detected_entity_value)
        print(detected_entity_name)
        # Perform actions based on the detected entity name
        if detected_entity_name in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]:
            dispatcher.utter_message(response=f"utter_time_{detected_entity_name}")
        elif detected_entity_name == "sunday":
            dispatcher.utter_message(response=f"utter_{detected_entity_name}")
        else:
            dispatcher.utter_message("ขอโทษครับ ไม่มีข้อมูลสำหรับวันนั้น")

        return []
    