import asyncio
import winsound
from winsdk.windows.ui.notifications.management import UserNotificationListener
from winsdk.windows.ui.notifications import NotificationKinds

# Configuration: Add the explicit display names or text phrases you want to monitor
WATCHED_KEYWORDS = ["Alex", "JohnDoe", "Mod_Sarah"]

async def listen_to_windows_notifications():
    print("--- LIVE OS-LEVEL MIDDLEWARE FILTER STARTED ---")
    print("Polled interception framework active... Press Ctrl+C to terminate.")
    
    # Initialize a system notification loop listener
    listener = UserNotificationListener.get_current()
    
    # Verify local user execution clearance policies
    access_status = await listener.request_access_async()
    if access_status != 1:  # Status code 1 indicates system validation 'Allowed'
        print("[CRITICAL] Access Denied. Turn on Notification Access in Windows Settings.")
        return

    # In-memory storage cache array tracking historical event logs
    processed_ids = set()

    while True:
        # Extract toast layout formats present in the active notification buffer
        notifications = await listener.get_notifications_async(NotificationKinds.TOAST)
        
        for notif in notifications:
            if notif.id in processed_ids:
                continue
                
            try:
                # Capture metadata labels marking application origination footprints
                app_name = notif.app_info.display_info.display_name
                
                # Check for standard Discord client application profiles
                if app_name == "Discord":
                    binding = notif.notification.visual.get_binding("ToastGeneric")
                    if binding:
                        text_elements = binding.get_text_elements()
                        
                        if len(text_elements) >= 2:
                            title = text_elements[0].text
                            body = text_elements[1].text
                            
                            # Execute pattern-matching loops looking for targeted keywords
                            if any(keyword.lower() in body.lower() for keyword in WATCHED_KEYWORDS):
                                print(f"\n[ALERT MATCH DETECTED] {title} -> {body}")
                                
                                # Fire an unthrottled hardware audio indicator beep
                                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                                
            except Exception:
                pass  # Suppress internal UI buffer mapping exceptions
                
            processed_ids.add(notif.id)
            
        # Clear out historical memory array allocations when sizing parameters hit margins
        if len(processed_ids) > 1000:
            processed_ids.clear()
            
        # Run event loops at microsecond polling intervals
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    try:
        asyncio.run(listen_to_windows_notifications())
    except KeyboardInterrupt:
        print("\nMiddleware service shut down gracefully.")
