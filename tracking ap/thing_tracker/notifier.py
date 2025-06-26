from pydbus import SessionBus

bus = SessionBus()
notify = bus.get('org.freedesktop.Notifications')

def send_notification(summary, body, timeout=5000):
    # timeout in milliseconds
    notify.Notify(
        "ThingTracker",  # app name
        0,               # replaces_id 
        "",              # app icon
        summary,
        body,
        [],              # actions
        {},              # hints
        timeout
    )
