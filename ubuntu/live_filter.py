#!/usr/bin/env python3
"""
Live Discord notification filter for Ubuntu / Linux desktops.

On Linux there is no WinRT UserNotificationListener. Instead, every app that
raises a desktop notification does so by calling the `Notify` method on the
`org.freedesktop.Notifications` service over the D-Bus *session* bus. We register
this process as a passive bus **monitor** (the exact mechanism the `dbus-monitor`
command-line tool uses) and watch those calls stream past -- the Linux
equivalent of the Windows notification listener.

Requires a running notification daemon, which is standard on GNOME, KDE Plasma,
XFCE, etc. Discord's Linux client posts through this same interface.
"""

import subprocess
import sys

from jeepney import DBusAddress, HeaderFields, MessageType, new_method_call
from jeepney.io.blocking import open_dbus_connection

# Configuration: display names / text phrases to watch for in Discord messages.
WATCHED_KEYWORDS = ["Alex", "JohnDoe", "Mod_Sarah"]

# The application name Discord uses when it posts a notification.
# Matched case-insensitively, so "discord" and "Discord" both count.
TARGET_APP_NAME = "discord"

NOTIFY_INTERFACE = "org.freedesktop.Notifications"

# Sound players tried in order for an audible alert; first one present wins.
SOUND_PLAYERS = [
    ["canberra-gtk-play", "--id", "message"],
    ["paplay", "/usr/share/sounds/freedesktop/stereo/message.oga"],
]


def alert(summary, body):
    print(f"\n[ALERT MATCH DETECTED] {summary} -> {body}")

    # Terminal bell first -- always available, costs nothing.
    sys.stdout.write("\a")
    sys.stdout.flush()

    # Then try a real desktop sound, silently skipping any player that is absent.
    for player in SOUND_PLAYERS:
        try:
            subprocess.Popen(
                player, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            break
        except (FileNotFoundError, OSError):
            continue


def become_notification_monitor(conn):
    """Ask the bus daemon to copy every Discord `Notify` call to us."""
    monitoring = DBusAddress(
        "/org/freedesktop/DBus",
        bus_name="org.freedesktop.DBus",
        interface="org.freedesktop.DBus.Monitoring",
    )
    match_rule = f"interface='{NOTIFY_INTERFACE}',member='Notify'"
    # BecomeMonitor(match_rules: as, flags: u); flags must be 0.
    request = new_method_call(monitoring, "BecomeMonitor", "asu", ([match_rule], 0))
    conn.send_and_get_reply(request)


def main():
    print("--- LIVE OS-LEVEL NOTIFICATION FILTER STARTED (Linux / D-Bus) ---")
    print("Monitoring the session bus for Discord notifications... Press Ctrl+C to stop.")

    try:
        conn = open_dbus_connection(bus="SESSION")
    except Exception as exc:
        print(f"[CRITICAL] Could not connect to the D-Bus session bus: {exc}")
        print("Run this inside a graphical desktop session (DBUS_SESSION_BUS_ADDRESS must be set).")
        return

    try:
        become_notification_monitor(conn)
    except Exception as exc:
        print(f"[CRITICAL] Could not become a bus monitor: {exc}")
        conn.close()
        return

    while True:
        msg = conn.receive()

        # We only care about the app -> daemon `Notify` method calls.
        if msg.header.message_type != MessageType.method_call:
            continue
        fields = msg.header.fields
        if fields.get(HeaderFields.interface) != NOTIFY_INTERFACE:
            continue
        if fields.get(HeaderFields.member) != "Notify":
            continue

        try:
            # Notify(app_name, replaces_id, app_icon, summary, body, actions, hints, timeout)
            app_name = msg.body[0]
            summary = msg.body[3]
            body = msg.body[4]
        except (IndexError, TypeError):
            continue  # Malformed / unexpected payload -- skip it.

        if str(app_name).lower() != TARGET_APP_NAME:
            continue

        if any(keyword.lower() in body.lower() for keyword in WATCHED_KEYWORDS):
            alert(summary, body)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nMonitor service shut down gracefully.")
