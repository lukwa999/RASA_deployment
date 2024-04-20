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
from datetime import datetime, timedelta
import pytz

# Map the detected day ask_day_entities to their corresponding names
day_name_mapping = {
    "monday": "Monday",
    "tuesday": "Tuesday",
    "wednesday": "Wednesday",
    "thursday": "Thursday",
    "friday": "Friday",
    "saturday": "Saturday",
    "sunday": "Sunday",
}

open_mappings = {"open": "open"}

close_mappings = {"close": "close"}

today_mappings = {"today": "today"}

now_mappings = {"now": "now"}

thai_day_names = {
    "Monday": "วันจันทร์",
    "Tuesday": "วันอังคาร",
    "Wednesday": "วันพุธ",
    "Thursday": "วันพฤหัสบดี",
    "Friday": "วันศุกร์",
    "Saturday": "วันเสาร์",
    "Sunday": "วันอาทิตย์",
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
        return "action_handle_time_open_close"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # Get the message from the ask_day_open slot
        ask_day_message = tracker.get_slot("ask_time_open_close")

        utc_plus_7 = pytz.timezone("Asia/Bangkok")

        # Get the current time in the UTC +7 timezone
        current_time = datetime.now(utc_plus_7)

        # Get the day of the week and translate it to Thai
        current_day = current_time.strftime("%A")
        current_day_thai = thai_day_names.get(current_day)

        # Get the current hour
        current_hour = current_time.hour

        if ask_day_message:
            # Extract ask_day_entities related to the ask_day_open slot from the user's message
            ask_day_entities = tracker.latest_message.get("entities", [])
            extract_entities = [
                entity["entity"] for entity in ask_day_entities if entity.get("entity")
            ]
            print("Detected time entities :", extract_entities)

            # Separate detected entities into different lists
            detected_day_entities = []
            detected_open_entities = []
            detected_close_entities = []
            detected_today_entities = []
            detected_now_entities = []
            for entity in extract_entities:
                if entity in day_name_mapping:
                    detected_day_entities.append(day_name_mapping[entity])
                elif entity in open_mappings:
                    detected_open_entities.append(entity)
                elif entity in close_mappings:
                    detected_close_entities.append(entity)
                elif entity in today_mappings:
                    detected_today_entities.append(entity)
                elif entity in now_mappings:
                    detected_now_entities.append(entity)

            print(
                "Detected time entities date:",
                detected_day_entities,
                "Detected time entities open:",
                detected_open_entities,
                "Detected time entities close:",
                detected_close_entities,
                "Detected time entities today:",
                detected_today_entities,
                "Detected time entities now:",
                detected_now_entities,
            )
            
            # Handle detected entities based on mappings
            if detected_now_entities and detected_open_entities:
                # Check if today is not Sunday
                if current_day != "Sunday":
                    # Check if it's within opening hours
                    if current_day != "Saturday":
                        if current_hour > 8 and current_hour < 20:
                            response = f"ตอนนี้เวลา {current_time.strftime('%H:%M')} ห้องสมุดเปิดทำการแล้วครับ"
                        else:
                            response = f"ตอนนี้เวลา {current_time.strftime('%H:%M')} ห้องสมุดปิดทำการแล้วครับ โปรดมาใช้บริการใหม่โอกาศหน้า"
                    else:  # It's Saturday
                        if current_hour > 9 and current_hour < 18:
                            response = f"ตอนนี้เวลา {current_time.strftime('%H:%M')} ห้องสมุดเปิดทำการแล้วครับ"
                        else:
                            response = f"ตอนนี้เวลา {current_time.strftime('%H:%M')} ห้องสมุดปิดทำการแล้วครับ โปรดมาใช้บริการใหม่โอกาศหน้า"
                else:
                    response = "วันนี้ วันอาทิตย์ ห้องสมุดปิดทำการครับ"
            elif detected_now_entities and detected_close_entities:
                # Check if today is not Sunday
                if current_day != "Sunday":
                    # Check if it's within opening hours
                    if current_day != "Saturday":
                        if current_hour > 8 and current_hour < 20:
                            
                            # Calculate remaining time until 8:00 PM
                            closing_time = datetime(current_time.year, current_time.month, current_time.day, 20, 0, tzinfo=utc_plus_7)  # Set closing time to 8:00 PM
                            remaining_time = closing_time - current_time

                            # Convert remaining time to hours and minutes
                            remaining_hours = remaining_time.seconds // 3600
                            remaining_minutes = (remaining_time.seconds % 3600) // 60

                            # Construct the response message
                            response = f"ตอนนี้เวลา {current_time.strftime('%H:%M')} ห้องสมุดเปิดทำการแล้วครับ และเหลือเวลา {remaining_hours} ชั่วโมง {remaining_minutes} นาที ก่อนจะปิด"
                        else:
                            response = f"ตอนนี้เวลา {current_time.strftime('%H:%M')} ห้องสมุดปิดทำการแล้วครับ โปรดมาใช้บริการใหม่โอกาศหน้า"
                    else:  # It's Saturday
                        if current_hour > 9 and current_hour < 18:
                            
                            # Calculate remaining time until 6:00 PM
                            closing_time = datetime(current_time.year, current_time.month, current_time.day, 18, 0, tzinfo=utc_plus_7)  # Set closing time to 6:00 PM
                            remaining_time = closing_time - current_time

                            # Convert remaining time to hours and minutes
                            remaining_hours = remaining_time.seconds // 3600
                            remaining_minutes = (remaining_time.seconds % 3600) // 60

                            # Construct the response message
                            response = f"ตอนนี้เวลา {current_time.strftime('%H:%M')} ห้องสมุดเปิดทำการแล้วครับ และเหลือเวลา {remaining_hours} ชั่วโมง {remaining_minutes} นาที ก่อนจะปิด"
                        else:
                            response = f"ตอนนี้เวลา {current_time.strftime('%H:%M')} ห้องสมุดปิดทำการแล้วครับ โปรดมาใช้บริการใหม่โอกาศหน้า"
                else:
                    response = "วันนี้ วันอาทิตย์ ห้องสมุดปิดทำการครับ"
            elif detected_day_entities and (detected_open_entities or detected_close_entities):
                day_thai = thai_day_names.get(detected_day_entities[0])
                if "Sunday" not in detected_day_entities:
                    if "Saturday" not in detected_day_entities:
                        response = f"วัน {day_thai} ห้องสมุดเปิดทำการเวลา 8:00 น ครับ และ ปิดเทำการวลา 20:00 น ครับ"
                    else : #Saturday
                        response = f"วัน {day_thai} ห้องสมุดเปิดทำการเวลา 9:00 น ครับ และ ปิดเทำการวลา 18:00 น ครับ"
                else:
                    response = "วันอาทิตย์ ห้องสมุดปิดทำการครับ"
            elif detected_today_entities and (detected_open_entities or detected_close_entities):
                # Check if today is not Sunday
                if current_day != "Sunday":
                    # Check if it's within opening hours
                    if current_day != "Saturday":
                        response = f"วันนี้ {current_day_thai} ห้องสมุดเปิดทำการเวลา 8:00 น ครับ และ ปิดเทำการวลา 20:00 น ครับ"
                    else:  # It's Saturday
                        response = f"วันนี้ {current_day_thai} ห้องสมุดเปิดทำการเวลา 9:00 น ครับ และ ปิดเทำการวลา 18:00 น ครับ"
                else:
                    response = "วันนี้ วันอาทิตย์ ห้องสมุดปิดทำการครับ"
            elif detected_open_entities or detected_close_entities:
                # Check if today is not Sunday
                if current_day != "Sunday":
                    # Check if it's within opening hours
                    if current_day != "Saturday":
                        response = f"วันนี้ {current_day_thai} ห้องสมุดเปิดทำการเวลา 8:00 น ครับ และ ปิดเทำการวลา 20:00 น ครับ"
                    else:  # It's Saturday
                        response = f"วันนี้ {current_day_thai} ห้องสมุดเปิดทำการเวลา 9:00 น ครับ และ ปิดเทำการวลา 18:00 น ครับ"
                else:
                    response = "วันนี้ วันอาทิตย์ ห้องสมุดปิดทำการครับ"
            # Utter the response message
        dispatcher.utter_message(response)

        # Reset the ask_day_open slot value
        return [SlotSet("ask_time_open_close", None)]



class ActionHandleLibraryStatus(Action):
    def name(self) -> Text:
        return "action_handle_library_open_close"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Define the UTC +7 timezone
        utc_plus_7 = pytz.timezone("Asia/Bangkok")

        # Get the current time in the UTC +7 timezone
        current_time = datetime.now(utc_plus_7)

        # Get the day of the week and translate it to Thai
        current_day = current_time.strftime("%A")
        current_day_thai = thai_day_names.get(current_day)

        # Get the message from the ask_day_open_close slot
        ask_day_message = tracker.get_slot("ask_day_open_close")

        if ask_day_message:
            # Extract ask_day_entities related to the ask_day_open slot from the user's message
            ask_day_entities = tracker.latest_message.get("entities", [])
            extract_entities = [
                entity["entity"] for entity in ask_day_entities if entity.get("entity")
            ]
            print("Detected day entities open:", extract_entities)

            # Separate detected entities into different lists
            detected_day_entities = []
            detected_open_entities = []
            detected_close_entities = []
            detected_today_entities = []
            for entity in extract_entities:
                if entity in day_name_mapping:
                    detected_day_entities.append(day_name_mapping[entity])
                elif entity in open_mappings:
                    detected_open_entities.append(entity)
                elif entity in close_mappings:
                    detected_close_entities.append(entity)
                elif entity in today_mappings:
                    detected_today_entities.append(entity)

            print(
                "Detected day entities date:",
                detected_day_entities,
                "Detected day entities open:",
                detected_open_entities,
                "Detected day entities close:",
                detected_close_entities,
                "Detected today entities",
                detected_today_entities,
            )

            # Debugging: Print the value of current_day_thai
            print("Current day in Thai:", current_day_thai)

            if detected_day_entities and detected_open_entities:
                thai_date = thai_day_names.get(detected_day_entities[0])
                if "Sunday" not in detected_day_entities:
                    response = f"{thai_date} ห้องสมุดเปิดให้บริการครับ"
                else:
                    response = f"{thai_date} ห้องสมุดปิดให้บริการครับ"
            elif detected_day_entities and detected_close_entities:
                thai_date = thai_day_names.get(detected_day_entities[0])
                if "Sunday" not in detected_day_entities:
                    response = f"{thai_date} ห้องสมุดไม่ปิดให้บริการครับ"
                else:
                    response = f"{thai_date} ห้องสมุดปิดให้บริการครับ"
            elif detected_today_entities and detected_open_entities:
                if current_day == "Sunday":
                    response = f"วันนี้ {current_day_thai} ห้องสมุดปิดทำการครับ"
                else :
                    response = f"วันนี้ {current_day_thai} ห้องสมุดเปิดให้บริการครับ"
            elif detected_today_entities and detected_close_entities:
                if current_day == "Sunday":
                    response = f"วันนี้ {current_day_thai} ห้องสมุดปิดให้บริการครับ"
                else :
                    response = f"วันนี้ {current_day_thai} ห้องสมุดไม่ปิดให้บริการครับ"
            elif detected_open_entities :
                if current_day == "Sunday":
                    response = f"วันนี้ {current_day_thai} ห้องสมุดปิดทำการครับ"
                else :
                    response = f"วันนี้ {current_day_thai} ห้องสมุดเปิดให้บริการครับ"
            elif detected_close_entities :
                if current_day == "Sunday":
                    response = f"วันนี้ {current_day_thai} ห้องสมุดปิดทำการครับ"
                else :
                    response = f"วันนี้ {current_day_thai} ห้องสมุดไม่ปิดให้บริการครับ"

            dispatcher.utter_message(response)

        return [SlotSet("ask_day_open_close", None)]
