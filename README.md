# Discord Filter & Notifier

Watch your OS-level desktop notifications, and beep when a **Discord** message
contains one of your watched keywords (e.g. specific people you don't want to
miss). Because the notification APIs are completely different per OS, the project
is split into two self-contained versions:

```
.
├── windows/      # Windows 10/11 version  (WinRT UserNotificationListener + toasts)
│   ├── live_filter.py
│   ├── fake_notifier.py
│   └── requirements.txt
├── ubuntu/       # Ubuntu / Linux version (D-Bus org.freedesktop.Notifications)
│   ├── live_filter.py
│   ├── fake_notifier.py
│   └── requirements.txt
└── README.md
```

Each folder has the same two tools:

- **`live_filter.py`** — the watcher. Listens to the OS notification stream,
  keeps only Discord notifications, and alerts (beep) when the message body
  contains a watched keyword. Configure the list at the top of the file:
  ```python
  WATCHED_KEYWORDS = ["Alex", "JohnDoe", "Mod_Sarah"]
  ```
- **`fake_notifier.py`** — a test tool that injects one fake, Discord-looking
  notification so you can confirm the filter reacts without waiting for a real
  message.

Pick the folder for your OS; the two versions do not share code or dependencies.

---

## Windows (10 / 11)

Uses the WinRT `UserNotificationListener` API via the maintained **PyWinRT**
packages (the old `winsdk` package is abandoned and won't build on Python 3.13+).
Prebuilt wheels mean **no Visual Studio / C++ build tools are required**.
Supported on CPython 3.9–3.14.

```powershell
cd windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Before running:** enable notification access — Windows Settings →
Privacy & security → Notifications → "Let apps access your notifications".
Without it the listener is denied and exits.

Run the watcher, then (in a second terminal) fire a test notification:

```powershell
python live_filter.py
# ... in another terminal:
python fake_notifier.py
```

> **Note on the Windows test tool:** Windows refuses to display a toast posted
> under an unregistered AppUserModelID (it raises "Element not found"). So
> `fake_notifier.py` first registers a lightweight AUMID named `Discord` under
> `HKCU\Software\Classes\AppUserModelId\Discord` (per-user, no admin needed) so
> the test toast actually appears and is attributed to "Discord". Remove it any
> time by deleting that registry key. This does not affect the real Discord app,
> which uses a different AUMID.

---

## Ubuntu / Linux

There is no `UserNotificationListener` on Linux. Instead, every app posts
notifications by calling `Notify` on the `org.freedesktop.Notifications` service
over the **D-Bus session bus**. `live_filter.py` registers as a passive bus
**monitor** (the same mechanism as the `dbus-monitor` tool) and watches those
calls go by; `fake_notifier.py` calls the same `Notify` method, spoofing the app
name to `discord`.

Uses **jeepney**, a pure-Python D-Bus client with zero other dependencies — no
system `libdbus`, PyGObject, or compilers needed.

```bash
cd ubuntu
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Requirements:** a running desktop session with a notification daemon
(standard on GNOME, KDE Plasma, XFCE, dunst, mako, …) and a session bus
(`DBUS_SESSION_BUS_ADDRESS` set — automatic inside any graphical login).

Run the watcher, then (in a second terminal) fire a test notification:

```bash
python3 live_filter.py
# ... in another terminal:
python3 fake_notifier.py
```

For an audible alert beyond the terminal bell, install a sound player such as
`libcanberra-gtk-module` (provides `canberra-gtk-play`) or `pulseaudio-utils`
(provides `paplay`); the filter uses whichever it finds and falls back to the
terminal bell.

> **Note on the app name:** the filter matches Discord's notification `app_name`
> case-insensitively against `discord`. If your Discord build advertises a
> different name, adjust `TARGET_APP_NAME` at the top of `live_filter.py`.
