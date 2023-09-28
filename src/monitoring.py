from datetime import datetime

class Monitoring:
    def __init__(self):
        self.requests = {}
        self.picked_models = {}
    
    def request_called(self, name: str, status: bool):
        if not name in self.requests:
            self.requests[name] = []

        self.requests[name].append([status, datetime.now()])
    
    def picked_model(self, model_name):
        if not model_name in self.picked_models:
            self.picked_models[model_name] = 0
        self.picked_models[model_name] += 1
    
    def get_total_requests_info(self):
        return sum([len(req) for req in self.requests.values()]), sum([len([r for r in req if r[0]]) for req in self.requests.values()])

    def get_timeline_date(self):
        return self.requests
    
    def get_picked_models(self):
        return self.picked_models