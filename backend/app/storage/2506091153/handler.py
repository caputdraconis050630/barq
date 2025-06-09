def main(event):
    name = event.get('name', 'Guntak')
    return f"Hello {name}!"