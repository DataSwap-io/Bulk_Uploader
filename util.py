from datetime import datetime, timedelta

def get_target_timestamp(iteration: int):
    target_hours = [12, 14, 17]
    now = datetime.now()
    today = now.date()
    
    # Figure out which day and hour based on iteration
    day_offset = iteration // len(target_hours)
    hour_index = iteration % len(target_hours)
    
    target_time = datetime.combine(today + timedelta(days=day_offset), datetime.min.time()) + timedelta(hours=target_hours[hour_index])
    
    return int(target_time.timestamp())

for i in range(7):
    ts = get_target_timestamp(i)
    print(f"Iteration {i}: {datetime.fromtimestamp(ts)} (Unix: {ts})")