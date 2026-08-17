#!/usr/bin/env python3
"""
Fake Discord notification injector for Ubuntu / Linux desktops.

Sends a single desktop notification over D-Bus that looks like it came from
Discord, so you can confirm live_filter.py picks it up. This is the Linux
counterpart of the Windows toast injector: it calls the same
`org.freedesktop.Notifications.Notify` method that real apps use, spoofing the
`app_name` field to "discord" so the filter's app match succeeds.
"""

import time

from jeepney import DBusAddress, new_method_call
from jeepney.io.blocking import open_dbus_connection

NOTIFICATIONS = DBusAddress(
    "/org/freedesktop/Notifications",
    bus_name="org.freedesktop.Notifications",
    interface="org.freedesktop.Notifications",
)


def send_fake_discord_notification(sender_name, message_text):
    summary = "Discord Test Server (#general)"
    body = f"{sender_name}: {message_text}"

    # Notify(app_name, replaces_id, app_icon, summary, body, actions, hints, timeout)
    request = new_method_call(
        NOTIFICATIONS,
        "Notify",
        "susssasa{sv}i",
        (
            "discord",  # app_name -- must match the filter's TARGET_APP_NAME
            0,          # replaces_id (0 = new notification)
            "",         # app_icon
            summary,
            body,
            [],         # actions
            {},         # hints
            5000,       # expire_timeout in ms
        ),
    )

    print(f"Injecting fake Discord notification payload -> [{sender_name}: {message_text}]")
    conn = open_dbus_connection(bus="SESSION")
    try:
        reply = conn.send_and_get_reply(request)
    finally:
        conn.close()
    return reply.body[0]  # the assigned notification id


if __name__ == "__main__":
    print("--- LINUX DISCORD NOTIFICATION SIMULATOR ---")
    print("Sending fake notification test packet in 2 seconds...")
    print("Make sure your filter script is running in another terminal!\n")

    time.sleep(2.0)
    # This message contains 'Alex', one of the live watcher's WATCHED_KEYWORDS.
    send_fake_discord_notification("Jacob_Steevs", "Hey Alex, look at this update!")
    print("Notification injected successfully.")
