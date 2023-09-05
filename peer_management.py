class peer_pool:
    def __init__(self) -> None:
        self.pool = {}
    
    def add_peer(self,sid,specifications) -> None:
        self.pool[sid] = {
            'specifications':specifications,
            'availiblity':True
        }
    
    def show_all_peers(self) -> None:
        return self.pool
    
    def mark_peer_busy(self,sid) -> None:
        if sid in self.pool:
            self.pool[sid]['availiblity'] = False
    
    def mark_peer_available(self,sid):
        if sid in self.pool:
            self.pool[sid]['availiblity'] = True
        
    def select_peer_for_service(self,current_sid,min_specs):
        for sid,data in self.pool.items():
            if sid is not current_sid:
                if data['availiblity'] and self.check_specifications(data['specifications'],min_specs):
                    self.mark_peer_busy(sid)
                    return sid
        return None
    
    def check_specifications(self,required_specs,min_specs):
        for key,value in min_specs.items():
            if key not in required_specs or required_specs[key] < value:
                return False
        
        return True