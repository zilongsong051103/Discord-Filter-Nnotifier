import time
import winreg

from winrt.windows.ui.notifications import ToastNotificationManager, ToastNotification
from winrt.windows.data.xml.dom import XmlDocument

# AppUserModelID we post the fake toast under. The live filter matches Discord
# notifications by this display name, so it must equal the name live_filter.py
# checks for ("Discord"). Real Discord uses a different AUMID
# (com.squirrel.Discord.Discord), so this does not collide with it.
APP_ID = "Discord"


def ensure_app_registered(app_id, display_name):
    """Register a lightweight AppUserModelID under HKCU so Windows will actually
    display toasts posted under it.

    Showing a toast with an unregistered AUMID raises 'Element not found', so
    without this the notification never appears. Writing DisplayName is enough
    (an icon is optional); this is per-user, needs no admin, and is reversible
    by deleting HKCU\\Software\\Classes\\AppUserModelId\\<app_id>.
    """
    key_path = rf"SOFTWARE\Classes\AppUserModelId\{app_id}"
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path) as key:
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, display_name)


def send_fake_discord_toast(sender_name, message_text):
    # Standard Windows XML layout for a "ToastGeneric" notification.
    toast_xml = f"""
    <toast>
        <visual>
            <binding template="ToastGeneric">
                <text>Discord Test Server (#general)</text>
                <text>{sender_name}: {message_text}</text>
            </binding>
        </visual>
    </toast>
    """

    xml_doc = XmlDocument()
    xml_doc.load_xml(toast_xml)

    # NOTE: winrt splits WinRT's two CreateToastNotifier overloads into two names.
    # The one that takes an AppUserModelID is create_toast_notifier_with_id();
    # the bare create_toast_notifier() takes no arguments.
    notifier = ToastNotificationManager.create_toast_notifier_with_id(APP_ID)
    notification = ToastNotification(xml_doc)

    print(f"Injecting fake Windows notification payload -> [{sender_name}: {message_text}]")
    notifier.show(notification)


if __name__ == "__main__":
    print("--- WINDOWS DISCORD NOTIFICATION SIMULATOR ---")
    ensure_app_registered(APP_ID, "Discord")
    print("Sending fake notification test packet in 2 seconds...")
    print("Make sure your filter script is running in another window!\n")

    time.sleep(2.0)
    # This message contains 'Alex', one of the live watcher's WATCHED_KEYWORDS.
    send_fake_discord_toast("Jacob_Steevs", "Hey Alex, look at this update!")
    print("Notification injected successfully.")
