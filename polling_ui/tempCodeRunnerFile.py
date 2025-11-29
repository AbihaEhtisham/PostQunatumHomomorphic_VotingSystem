
def voter_validation():
    if request.method == 'POST':
        name = request.form.get('name').strip()