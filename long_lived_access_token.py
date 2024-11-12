import requests

def get_long_lived_token(app_id, app_secret, short_lived_token):
    url = 'https://graph.facebook.com/v17.0/oauth/access_token'
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': short_lived_token
    }
    response = requests.get(url, params=params)
    return response.json()

app_id = '241432711870469'
app_secret = 'a1aa25326d69a1f64f1b2402d65f6a25'
short_lived_token = 'EAADblO8HOAUBO8ucC7HcuGSZAL24tJG315WlQHqZCCwSwz3KaZBZB8XQyRA607JEwI7ZCFeOe66uTEoQlFuBZAgrvsCqYzlH4E68jLeIW4H2eYSAOrgvsc22Jvjs3KcMxDVBwbAcLZCgptu1H2EYF9SZCFcZBDHUqRAkZAgo8SCDR0kxYs9mTM7ktxwAZDZD'

long_lived_token = get_long_lived_token(app_id, app_secret, short_lived_token)
print('Long-Lived Access Token:', long_lived_token)
