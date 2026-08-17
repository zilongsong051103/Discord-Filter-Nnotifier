import sys
import asyncio
from winrt.windows.ui.notifications import ToastNotificationManager, ToastNotification
from winrt.windows.data.xml.dom import XmlDocument

async def send_fake_discord_toast(sender_name, message_text):
    # Standard Windows XML layout blueprint for custom Toast notifications
    toast_xml_xml = f"""
    <toast>
        <visual>
            <binding template="ToastGeneric">
                <text>Discord Test Server (#general)</text>
                <text>{sender_name}: {message_text}</text>
            </binding>
        </visual>
    </toast>
    """
    
    # Load raw text layout configurations into XML structures
    xml_doc = XmlDocument()
    xml_doc.load_xml(toast_xml_xml)
    
    # Fetch a standard system notifier handle using an explicit Discord signature template
    notifier = ToastNotificationManager.create_toast_notifier("Discord")
    notification = ToastNotification(xml_doc)
    
    print(f"Injecting fake Windows notification payload -> [{sender_name}: {message_text}]")
    notifier.show(notification)

if __name__ == "__main__":
    print("--- WINDOWS DISCORD NOTIFICATION SIMULATOR ---")
    print("Sending fake notification test packet in 2 seconds...")
    print("Make sure your filter script is running in another window!\n")
    
    asyncio.run(asyncio.sleep(2.0))
    # This matches 'Alex', which is in our live watcher config parameters
    asyncio.run(send_fake_discord_toast("Jacob_Steevs", "Hey Alex, look at this update!"))
    print("Notification injected successfully.")
