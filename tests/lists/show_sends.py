class MyListView(ListView):
    def start(self, head, request):
        return ['first chunk', 'second \"chunk\"'], {'headers':{'Content-Type' : 'text/plain'}}
    def list_end(self):
        return 'tail'
