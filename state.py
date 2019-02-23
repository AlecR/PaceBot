class _State_Singleton:
    _instance=  None
    
    def __init__(self):
        self.state = {
            "auto_mode": False,
            "esc_pwm": 320,
            "esc_center": 320,
            "esc_variation": 50,
            "servo_pwm": 320,
            "servo_center": 320,
            "servo_variation": 100,
            "servo_pin": 0,
            "esc_pin": 1
        }

    def servo_pin(self):
        return servo_pin

    def esc_pin(self):
        return esc_pin

    def auto_move(self):
        return atuo_mode

    def esc_center(self):
        return servo_center

    def esc_pwm(self):
        return servo_pwm

    def esc_variation(self):
        return servo_variation

    def servo_center(self):
        return servo_center

    def servo_pwm(self):
        return servo_pwm

    def servo_variation(self):
        return servo_variation
            
    def update_esc_pwm(self, value):
        self.state['esc_pwm'] = value
        
    def update_servo_pwm(self, value):
        self.state['servo_pwm'] = value;
        
    def toggle_auto_mode(self):
        self.state['auto_mode'] = not self.state['auto_mode']

    
def State():
    if _State_Singleton._instance is None:
        _State_Singleton._instance = _State_Singleton()
    return _State_Singleton._instance
    
        
    