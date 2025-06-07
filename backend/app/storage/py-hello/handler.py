def main(event):
    name = event.get('name', 'world')
    return {'msg': f'Hello {name} from Python!'}