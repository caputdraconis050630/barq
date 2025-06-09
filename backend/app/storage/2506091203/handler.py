def handler(event):
    name = event.get('name', 'Guntak')
    return f"Hello {name}!"