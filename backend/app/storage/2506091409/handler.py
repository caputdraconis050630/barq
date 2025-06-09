def main(event):
    name = event.get('name', 'World')
    return f'Hello {name}!'