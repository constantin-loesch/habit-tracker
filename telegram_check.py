import os
import requests
from datetime import date

# ─── CONFIG ───────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_ANON_KEY']
BOT_TOKEN    = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_ID      = os.environ['TELEGRAM_CHAT_ID']

# Deine GitHub Pages URL (nach dem ersten Push anpassen)
TRACKER_URL  = 'https://constantin-loesch.github.io/habit-tracker'

today = date.today().isoformat()

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

def get_habits():
    r = requests.get(f'{SUPABASE_URL}/rest/v1/habits?is_active=eq.true', headers=HEADERS)
    return r.json()

def get_todays_logs():
    r = requests.get(
        f'{SUPABASE_URL}/rest/v1/habit_logs?date=eq.{today}&completed=eq.true',
        headers=HEADERS
    )
    return r.json()

def send_telegram(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    r = requests.post(url, json=payload)
    print(f'Telegram: {r.status_code} - {r.text}')

def main():
    habits = get_habits()
    if not habits:
        print('Keine Habits angelegt – kein Reminder nötig.')
        return

    logs = get_todays_logs()
    logged_ids = {l['habit_id'] for l in logs}

    not_done = [h for h in habits if h['id'] not in logged_ids]
    total = len(habits)
    done_count = total - len(not_done)

    if not not_done:
        print(f'Alles erledigt ({done_count}/{total}) – kein Reminder.')
        return

    # Stunde für kontextbasierte Nachricht
    from datetime import datetime
    hour = datetime.utcnow().hour + 1  # UTC+1

    if hour <= 9:
        greeting = 'Guten Morgen! ☀️'
        motivate = 'Starte stark in den Tag!'
    elif hour <= 14:
        greeting = 'Hey! 🌤'
        motivate = 'Kurze Mittagspause – perfekt für deine Habits.'
    else:
        greeting = 'Guten Abend! 🌙'
        motivate = 'Der Tag ist fast vorbei – jetzt noch schnell eintragen!'

    remaining = '\n'.join([f'  • {h.get("icon","") + " " if h.get("icon") else ""}{h["name"]}' for h in not_done])

    message = (
        f'{greeting}\n\n'
        f'<b>{done_count}/{total} Habits</b> heute erledigt.\n\n'
        f'Noch offen:\n{remaining}\n\n'
        f'{motivate}\n\n'
        f'👉 <a href="{TRACKER_URL}">Jetzt eintragen</a>'
    )

    send_telegram(message)
    print(f'Reminder gesendet – {len(not_done)} Habits noch offen.')

if __name__ == '__main__':
    main()