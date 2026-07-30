def enqueue(hold_music_url, queue_name):
    
    # Puts the CURRENT caller on hold, playing hold_music_url, inside a named queue when no match is available yet .

    return f'<Enqueue holdMusic="{hold_music_url}" name="{queue_name}"/>'


def dequeue(phone_number, queue_name):
    
    # Pulls a specific phone number OUT of a named hold queue and bridges them
    # live into the CURRENT call when a match IS found.
    
    return f'<Dequeue phoneNumber="{phone_number}" name="{queue_name}"/>'


def queue_name_for(intent, language):
    
    #  Builds a consistent queue name from intent + language, so callers are only
    #  ever held alongside people they could actually be matched with.
    
    return f"{intent}_{language}"