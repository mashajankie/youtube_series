import os

def log_op(operation, *args, **kwargs) -> None:
    """Log operations to a file."""
    log_dir = "./logs"
    log_file_path = os.path.join(log_dir, "logs.txt")
    
    # Check if the directory exists, if not, create it
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    details = ', '.join(map(str, args)) + ', '.join(f"{k}={v}" for k, v in kwargs.items())
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{operation}: {details}\n")
